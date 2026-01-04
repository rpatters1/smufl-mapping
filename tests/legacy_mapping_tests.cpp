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

#include <gtest/gtest.h>
#include "smufl_mapping.h"

using namespace smufl_mapping;

TEST(LegacyGlyphInfoTests, KnownGlyphLookup)
{
    {
        auto* info = getLegacyGlyphInfo("maestro", 207);
        ASSERT_NE(info, nullptr);
        EXPECT_EQ(info->name, "noteheadBlack");
        EXPECT_EQ(info->codepoint, 0xE0A4);
        EXPECT_EQ(info->source, SmuflGlyphSource::Smufl);
    }
    {
        auto* info = getLegacyGlyphInfo("Jazz", 103);
        EXPECT_EQ(info->name, "arpeggioVerticalSegment");
        EXPECT_EQ(info->codepoint, 0xF700);
        EXPECT_EQ(info->source, SmuflGlyphSource::Finale);
    }
}

TEST(LegacyGlyphInfoTests, CaseInsensitiveFontName)
{
    auto* info = getLegacyGlyphInfo("ChacOnNe", 65);
    ASSERT_NE(info, nullptr);
    EXPECT_EQ(info->name, "accidentalFlatParens");
    EXPECT_EQ(info->codepoint, 0xF5D5);
    EXPECT_EQ(info->source, SmuflGlyphSource::Finale);
}

TEST(LegacyGlyphInfoTests, IgnoresSpacesInFontName)
{
    auto* compact = getLegacyGlyphInfo("FinaleCopyistText", 123);
    ASSERT_NE(compact, nullptr);
    EXPECT_EQ(compact->name, "enclosureBracketLeft");
    EXPECT_EQ(compact->codepoint, 0xF720);

    auto* spaced = getLegacyGlyphInfo("Finale Copyist Text", 123);
    ASSERT_NE(spaced, nullptr);
    EXPECT_EQ(spaced->name, "enclosureBracketLeft");
    EXPECT_EQ(spaced->codepoint, 0xF720);
}

TEST(LegacyGlyphInfoTests, UnknownFont)
{
    auto* info = getLegacyGlyphInfo("unknownfont", 0xF000);
    EXPECT_EQ(info, nullptr);
}

TEST(LegacyGlyphInfoTests, UnknownCodepoint)
{
    // Assuming 0xFFFF isn't mapped in "maestro"
    auto* info = getLegacyGlyphInfo("maestro", 0xFFFF);
    EXPECT_EQ(info, nullptr);
}

TEST(LegacyGlyphInfoTests, CollisionPrefersFirstCanonicalEntry)
{
    auto* info = getLegacyGlyphInfo("maestro", 45);
    ASSERT_NE(info, nullptr);
    EXPECT_EQ(info->name, "articTenutoAbove");
    EXPECT_EQ(info->codepoint, 0xE4A4);
}

TEST(LegacyGlyphInfoTests, CollisionSkipsAlternateEntry)
{
    auto* info = getLegacyGlyphInfo("Broadway Copyist", 246);
    ASSERT_NE(info, nullptr);
    EXPECT_EQ(info->name, "csymAugmented");
    EXPECT_EQ(info->codepoint, 0xE872);
}

TEST(LegacyGlyphInfoTests, GetAllReturnsCanonicalThenAlternate)
{
    auto infos = getAllLegacyGlyphInfo("Broadway Copyist", 246);
    ASSERT_EQ(infos.size(), 3u);
    EXPECT_EQ(infos[0]->name, "csymAugmented");
    EXPECT_FALSE(infos[0]->alternate);
    EXPECT_EQ(infos[1]->name, "timeSigPlus");
    EXPECT_FALSE(infos[1]->alternate);
    EXPECT_TRUE(infos[2]->alternate);
    EXPECT_EQ(infos[2]->name, "brassMuteClosed");
}

TEST(LegacyGlyphInfoTests, GetAllReturnsAllCanonicalEntries)
{
    auto infos = getAllLegacyGlyphInfo("maestro", 45);
    ASSERT_EQ(infos.size(), 2u);
    EXPECT_EQ(infos[0]->name, "articTenutoAbove");
    EXPECT_EQ(infos[1]->name, "articTenutoBelow");
    EXPECT_FALSE(infos[0]->alternate);
    EXPECT_FALSE(infos[1]->alternate);
}
