"""Render cron helper: POST /update-data on the same deployed service."""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    base = os.environ.get("RENDER_EXTERNAL_URL", "").strip().rstrip("/")
    if not base:
        print("RENDER_EXTERNAL_URL is not set", file=sys.stderr)
        return 2

    url = f"{base}/update-data"
    req = urllib.request.Request(url, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(body)
        return 0
    except urllib.error.HTTPError as exc:
        print(f"HTTPError {exc.code}: {exc.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
