## Legacy font mapping JSON format

Each file in `source_json/legacy` defines a mapping from **legacy music-font codepoints** (as used by Finale and other pre-SMuFL systems) to **SMuFL glyphs** and Unicode codepoints. The file is a JSON object whose keys are SMuFL glyph names and whose values describe how that glyph appears in the legacy font being mapped.

The authoritative schema lives in [`docs/legacy_mapping.schema.json`](legacy_mapping.schema.json). The summary below mirrors that schema.

### Top-level structure

- The file is a JSON object.
- **Keys** are SMuFL glyph names (strings). Leading and trailing whitespace is ignored.
- **Values** are arrays of entry objects. Even if only one mapping exists, it must be wrapped in an array. This keeps the files valid JSON while preserving multiple legacy mappings per glyph.

### Entry object fields

Each entry object may contain the following fields:

| Field name         | Type            | Required | Description |
|--------------------|-----------------|----------|-------------|
| `legacyCodepoints` | array of string | yes      | One or more legacy font codepoints (decimal or C-style hex). Values must be unique within the array. |
| `codepoint`        | string          | yes*     | The Unicode codepoint of the corresponding SMuFL glyph, written as `"U+XXXX"`. Special handling applies for `"U+FFFD"` (see below). |
| `description`      | string          | no       | A human-readable description of the glyph. Defaults to the empty string if omitted. |
| `nameIsMakeMusic`  | boolean         | no       | Kept for historical accuracy; surfaced but unused by the generator. |
| `smuflFontName`    | string          | no       | Name of the SMuFL font that supplied an optional glyph (e.g., `"Finale Broadway"`, `"Bravura"`). Any value other than `"Bravura"` is treated as Finale metadata. |
| `xOffset`,`yOffset`| integer string  | no       | Positional adjustments translated directly into the generated tables. |
| `alternate`        | boolean         | no       | Set to `true` when the entry intentionally differs from the canonical SMuFL mapping. Absent (or `false`) entries are considered canonical and are preferred during lookups. |
| `notes`            | string          | no       | Free-form annotations for future maintainers. |

\* `codepoint` is required unless it is explicitly set to `"U+FFFD"` and can be resolved from reference data.

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
    "enclosureClosed": [
        {
            "nameIsMakeMusic": true,
            "codepoint": "U+F74A",
            "legacyCodepoints": ["94"],
            "description": "",
            "smuflFontName": "Finale Broadway"
        }
    ],
    "gClef": [
        {
            "codepoint": "U+E050",
            "legacyCodepoints": ["38"],
            "description": ""
        }
    ]
}
```
