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
#include <unordered_map>

#include "smufl_mapping.h"

#include "detail/glyphnames_smufl.h"
#include "detail/glyphnames_finale.h"
#include "detail/glyphnames_bravura.h"

namespace smufl_mapping {

#ifndef DOXYGEN_SHOULD_IGNORE_THIS
template <std::size_t N>
static constexpr const SmuflGlyphInfo* findGlyphInfoByName(
    std::string_view name,
    const std::pair<std::string_view, SmuflGlyphInfo> (&table)[N]) noexcept
{
    std::size_t low = 0;
    std::size_t high = N;

    while (low < high) {
        std::size_t mid = low + (high - low) / 2;
        const auto& pair = table[mid];

        if (pair.first < name) {
            low = mid + 1;
        } else if (pair.first > name) {
            high = mid;
        } else {
            return &pair.second;
        }
    }

    return nullptr;
}
#endif // DOXYGEN_SHOULD_IGNORE_THIS

const SmuflGlyphInfo* getGlyphInfo(std::string_view name,
                                   std::optional<SmuflGlyphSource> optionalSource)
{
    // Step 1: Search standard set (glyphnamesSmufl)
    if (const SmuflGlyphInfo* info = findGlyphInfoByName(name, detail::glyphnamesSmufl)) {
        return info;
    }

    // Step 2: If a specific optional source is given, search only that
    if (optionalSource) {
        switch (*optionalSource) {
            case SmuflGlyphSource::Bravura:
                return findGlyphInfoByName(name, detail::glyphnamesBravura);
            case SmuflGlyphSource::Finale:
                return findGlyphInfoByName(name, detail::glyphnamesFinale);
            default:
                return nullptr;
        }
    }

    // Step 3: Not found
    return nullptr;
}

#ifndef DOXYGEN_SHOULD_IGNORE_THIS
template <std::size_t N>
static constexpr const std::string_view* findGlyphNameByCodepoint(
    char32_t codepoint,
    const std::pair<char32_t, std::string_view> (&table)[N])
{
    std::size_t low = 0;
    std::size_t high = N;

    while (low < high) {
        std::size_t mid = low + (high - low) / 2;
        const auto& pair = table[mid];

        if (pair.first < codepoint) {
            low = mid + 1;
        } else if (pair.first > codepoint) {
            high = mid;
        } else {
            return &pair.second;
        }
    }

    return nullptr;
}
#endif // DOXYGEN_SHOULD_IGNORE_THIS

const std::string_view* getGlyphName(char32_t codepoint,
                                     std::optional<SmuflGlyphSource> optionalSource)
{
    // Step 1: Try standard glyph set
    if (const auto* name = findGlyphNameByCodepoint(codepoint, detail::reverseGlyphnamesSmufl)) {
        return name;
    }

    // Step 2: If optional source is provided, search only that set
    if (optionalSource) {
        switch (*optionalSource) {
            case SmuflGlyphSource::Bravura:
                return findGlyphNameByCodepoint(codepoint, detail::reverseGlyphnamesBravura);

            case SmuflGlyphSource::Finale:
                return findGlyphNameByCodepoint(codepoint, detail::reverseGlyphnamesFinale);

            default:
                break;
        }
    }

    // Step 3: Not found
    return nullptr;
}

} // namespace smufl_mapping

