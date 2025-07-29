# smufl-mapping

**smufl-mapping** is a lightweight C++ library that provides lookup tables for SMuFL glyph names, Unicode codepoints, and descriptions. It supports standard SMuFL metadata as well as metadata for legacy music fonts using the format developed by MakeMusic for Finale’s legacy music fonts.

This library is header-only except for a single translation unit and is designed for easy integration via CMake and FetchContent.

---

## Features

- Maps SMuFL glyph names to:
  - Unicode codepoints
  - Human-readable descriptions
  - Glyph source (SMuFL, Finale, etc.)
- Separated sources:
  - `glyphnames_smufl.h` for standard SMuFL metadata
  - `glyphnames_finale.h` for Finale-specific glyphs
  - `glyphnames_bravura.h` for Bravura-specific glyphs
  - legacy music font mappings
- Encapsulated via internal namespaces.
- Public lookup API via `smufl_mapping.h`
- Requires **C++17 or higher**
- MIT licensed — free for commercial and open-source use

---

## Usage

### CMake (via FetchContent)

```cmake
include(FetchContent)

FetchContent_Declare(
    smufl_mapping
    GIT_REPOSITORY https://github.com/rpatters1/smufl-mapping.git
    GIT_TAG main  # or use a version tag, branch name, or commit number
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)

FetchContent_MakeAvailable(smufl_mapping)

target_link_libraries(your_target PRIVATE smufl_mapping)
```

Then in C++:

```cpp
#include "smufl_mapping.h"

auto glyph = smufl_mapping::getGlyphInfo("gClef");
if (glyph) {
    std::cout << "Codepoint: " << std::hex << glyph->codepoint << "\n";
}
```

See `src/smufl_mapping.h` for a complete list of functions.

---

## Generated Files

This project includes auto-generated headers derived from SMuFL metadata:

- `src/detail/glyphnames_smufl.h` — from `glyphnames.json` (official glyph defintions)
- `src/detail/glyphnames_finale.h` — from `glyphnamesFinale.json` (optional-range glyphs shared by all Finale SMuFL fonts)
- `src/detail/glyphnames_bravura.h` — from `glyphnamesBravura.json` (optional-range glyphs from Bravura font)
- `src/detail/legacy/...` - legacy fontmappings from legacy mapping files in `source_json/legacy`

The CMake files regenerate these files automatically as needed.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Credits

- SMuFL data from [https://w3c.github.io/smufl](https://w3c.github.io/smufl)
- Finale glyph metadata © MakeMusic, used under fair use for interoperability
