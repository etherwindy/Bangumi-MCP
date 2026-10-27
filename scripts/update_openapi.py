#!/usr/bin/env python3
"""Refresh the bundled Bangumi OpenAPI document.

Usage:
    uv run python scripts/update_openapi.py          # download and save
    uv run python scripts/update_openapi.py --check  # exit 1 if stale

The server only uses the document as a reference for the API revision it was
written against; the runtime schemas come from ``bangumi_mcp/models.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.request import urlopen

SOURCE = "https://bangumi.github.io/api/dist.json"
TARGET = Path(__file__).resolve().parent.parent / "bangumi_mcp" / "dist.json"


def load_remote(timeout: float = 30.0) -> dict:
    with urlopen(SOURCE, timeout=timeout) as response:  # noqa: S310 - fixed URL
        return json.load(response)


def current_version(path: Path = TARGET) -> str:
    return json.loads(path.read_text(encoding="utf-8"))["info"]["version"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="only report whether the bundled schema is stale",
    )
    args = parser.parse_args()

    remote = load_remote()
    remote_version = remote["info"]["version"]
    local_version = current_version()

    if args.check:
        if remote_version != local_version:
            print(
                f"Bundled Bangumi OpenAPI is stale: {local_version} -> {remote_version}. "
                "Run scripts/update_openapi.py.",
                file=sys.stderr,
            )
            return 1
        print(f"Bundled Bangumi OpenAPI is current ({local_version}).")
        return 0

    TARGET.write_text(
        json.dumps(remote, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {TARGET} ({local_version} -> {remote_version}).")
    print("Review the diff against bangumi_mcp/models.py and the client.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
