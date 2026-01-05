#!/usr/bin/env python3
"""Ensure duplicate legacy codepoints within a single entry are rejected."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    validator = root / "tools" / "validate_legacy_mappings.py"
    fixture = Path(__file__).resolve().parent / "data" / "legacy_duplicate_codepoints_array.json"

    result = subprocess.run(
        [sys.executable, str(validator), str(fixture)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("PASS: validator rejected duplicate legacy codepoints in a single entry.")
        return 0

    print(
        "FAIL: validator accepted duplicate legacy codepoints within one entry.",
        file=sys.stderr,
    )
    if result.stdout:
        print("stdout:\n" + result.stdout, file=sys.stderr)
    if result.stderr:
        print("stderr:\n" + result.stderr, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
