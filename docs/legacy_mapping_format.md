## Legacy font mapping JSON format

Each file in `source_json/legacy` defines a mapping from **legacy music-font codepoints** (as used by Finale and other pre-SMuFL systems) to **SMuFL glyphs** and Unicode codepoints. The file is a JSON object whose keys are SMuFL glyph names and whose values describe how that glyph appears in the legacy font being mapped.

Note: Some of the legacy mapping files contain duplicate keys, reflecting errors in the original MakeMusic data. As a result, they are not strictly valid JSON but are parsed with a custom loader that preserves all entries.

### Top-level structure

- The file is a JSON object.
- **Keys** are SMuFL glyph names (strings). Leading and trailing whitespace is ignored.
- **Values** may be either:
  - a single object, or
  - a list of objects, allowing multiple legacy mappings for the same glyph name.

This design allows the format to represent duplicate glyph names without losing information.

### Entry object fields

Each entry object may contain the following fields:

| Field name         | Type     | Required | Description |
|--------------------|----------|----------|-------------|
| `nameIsMakeMusic`  | boolean  | no       | Sometimes used by MakeMusic to denote optional glyphs from Finale. It is currently unreferenced by the Python scripts.|
| `legacyCodepoint`  | string   | yes      | The codepoint used by the legacy font. Parsed as an integer using C-style notation (e.g. `"121"` or `"0x2041"`). |
| `codepoint`        | string   | yes*     | The Unicode codepoint of the corresponding SMuFL glyph, written as `"U+XXXX"`. Special handling applies for `"U+FFFD"` (see below). |
| `description`      | string   | no       | A human-readable description of the glyph. Defaults to the empty string if omitted. |
| `smuflFontName`    | string   | no       | Indicates the name of the SMuFL font that supplied an optional glyph. |

\* `codepoint` is required unless it is explicitly set to `"U+FFFD"` and can be resolved from reference data.

### Duplicate glyph names

If a glyph name maps to multiple legacy codepoints, its key value appears multiple times in the dictionary. While this is invalid JSON, the Python scripts nevertheless process all entries independently, preserving the full set of mappings.

### Handling of `U+FFFD`

If `codepoint` is `"U+FFFD"`, the script attempts to resolve the actual Unicode codepoint by looking up the glyph name in `glyphnamesFinale.json`. If resolution fails, the Unicode codepoint is set to `0` and a warning is emitted. This works around how the original Finale mappings were coded. Future contributions should supply explicit Unicode codepoints rather than relying on this fallback.

### Optional-range glyphs (U+F400–U+F8FF)

Unicode codepoints in the private-use optional SMuFL range (`U+F400`–`U+F8FF`) are validated against reference glyph lists:

- If `smuflFontName` is `"Bravura"`, the glyph must exist in `glyphnamesBravura.json`.
- Otherwise, it must exist in `glyphnamesFinale.json`.

Optional-range entries whose glyph names are not found in the appropriate reference list are omitted.

Additional SMuFL font sources may be supported in the future, and contributions that extend the set of optional glyph sources are welcome.

### Glyph source classification

Each processed entry is tagged with a source indicating where the Unicode codepoint originates:

- `SmuflGlyphSource::Smufl`  
  For codepoints outside the optional private-use range.
- `SmuflGlyphSource::Finale`  
  For optional-range glyphs resolved via Finale metadata.
- `SmuflGlyphSource::Bravura`  
  For optional-range glyphs resolved via Bravura metadata.

### Sample mapping entry

```json
{
	"enclosureClosed": {
		"nameIsMakeMusic": true,
		"codepoint": "U+F74A",
		"legacyCodepoint": "94",
		"description": "",
        "smuflFontName": "Finale Broadway"
	},
	"gClef": {
		"codepoint": "U+E050",
		"legacyCodepoint": "38",
		"description": ""
	}
}
```
