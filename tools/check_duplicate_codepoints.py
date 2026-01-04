#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def parse_codepoint(value: str) -> int:
    if not value or not value.startswith("U+"):
        raise ValueError(f"Invalid codepoint format: {value}")
    return int(value[2:], 16)


def load_codepoints(path: Path) -> dict[int, str]:
    data = json.loads(path.read_text())
    mapping = {}
    for name, props in data.items():
        if not isinstance(props, dict):
            continue
        cp = props.get("codepoint")
        if not cp:
            continue
        try:
            cp_int = parse_codepoint(cp)
        except ValueError:
            continue
        mapping[cp_int] = name.strip()
    return mapping


def find_conflicts(std_map: dict[int, str], optional_map: dict[int, str], label: str):
    conflicts = []
    for cp, opt_name in optional_map.items():
        if cp in std_map:
            conflicts.append((cp, std_map[cp], opt_name, label))
    return conflicts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect duplicate SMuFL codepoints between standard and optional glyph sets."
    )
    parser.add_argument("--std", type=Path, default=Path("source_json/glyphnames.json"))
    parser.add_argument("--finale", type=Path, default=Path("source_json/glyphnamesFinale.json"))
    parser.add_argument("--bravura", type=Path, default=Path("source_json/glyphnamesBravura.json"))
    args = parser.parse_args()

    std_map = load_codepoints(args.std)
    finale_map = load_codepoints(args.finale)
    bravura_map = load_codepoints(args.bravura)

    conflicts = []
    conflicts.extend(find_conflicts(std_map, finale_map, "Finale"))
    conflicts.extend(find_conflicts(std_map, bravura_map, "Bravura"))

    if conflicts:
        print("Duplicate codepoints between standard SMuFL and optional glyph sets:")
        for cp, std_name, opt_name, label in conflicts:
            print(f"  U+{cp:04X}: '{std_name}' vs '{opt_name}' ({label})")
        return 1

    print("No duplicate codepoints found between standard SMuFL and optional glyph sets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
