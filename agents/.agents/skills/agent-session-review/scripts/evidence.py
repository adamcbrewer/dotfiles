"""Index evidence references and reported results, without replaying commands."""

import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse


MEDIA = r"(?:png|jpe?g|webp|gif|bmp|svg|mp4|webm|mov|mkv)"
MEDIA_PATH = re.compile(r"(?:file://|https?://|/|~/|\./)[^\s<>\"'\]\)]+\." + MEDIA + r"(?:\?[^\s<>\"'\]\)]*)?", re.I)
MARKDOWN_MEDIA = re.compile(r"\]\(<?([^\n]+?\." + MEDIA + r")>?\)", re.I)
PR_URL = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/pull/\d+\b")
RESULT_LINE = re.compile(
    r"(?:test result: (?:ok|FAILED)|\b\d+ (?:passed|failed|skipped)\b|^Ran \d+ tests?\b|"
    r"^# (?:pass|fail|tests) \d+|^FAIL(?:ED)?\b|^OK$|^Process exited with code \d+)", re.I)


def media_reference(value, directory):
    if value.startswith("data:"):
        return {"availability": "embedded_not_extracted", "media_type": value[5:].split(";", 1)[0]}
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        return {"url": value, "availability": "remote_not_fetched"}
    if parsed.scheme not in ("", "file") or parsed.netloc:
        return {"reference": value, "availability": "unsupported_reference"}
    path = Path(unquote(parsed.path)).expanduser()
    if not path.is_absolute():
        path = Path(directory) / path
    path = path.absolute()
    try:
        stat = path.stat()
        if path.is_file():
            return {"path": str(path), "availability": "local_file", "size_bytes": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns}
    except OSError:
        pass
    return {"path": str(path), "availability": "missing_or_unreadable"}


def scan(text, directory, results=False):
    original = text
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False)
    media = list(dict.fromkeys([*MARKDOWN_MEDIA.findall(text), *MEDIA_PATH.findall(text)]))
    evidence = {}
    if media:
        evidence["media"] = [media_reference(value, directory) for value in media]
    prs = list(dict.fromkeys(PR_URL.findall(text)))
    if prs:
        evidence["pull_requests"] = [{"url": url, "verification": "link_only"} for url in prs]
    if results:
        lines = [line.strip() for value in result_texts(original) for line in value.splitlines()
                 if RESULT_LINE.search(line.strip())]
        if lines:
            evidence["result_lines"] = [line[:2000] for line in lines[:20]]
            evidence["result_lines_omitted"] = max(0, len(lines) - 20)
        facts = structured_results(text)
        if facts:
            evidence["reported_results"] = facts
    return evidence


def result_texts(value, depth=0):
    if depth > 5:
        return
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except ValueError:
            decoded = None
        if isinstance(decoded, (dict, list)):
            yield from result_texts(decoded, depth + 1)
        else:
            yield value
    elif isinstance(value, list):
        for item in value:
            yield from result_texts(item, depth + 1)
    elif isinstance(value, dict):
        for key in ("content", "structuredContent", "output", "text", "value"):
            if key in value:
                yield from result_texts(value[key], depth + 1)


def bounded_items(values, budget):
    kept = []
    for value in values:
        size = len(json.dumps(value, ensure_ascii=False)) + 2
        if size <= budget:
            kept.append(value)
            budget -= size
    return kept, len(values) - len(kept)


def bound_entries(entries):
    for entry in entries:
        evidence = entry.get("evidence", {})
        for fact in evidence.get("reported_results", []):
            if "checks" in fact:
                fact["checks"], omitted = bounded_items(fact["checks"], 1000)
                if omitted:
                    fact["checks_omitted"] = fact.get("checks_omitted", 0) + omitted
        budget = 3000
        for key, values in list(evidence.items()):
            if not isinstance(values, list):
                continue
            evidence[key], omitted = bounded_items(values, budget)
            budget -= len(json.dumps(evidence[key], ensure_ascii=False))
            if omitted:
                evidence[key + "_omitted"] = evidence.get(key + "_omitted", 0) + omitted
    return entries


def structured_results(value, depth=0):
    if depth > 5:
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return []
    if isinstance(value, list):
        return [fact for item in value for fact in structured_results(item, depth + 1)][:20]
    if not isinstance(value, dict):
        return []
    facts = []
    for key in ("exit_code", "exitCode", "exit"):
        if isinstance(value.get(key), int) and not isinstance(value[key], bool):
            facts.append({"kind": "process_exit", "exit_code": value[key]})
    if isinstance(value.get("isError"), bool):
        facts.append({"kind": "tool_status", "is_error": value["isError"]})
    url = value.get("url") or value.get("html_url")
    if isinstance(url, str) and PR_URL.fullmatch(url):
        state = {k: value[k] for k in ("state", "merged", "mergedAt", "merged_at", "headRefOid") if k in value}
        head = value.get("head")
        if isinstance(head, dict) and head.get("sha"):
            state["head_sha"] = head["sha"]
        checks = value.get("statusCheckRollup")
        if isinstance(checks, list):
            state["checks"] = [{k: c[k] for k in ("name", "context", "status", "conclusion", "state") if k in c}
                               for c in checks if isinstance(c, dict)]
        if state:
            facts.append({"kind": "pull_request_state", "url": url, **state})
    for key in ("content", "structuredContent", "output", "text", "value"):
        if key in value:
            facts.extend(structured_results(value[key], depth + 1))
    return facts[:20]


def attach(entry, value, directory, results=False):
    evidence = scan(value, directory, results)
    if evidence:
        existing = entry.setdefault("evidence", {})
        for key, value in evidence.items():
            existing[key] = existing.get(key, []) + value if isinstance(value, list) else value
    return entry
