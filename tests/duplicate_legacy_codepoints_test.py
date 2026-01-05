#!/usr/bin/env python3
"""
Demonstrates that duplicate glyph keys silently overwrite the first entry.

The fixture intentionally repeats the "glyphDuplicate" key. Standard json.load
keeps only the final occurrence without emitting a warning, so the first mapping
is lost and the surviving entry uses the last codepoint.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from json_utils import DuplicateKeyError, load_json_strict  # type: ignore  # noqa: E402


def main() -> int:
    fixture = Path(__file__).resolve().parent / "data" / "legacy_duplicate_glyph.json"
    try:
        with fixture.open("r", encoding="utf-8") as handle:
            load_json_strict(handle, location=str(fixture))
    except DuplicateKeyError as exc:
        print(f"PASS: parser rejected duplicate glyph key ({exc}).")
        return 0

    print(
        "FAIL: parser accepted duplicate glyph key and overwrote the earlier mapping.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
