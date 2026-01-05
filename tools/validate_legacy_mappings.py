#!/usr/bin/env python3

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set

from json_utils import DuplicateKeyError, load_json_strict


CODEPOINT_RE = re.compile(r"^U\+[0-9A-Fa-f]{4,6}$")
LEGACY_CODEPOINT_RE = re.compile(r"^(0x[0-9A-Fa-f]+|[0-9]+)$")
OFFSET_RE = re.compile(r"^-?[0-9]+$")
ALLOWED_KEYS = {
    "legacyCodepoints",
    "codepoint",
    "description",
    "nameIsMakeMusic",
    "smuflFontName",
    "xOffset",
    "yOffset",
    "alternate",
    "notes",
}


class ValidationError(Exception):
    pass


def _err(path: Path, glyph: str, entry_idx: int, message: str) -> ValidationError:
    prefix = f"{path}: glyph '{glyph}' entry {entry_idx}: {message}"
    return ValidationError(prefix)


def validate_entry(path: Path, glyph: str, entry_idx: int, entry: Dict) -> Set[str]:
    extra_keys = set(entry.keys()) - ALLOWED_KEYS
    if extra_keys:
        raise _err(path, glyph, entry_idx, f"unexpected fields: {sorted(extra_keys)}")

    if "legacyCodepoints" not in entry:
        raise _err(path, glyph, entry_idx, "missing 'legacyCodepoints'")
    legacy_values = entry["legacyCodepoints"]
    if not isinstance(legacy_values, list) or not legacy_values:
        raise _err(path, glyph, entry_idx, "'legacyCodepoints' must be a non-empty array")

    seen = set()
    for raw in legacy_values:
        if not isinstance(raw, str):
            raise _err(path, glyph, entry_idx, f"legacy codepoint '{raw}' must be a string")
        if not LEGACY_CODEPOINT_RE.match(raw):
            raise _err(
                path,
                glyph,
                entry_idx,
                f"legacy codepoint '{raw}' must be decimal or C-style hex",
            )
        if raw in seen:
            raise _err(path, glyph, entry_idx, f"duplicate legacy codepoint '{raw}'")
        seen.add(raw)

    codepoint = entry.get("codepoint")
    if not isinstance(codepoint, str) or not CODEPOINT_RE.match(codepoint):
        raise _err(path, glyph, entry_idx, "invalid or missing 'codepoint'")

    if "nameIsMakeMusic" in entry and not isinstance(entry["nameIsMakeMusic"], bool):
        raise _err(path, glyph, entry_idx, "'nameIsMakeMusic' must be a boolean")

    if "smuflFontName" in entry and not isinstance(entry["smuflFontName"], str):
        raise _err(path, glyph, entry_idx, "'smuflFontName' must be a string")

    for key in ("description", "notes"):
        if key in entry and not isinstance(entry[key], str):
            raise _err(path, glyph, entry_idx, f"'{key}' must be a string")

    for key in ("xOffset", "yOffset"):
        if key in entry:
            value = entry[key]
            if isinstance(value, int):
                entry[key] = str(value)
                value = entry[key]
            if not isinstance(value, str) or not OFFSET_RE.match(value):
                raise _err(path, glyph, entry_idx, f"'{key}' must be an integer string")

    if "alternate" in entry and not isinstance(entry["alternate"], bool):
        raise _err(path, glyph, entry_idx, "'alternate' must be a boolean")

    return seen


def validate_file(path: Path) -> None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = load_json_strict(handle, location=str(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc
    except DuplicateKeyError as exc:
        raise ValidationError(str(exc)) from exc

    if not isinstance(data, dict):
        raise ValidationError(f"{path}: top-level structure must be an object")

    for glyph, entries in data.items():
        if not isinstance(glyph, str) or not glyph.strip():
            raise ValidationError(f"{path}: glyph names must be non-empty strings")

        if not isinstance(entries, list) or not entries:
            raise ValidationError(f"{path}: glyph '{glyph}' must map to a non-empty array")

        accumulated: Set[str] = set()
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValidationError(
                    f"{path}: glyph '{glyph}' entry {idx} must be an object"
                )
            if "legacyCodepoint" in entry:
                raise ValidationError(
                    f"{path}: glyph '{glyph}' entry {idx} uses deprecated 'legacyCodepoint'"
                )
            entry_codes = validate_entry(path, glyph, idx, entry)
            overlap = accumulated.intersection(entry_codes)
            if overlap:
                dup_list = ", ".join(sorted(overlap))
                raise ValidationError(
                    f"{path}: glyph '{glyph}' entry {idx} reuses legacy codepoint(s): {dup_list}"
                )
            accumulated.update(entry_codes)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate legacy JSON mapping files for smufl_mapping."
    )
    parser.add_argument(
        "--legacy-dir",
        type=Path,
        default=Path("source_json/legacy"),
        help="Directory containing legacy JSON mapping files.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Optional explicit list of files to validate. Overrides --legacy-dir.",
    )
    args = parser.parse_args()

    if args.files:
        files = args.files
    else:
        files = sorted(args.legacy_dir.glob("*.json"))

    if not files:
        print("No legacy mapping files found.", file=sys.stderr)
        return 1

    errors: List[str] = []
    for file_path in files:
        try:
            validate_file(file_path)
        except ValidationError as exc:
            errors.append(str(exc))

    if errors:
        print("Legacy mapping validation failed:", file=sys.stderr)
        for msg in errors:
            print(f"  - {msg}", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} legacy mapping file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
