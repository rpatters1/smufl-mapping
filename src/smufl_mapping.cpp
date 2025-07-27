/*
 * Copyright (C) 2025, Robert Patterson
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include "smufl_mapping.h"

#include "detail/glyphnames_smufl.h"
#include "detail/glyphnames_finale.h"
#include "detail/glyphnames_bravura.h"

namespace smufl_mapping {

const SmuflGlyphInfo* getGlyphInfo(std::string_view name,
                                   std::optional<SmuflGlyphSource> optionalSource)
{
    // Local lambda to search a map
    auto findIn = [&](const auto& map) -> const SmuflGlyphInfo* {
        auto it = map.find(name);
        return it != map.end() ? &it->second : nullptr;
    };

    // Step 1: Search standard set (glyphnamesSmufl)
    if (const SmuflGlyphInfo* info = findIn(detail::glyphnamesSmufl)) {
        return info;
    }

    // Step 2: If a specific optional source is given, search only that
    if (optionalSource) {
        switch (*optionalSource) {
            case SmuflGlyphSource::Bravura:
                return findIn(detail::glyphnamesBravura);
            case SmuflGlyphSource::Finale:
                return findIn(detail::glyphnamesFinale);
            default:
                return nullptr;
        }
    }

    // Step 3: Not found
    return nullptr;
}

#ifndef DOXYGEN_SHOULD_IGNORE_THIS
template <const std::unordered_map<std::string_view, SmuflGlyphInfo>& Map>
static const std::unordered_map<char32_t, std::string_view>& getReverseMap()
{
    static std::unordered_map<char32_t, std::string_view> reverseMap = [] {
        std::unordered_map<char32_t, std::string_view> result;
        for (const auto& [name, info] : Map) {
            result[info.codepoint] = name;
        }
        return result;
    }();
    return reverseMap;
}
#endif // DOXYGEN_SHOULD_IGNORE_THIS

const std::string_view* getGlyphName(char32_t codepoint,
                                     std::optional<SmuflGlyphSource> optionalSource)
{
    // Step 1: Try standard glyph set
    {
        const auto& reverse = getReverseMap<detail::glyphnamesSmufl>();
        auto it = reverse.find(codepoint);
        if (it != reverse.end()) {
            return &it->second;
        }
    }

    // Step 2: If optional source is provided, search only that set
    if (optionalSource) {
        switch (*optionalSource) {
            case SmuflGlyphSource::Bravura: {
                const auto& reverse = getReverseMap<detail::glyphnamesBravura>();
                auto it = reverse.find(codepoint);
                if (it != reverse.end()) {
                    return &it->second;
                }
                break;
            }
            case SmuflGlyphSource::Finale: {
                const auto& reverse = getReverseMap<detail::glyphnamesFinale>();
                auto it = reverse.find(codepoint);
                if (it != reverse.end()) {
                    return &it->second;
                }
                break;
            }
            default:
                break;
        }
    }

    // Step 3: Not found
    return nullptr;
}

} // namespace smufl_mapping

