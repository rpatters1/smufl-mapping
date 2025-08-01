#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from datetime import datetime

def parse_codepoint(uplus):
    return int(uplus.replace("U+", ""), 16)

def escape_cpp_string(text):
    return text.replace("\\", "\\\\").replace("\"", "\\\"")

def derive_var_name(input_path: Path) -> str:
    stem = input_path.stem
    if stem == "glyphnames":
        return "glyphnamesSmufl"
    return stem

def generate_glyphnames_header(input_path: Path, var_name: str, output_path: Path):
    with open(input_path, "r", encoding="utf-8") as f:
        glyphs = json.load(f)

    # Determine source enum based on filename
    if input_path.name == "glyphnames.json":
        source_enum = "SmuflGlyphSource::Smufl"
    elif input_path.name == "glyphnamesFinale.json":
        source_enum = "SmuflGlyphSource::Finale"
    elif input_path.name == "glyphnamesBravura.json":
        source_enum = "SmuflGlyphSource::Bravura"
    else:
        source_enum = "SmuflGlyphSource::Unknown"

    entries = []
    for name, data in glyphs.items():
        codepoint = parse_codepoint(data.get("codepoint", "U+FFFD"))
        description = escape_cpp_string(data.get("description", ""))
        entries.append((name.strip(), codepoint, description))

    entries.sort()

    reverse_entries = [(cp, name) for (name, cp, _) in entries]
    reverse_entries.sort()

    reverse_var_name = "reverse" + var_name[0].upper() + var_name[1:]

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"// This file is generated from source_json/{input_path.name}. DO NOT EDIT.\n")
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
        out.write("#pragma once\n\n")
        out.write("#include <string_view>\n#include <utility>\n\n")
        out.write('#include "smufl_mapping.h"\n\n')
        out.write("namespace smufl_mapping {\n")
        out.write("namespace detail {\n\n")

        # Forward map
        out.write("// Sorted array for binary search lookup by glyph name\n")
        out.write(f"inline constexpr std::pair<std::string_view, SmuflGlyphInfo> {var_name}[] = {{\n")
        for name, cp, desc in entries:
            out.write(f'    {{ "{name}", {{ 0x{cp:X}, "{desc}", {source_enum} }} }},\n')
        out.write("};\n\n")

        # Reverse map
        out.write("// Sorted array for binary search lookup by codepoint\n")
        out.write(f"inline constexpr std::pair<char32_t, std::string_view> {reverse_var_name}[] = {{\n")
        for cp, name in reverse_entries:
            out.write(f'    {{ 0x{cp:X}, "{name}" }},\n')
        out.write("};\n\n")

        out.write("} // namespace detail\n")
        out.write("} // namespace smufl_mapping\n")

# Entry point
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_glyphnames_map.py <glyphnames.json> <output.h>")
        sys.exit(1)

    input_json = Path(sys.argv[1])
    var_name = derive_var_name(input_json)
    output_header = Path(sys.argv[2])

    generate_glyphnames_header(input_json, var_name, output_header)
