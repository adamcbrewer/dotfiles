#!/usr/bin/env python3

import json
import os
import re
import subprocess
import sys


def run(*args):
    env = os.environ.copy()
    env["LC_ALL"] = "C"
    return subprocess.run(
        ["/usr/bin/nmcli", *args],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )


def service_password(uuid):
    result = subprocess.run(
        ["/usr/bin/secret-tool", "lookup", "application", "adam.nordvpn", "uuid", uuid],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.rstrip("\n") if result.returncode == 0 else ""


def prompt_credentials(uuid):
    result = subprocess.run(
        [
            "/usr/bin/zenity",
            "--forms",
            "--title=NordVPN service credentials",
            "--text=Use the manual-setup credentials from your Nord Account.",
            "--add-entry=Service username",
            "--add-password=Service password",
            "--separator=\n",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "", ""

    fields = result.stdout.rstrip("\n").split("\n", 1)
    if len(fields) != 2 or not all(fields):
        return "", ""

    username, password = fields
    saved = subprocess.run(
        [
            "/usr/bin/secret-tool",
            "store",
            "--label=NordVPN OpenVPN password",
            "application",
            "adam.nordvpn",
            "uuid",
            uuid,
        ],
        check=False,
        input=password,
        capture_output=True,
        text=True,
    )
    if saved.returncode != 0:
        return "", ""

    configured = run("connection", "modify", "uuid", uuid, "vpn.user-name", username)
    return (username, password) if configured.returncode == 0 else ("", "")


def connect(uuid):
    password = service_password(uuid)
    if not password:
        _username, password = prompt_credentials(uuid)
    if not password:
        return "NordVPN service credentials were not saved"

    env = os.environ.copy()
    env["LC_ALL"] = "C"
    result = subprocess.run(
        ["/usr/bin/nmcli", "connection", "up", "uuid", uuid, "passwd-file", "/dev/stdin"],
        check=False,
        input=f"vpn.secrets.password:{password}\n",
        capture_output=True,
        env=env,
        text=True,
    )
    return "" if result.returncode == 0 else result.stderr.strip() or result.stdout.strip() or "VPN connection failed"


def profile_status(uuid, error=""):
    profile = run("-g", "connection.id", "connection", "show", "uuid", uuid)
    if profile.returncode != 0:
        return {
            "available": False,
            "connected": False,
            "error": profile.stderr.strip() or "VPN profile not found",
            "name": "NordVPN",
        }

    active = run("-t", "-f", "UUID", "connection", "show", "--active")
    return {
        "available": True,
        "connected": uuid in active.stdout.splitlines(),
        "error": error,
        "name": profile.stdout.strip() or "NordVPN",
    }


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in {"status", "toggle"}:
        raise SystemExit("usage: vpn.py <status|toggle> <connection-uuid>")

    action, uuid = sys.argv[1:]
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", uuid):
        print(json.dumps({"available": False, "connected": False, "error": "Configure a valid VPN UUID", "name": "NordVPN"}))
        return

    status = profile_status(uuid)
    if action == "toggle" and status["available"]:
        if status["connected"]:
            result = run("connection", "down", "uuid", uuid)
            error = "" if result.returncode == 0 else result.stderr.strip() or result.stdout.strip() or "VPN disconnect failed"
        else:
            error = connect(uuid)
        status = profile_status(uuid, error)

    print(json.dumps(status))


if __name__ == "__main__":
    main()
