#!/usr/bin/env python3
"""Read a minimal Codex usage snapshot through the official Codex CLI."""

import json
import queue
import shutil
import subprocess
import threading
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path


def clean_text(value, fallback=""):
    text = "" if value is None else str(value)
    text = "".join(character for character in text if character >= " " and character != "\x7f")
    return text[:120] or fallback


def percentage(value):
    try:
        return max(0, min(100, int(float(value) + 0.5)))
    except (TypeError, ValueError):
        return None


def credit_balance(value):
    text = clean_text(value)
    if not text:
        return ""
    try:
        amount = Decimal(text)
        return f"{amount:.2f}" if amount.is_finite() else text
    except InvalidOperation:
        return text


def plan_label(value):
    plan = clean_text(value).lower()
    labels = {
        "prolite": "Pro Lite",
        "self_serve_business_prolite": "Business Pro Lite",
        "self_serve_business_usage_based": "Business",
        "enterprise_cbp_automation": "Enterprise",
        "enterprise_cbp_usage_based": "Enterprise",
    }
    return labels.get(plan, plan.replace("_", " ").title())


def window_label(minutes):
    if minutes == 300:
        return "5 hour"
    if minutes == 10_080:
        return "Weekly"
    if minutes and minutes % 1_440 == 0:
        return f"{minutes // 1_440} day"
    if minutes and minutes % 60 == 0:
        return f"{minutes // 60} hour"
    return "Usage"


def normalize_window(raw):
    if not isinstance(raw, dict):
        return None
    used = percentage(raw.get("usedPercent"))
    if used is None:
        return None
    try:
        minutes = int(raw.get("windowDurationMins") or 0)
    except (TypeError, ValueError):
        minutes = 0
    try:
        resets_at = int(raw.get("resetsAt") or 0)
    except (TypeError, ValueError):
        resets_at = 0
    return {
        "label": window_label(minutes),
        "used": used,
        "remaining": 100 - used,
        "duration_minutes": max(0, minutes),
        "resets_at": max(0, resets_at),
    }


def normalize_bucket(bucket_id, raw):
    if not isinstance(raw, dict):
        return None
    windows = [
        window
        for window in (normalize_window(raw.get("primary")), normalize_window(raw.get("secondary")))
        if window
    ]
    windows.sort(key=lambda window: window["duration_minutes"] or 10**12)
    credits = raw.get("credits") if isinstance(raw.get("credits"), dict) else {}
    individual = raw.get("individualLimit") if isinstance(raw.get("individualLimit"), dict) else {}
    name = clean_text(raw.get("limitName"))
    if not name:
        name = "Codex" if bucket_id == "codex" else clean_text(bucket_id.replace("_", " ").title(), "Usage")
    return {
        "id": clean_text(bucket_id, "usage"),
        "name": name,
        "windows": windows,
        "credits": {
            "balance": credit_balance(credits.get("balance")),
            "has_credits": credits.get("hasCredits") is True,
            "unlimited": credits.get("unlimited") is True,
        },
        "spend": {
            "used": clean_text(individual.get("used")),
            "limit": clean_text(individual.get("limit")),
            "remaining": percentage(individual.get("remainingPercent")),
        },
        "reached": raw.get("rateLimitReachedType") is not None or raw.get("spendControlReached") is True,
        "plan": clean_text(raw.get("planType")),
    }


def normalize(result):
    if not isinstance(result, dict):
        raise RuntimeError("Codex CLI returned invalid usage data")
    raw_buckets = result.get("rateLimitsByLimitId")
    if isinstance(raw_buckets, dict) and raw_buckets:
        bucket_items = raw_buckets.items()
    else:
        bucket_items = [("codex", result.get("rateLimits"))]

    buckets = [
        bucket
        for bucket in (normalize_bucket(str(bucket_id), raw) for bucket_id, raw in bucket_items)
        if bucket and (bucket["windows"] or bucket["credits"]["has_credits"] or bucket["credits"]["unlimited"])
    ]
    buckets.sort(key=lambda bucket: (bucket["id"] != "codex", bucket["name"].lower()))

    headline = next(
        (
            window
            for bucket in buckets
            for window in bucket["windows"]
            if bucket["id"] == "codex" and window["duration_minutes"] == 300
        ),
        next((window for bucket in buckets for window in bucket["windows"]), None),
    )
    plans = [bucket["plan"] for bucket in buckets if bucket["plan"]]
    reset_credits = result.get("rateLimitResetCredits")
    try:
        reset_credit_count = int(reset_credits.get("availableCount", 0)) if isinstance(reset_credits, dict) else 0
    except (TypeError, ValueError):
        reset_credit_count = 0
    reset_credit_expiries = []
    if isinstance(reset_credits, dict) and isinstance(reset_credits.get("credits"), list):
        for credit in reset_credits["credits"]:
            if not isinstance(credit, dict) or credit.get("status") != "available":
                continue
            try:
                expires_at = int(credit.get("expiresAt") or 0)
            except (TypeError, ValueError):
                expires_at = 0
            if expires_at > 0:
                reset_credit_expiries.append(expires_at)

    return {
        "available": bool(buckets),
        "plan": plan_label(plans[0]) if plans else "",
        "headline": headline,
        "buckets": buckets,
        "reset_credits": max(0, reset_credit_count),
        "reset_credits_expires_at": min(reset_credit_expiries, default=0),
        "updated_at": int(time.time()),
    }


def request_rate_limits(timeout=12):
    codex = shutil.which("codex")
    if not codex:
        raise RuntimeError("Codex CLI not found")

    process = subprocess.Popen(
        [codex, "app-server", "--stdio"],
        cwd=Path.home(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    messages = queue.Queue()

    def read_messages():
        try:
            for line in process.stdout:
                try:
                    messages.put(json.loads(line))
                except json.JSONDecodeError:
                    continue
        finally:
            messages.put(None)

    threading.Thread(target=read_messages, daemon=True).start()

    def send(message):
        process.stdin.write(json.dumps(message) + "\n")
        process.stdin.flush()

    def receive(request_id):
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("Codex CLI timed out")
            try:
                message = messages.get(timeout=remaining)
            except queue.Empty as error:
                raise RuntimeError("Codex CLI timed out") from error
            if message is None:
                raise RuntimeError("Codex CLI stopped unexpectedly")
            if not isinstance(message, dict):
                continue
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise RuntimeError("Codex CLI could not read usage")
            return message.get("result") or {}

    try:
        send({"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "adam-codex-usage", "version": "1"}}})
        receive(1)
        send({"method": "initialized"})
        send({"id": 2, "method": "account/rateLimits/read"})
        return receive(2)
    finally:
        try:
            process.stdin.close()
        except (AttributeError, OSError):
            pass
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main():
    try:
        print(json.dumps(normalize(request_rate_limits()), separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(json.dumps({"available": False, "error": clean_text(error, "Usage unavailable")}, separators=(",", ":")))


if __name__ == "__main__":
    main()
