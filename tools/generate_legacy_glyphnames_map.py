#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent  # root of repo
SOURCE_DIR = BASE_DIR / "source_json" / "legacy"
FINALE_FILE = BASE_DIR / "source_json" / "glyphnamesFinale.json"
BRAVURA_FILE = BASE_DIR / "source_json" / "glyphnamesBravura.json"
OUTPUT_DIR = BASE_DIR / "src" / "detail" / "legacy"
MASTER_HEADER = BASE_DIR / "src" / "detail" / "glyphnames_legacy.h"

def parse_codepoint(uplus: str) -> int:
    if not uplus.startswith("U+"):
        raise ValueError(f"Invalid codepoint format: {uplus}")
    return int(uplus[2:], 16)

def load_glyphnames(path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    name_to_codepoint = {}
    for name, props in data.items():
        if "codepoint" in props:
            try:
                name_to_codepoint[name.strip()] = parse_codepoint(props["codepoint"])
            except Exception as e:
                print(f"Warning: Failed to parse codepoint for {name}: {e}")
    return name_to_codepoint

def sanitize_var_name(stem: str) -> str:
    parts = stem.replace("-", " ").replace("_", " ").split()
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

def sanitize_file_name(stem: str) -> str:
    return stem.lower().replace("-", "_").replace(" ", "_")

def load_json_allow_duplicates(path: Path):
    def _object_pairs_hook(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                existing = obj[key]
                if isinstance(existing, list):
                    existing.append(value)
                else:
                    obj[key] = [existing, value]
            else:
                obj[key] = value
        return obj

    with path.open("r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=_object_pairs_hook)


def process_legacy_file(path: Path, finale_map: dict, bravura_map: dict) -> tuple[str, Path]:
    data = load_json_allow_duplicates(path)

    fontname = path.stem
    varname = sanitize_var_name(fontname) + "LegacyGlyphs"
    outpath = OUTPUT_DIR / f"{sanitize_file_name(fontname)}_legacy_map.h"

    entries = []

    for glyphname, value in data.items():
        glyphname = glyphname.strip()

        values = value if isinstance(value, list) else [value]

        for glyph_data in values:
            if not isinstance(glyph_data, dict):
                print(f"Unexpected entry type for '{glyphname}' in {path.name}; skipping")
                continue

            legacy_codepoint_str = glyph_data.get("legacyCodepoint")
            if not legacy_codepoint_str:
                print(f"Missing legacyCodepoint for '{glyphname}' in {path.name}")
                continue
            raw_codepoint = glyph_data.get("codepoint")
            description = glyph_data.get("description", "")
            smufl_font = glyph_data.get("smuflFontName", "finale").lower() # this is RGP proprietary in Lua mapping script: hopefully we can get something like it approved by SMuFL committee

            try:
                legacy_codepoint = int(legacy_codepoint_str, 0)
            except ValueError:
                print(f"Invalid legacyCodepoint '{legacy_codepoint_str}' for '{glyphname}' in {path.name}")
                continue

            # Resolve FFFD
            if raw_codepoint == "U+FFFD":
                resolved = finale_map.get(glyphname)
                if resolved:
                    codepoint = resolved
                    # print(f"Resolved 0xFFFD for {glyphname} → U+{resolved:04X}")
                else:
                    print(f"Could not resolve 0xFFFD for {glyphname}; setting to 0")
                    codepoint = 0
            else:
                if not raw_codepoint:
                    print(f"Missing codepoint for '{glyphname}' in {path.name}; skipping")
                    continue
                try:
                    codepoint = parse_codepoint(raw_codepoint)
                except Exception:
                    print(f"Invalid codepoint '{raw_codepoint}' for '{glyphname}' in {path.name}; skipping")
                    continue

            # Filter optional-range entries not in glyphnamesFinale
            if 0xF400 <= codepoint <= 0xF8FF:
                target_map = bravura_map if smufl_font == "bravura" else finale_map
                if glyphname not in target_map:
                    print(f"Omitting optional-range glyph '{glyphname}' (not found in glyphnames{smufl_font.capitalize()})")
                    continue

            if 0xF400 <= codepoint <= 0xF8FF:
                if smufl_font == "bravura":
                    source_enum = "SmuflGlyphSource::Bravura"
                else:
                    source_enum = "SmuflGlyphSource::Finale"
            else:
                source_enum = "SmuflGlyphSource::Smufl"

            entries.append((legacy_codepoint, glyphname, codepoint, description, source_enum))

    # Emit C++ header
    entries.sort(key=lambda entry: entry[0])
    with outpath.open("w", encoding="utf-8") as out:
        out.write("// This file is generated from {}\n".format(path.name))
        out.write("//\n")
        out.write(f"// SPDX-FileCopyrightText: Generated by smufl_mapping ({datetime.now().year})\n")
        out.write("// SPDX-License-Identifier: MIT\n")
        out.write("//\n")
        out.write("// Source project: https://github.com/rpatters1/smufl-mapping\n")
        out.write("//\n")
        out.write("// This header was generated from SMuFL font metadata provided by SMuFL and Finale\n")
        out.write("// and is part of the internal implementation of the smufl_mapping project.\n")
        out.write("//\n")
        out.write("// To regenerate this file, run tools/generate_glyphnames_map.py\n")
        out.write('#pragma once\n\n')
        out.write('#include "smufl_mapping.h"\n\n')
        out.write('namespace smufl_mapping::detail::legacy {\n\n')
        out.write(f'constexpr std::pair<char32_t, LegacyGlyphInfo> {varname}[] = {{\n')
        for legacy_cp, gname, cp, desc, source in entries:
            desc_escaped = desc.replace('"', '\\"')
            out.write(f'    {{ {legacy_cp:3}, '
                    f'{{ "{gname}", 0x{cp:X}, "{desc_escaped}", {source} }} }},\n')
        out.write('};\n\n')
        out.write('} // namespace smufl_mapping::detail::legacy\n')

    return varname, outpath

from typing import List, Tuple
def emit_master_header(entries: List[Tuple[str, str]]):
    # entries: list of (fontname, varname) tuples
    entries.sort(key=lambda item: item[0])
    outpath = MASTER_HEADER
    with outpath.open("w", encoding="utf-8") as out:
        out.write("// This file is auto-generated. Do not edit manually.\n")
        out.write("//\n")
        out.write(f"// SPDX-FileCopyrightText: Generated by smufl_mapping ({datetime.now().year})\n")
        out.write("// SPDX-License-Identifier: MIT\n")
        out.write("//\n")
        out.write("// Source project: https://github.com/rpatters1/smufl-mapping\n")
        out.write("//\n")
        out.write("// This header was generated from SMuFL font metadata provided by SMuFL and Finale\n")
        out.write("// and is part of the internal implementation of the smufl_mapping project.\n")
        out.write("//\n")
        out.write("// To regenerate this file, run tools/generate_glyphnames_map.py\n")
        out.write('#pragma once\n\n')
        out.write('#include "smufl_mapping.h"\n\n')

        for fontname, _ in entries:
            out.write(f'#include "detail/legacy/{sanitize_file_name(fontname)}_legacy_map.h"\n')

        out.write('\nnamespace smufl_mapping::detail {\n\n')

        out.write('struct LegacyFontMapping {\n')
        out.write('    const std::pair<char32_t, LegacyGlyphInfo>* table;\n')
        out.write('    std::size_t size;\n')
        out.write('};\n\n')

        out.write('constexpr std::pair<std::string_view, LegacyFontMapping> legacyFontMappings[] = {\n')
        for fontname, varname in entries:
            out.write(f'    {{ "{fontname.lower()}", {{legacy::{varname}, std::size(legacy::{varname})}} }},\n')
        out.write('};\n\n')

        out.write('} // namespace smufl_mapping::detail\n')

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    finale_map = load_glyphnames(FINALE_FILE)
    bravura_map = load_glyphnames(BRAVURA_FILE)

    all_entries = []
    for json_path in sorted(SOURCE_DIR.glob("*.json")):
        fontname = json_path.stem
        varname, _ = process_legacy_file(json_path, finale_map, bravura_map)
        all_entries.append((fontname, varname))

    emit_master_header(all_entries)

if __name__ == "__main__":
    main()
