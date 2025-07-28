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
#include <algorithm>
#include <string>

#include "smufl_mapping.h"

#include "detail/glyphnames_smufl.h"
#include "detail/glyphnames_finale.h"
#include "detail/glyphnames_bravura.h"
#include "detail/glyphnames_legacy.h"

namespace smufl_mapping {

#ifndef DOXYGEN_SHOULD_IGNORE_THIS
template <typename Key, typename Pair>
static constexpr const typename Pair::second_type* binarySearchByKey(
    const Key& key,
    const Pair* table,
    std::size_t size) noexcept
{
    std::size_t low = 0;
    std::size_t high = size;

    while (low < high) {
        std::size_t mid = low + (high - low) / 2;
        const auto& pair = table[mid];

        if (pair.first < key) {
            low = mid + 1;
        } else if (key < pair.first) {
            high = mid;
        } else {
            return &pair.second;
        }
    }

    return nullptr;
}

template <typename Key, typename Pair, std::size_t N>
static constexpr const typename Pair::second_type* binarySearchByKey(
    const Key& key,
    const Pair (&table)[N]) noexcept
{
    return binarySearchByKey<Key, Pair>(key, table, N);
}
#endif // DOXYGEN_SHOULD_IGNORE_THIS

const SmuflGlyphInfo* getGlyphInfo(std::string_view name,
                                   std::optional<SmuflGlyphSource> optionalSource)
{
    // Step 1: Search standard set (glyphnamesSmufl)
    if (const SmuflGlyphInfo* info = binarySearchByKey(name, detail::glyphnamesSmufl)) {
        return info;
    }

    // Step 2: If a specific optional source is given, search only that
    if (optionalSource) {
        switch (*optionalSource) {
            case SmuflGlyphSource::Bravura:
                return binarySearchByKey(name, detail::glyphnamesBravura);
            case SmuflGlyphSource::Finale:
                return binarySearchByKey(name, detail::glyphnamesFinale);
            default:
                return nullptr;
        }
    }

    // Step 3: Not found
    return nullptr;
}

const std::string_view* getGlyphName(char32_t codepoint,
                                     std::optional<SmuflGlyphSource> optionalSource)
{
    // Step 1: Try standard glyph set
    if (const auto* name = binarySearchByKey(codepoint, detail::reverseGlyphnamesSmufl)) {
        return name;
    }

    // Step 2: If optional source is provided, search only that set
    if (optionalSource) {
        switch (*optionalSource) {
            case SmuflGlyphSource::Bravura:
                return binarySearchByKey(codepoint, detail::reverseGlyphnamesBravura);

            case SmuflGlyphSource::Finale:
                return binarySearchByKey(codepoint, detail::reverseGlyphnamesFinale);

            default:
                break;
        }
    }

    // Step 3: Not found
    return nullptr;
}

// Lowercase normalization for case-insensitive font name lookup
static std::string toLower(std::string_view s)
{
    std::string out(s);
    std::transform(out.begin(), out.end(), out.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    return out;
}

const LegacyGlyphInfo* getLegacyGlyphInfo(std::string_view fontName, char32_t codepoint)
{
    const detail::LegacyFontMapping* entry = binarySearchByKey(std::string_view(toLower(fontName)), detail::legacyFontMappings);

    if (!entry) {
        return nullptr;
    }

    return binarySearchByKey(codepoint, entry->table, entry->size);
}

} // namespace smufl_mapping

