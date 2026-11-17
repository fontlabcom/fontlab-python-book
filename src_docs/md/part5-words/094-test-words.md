---
this_file: src_docs/md/part5-words/094-test-words.md
---

# 94. Test words

Thursday of week eighteen. Tobias, who proofed the kerning in chapter 77, sets a chapter heading from the cookbook in small caps: "Plum jam, baked figs". He sends back a screenshot. Some letters have turned into small capitals and the rest are still lowercase, so the line looks like a ransom note.

Nothing is broken. The `smcp` feature replaces the ten glyphs that have a small cap, and Ines has drawn ten. Yesterday's checker passed the feature, and it was right to: every rule in it is valid. The checker was never asked whether the rules are enough.

That's a question about two sets, the glyphs a feature replaces and the glyphs it ought to replace. You compared two sets in chapter 25, when a list of wanted glyphs met the font. Today you do it again, and the script also hands Tobias something to type.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py`.
- The eight features the font has after chapter 92.

I couldn't run the code in FontLab 9. I ran it in plain Python on Plum's glyph names and code points and on the feature text that chapters 88 to 92 produce. The counts are for the practice font with Part 3's glyphs in it. Without them you have 70 lowercase letters where I have 84, and 62 not covered where I have 76.

## Step 1: What does a feature replace?

Read the rules back out of the text. A one-for-one rule has four words, `sub a by a.sc`, once the semicolon is gone:

```python
def replacements(text):
    pairs = []
    for line in text.splitlines():
        words = line.split("#")[0].replace(";", " ").split()
        if len(words) == 4 and words[0] == "sub" and words[2] == "by":
            pairs.append((words[1], words[3]))
    return pairs
```

Any line that isn't such a rule is skipped: the opening line, the closing line, a ligature rule with five words, a class. This function reads one kind of rule and ignores the rest without complaint, which is the right manners for a reader and would be the wrong manners for yesterday's checker.

Now get at one feature's text. `blocks["features"]` is a list of pairs, tag and text. `dict` turns a list of pairs into a dictionary, as in chapter 87, so you can ask for a feature by its tag:

```python
from fly import fl
import fly.ap.core.scripting as scripting

font = fl.CurrentFont()
package = scripting.current_package()
blocks = scripting.read_feature_blocks(package)
texts = dict(blocks["features"])
pairs = replacements(texts["smcp"])
sources = {source for source, target in pairs}
print(len(pairs), sorted(sources))
```

```text
10 ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'one', 'zero']
```

## Step 2: What should it replace?

Small caps are for lowercase letters. Unicode's category for those is `Ll`, letter lowercase, and chapter 91's function collects glyphs by category. This time keep the character with each name, in a dictionary, because Tobias will want characters to type:

```python
import unicodedata


def by_categories(font, categories):
    found = {}
    for glyph in font.glyphs:
        code = glyph.unicode
        if code is not None and unicodedata.category(chr(code)) in categories:
            found[glyph.name] = chr(code)
    return found


characters = by_categories(font, ["Ll"])
should = set(characters)
print(len(should), characters["a"], characters["germandbls"])
```

```text
84 a ß
```

`set(characters)` makes a set of the dictionary's keys. The practice font has 84 lowercase letters, Plum's 70 and the fourteen Part 3 built. The count takes in the accented letters and a few you might not think of as letters at first, such as `germandbls` and `dotlessi`.

## Step 3: Three questions, three operators

Chapter 25 gave you the operators. `&` keeps what's in both sets. `-` keeps what's in the first and not in the second.

```python
covered = should & sources
missing = should - sources
extra = sources - should
print(len(covered), len(missing), sorted(extra))
```

```text
8 76 ['one', 'zero']
```

Eight lowercase letters have a small cap and 76 don't. Two glyphs are replaced that aren't lowercase letters: the figures `one` and `zero`, whose small-cap glyphs you made in chapter 40. `extra` isn't a fault here. It's the rest of what the feature does, and the report should say so.

## Step 4: The mistake

Mira writes the subtraction from memory, the wrong way round:

```python
missing = sources - should
text = "".join(sorted(characters[name] for name in missing))
```

```text
KeyError: 'zero'
```

Your message may say `'one'`. A set has no order, so either can come first.

`a - b` and `b - a` are different sets. Python has no way to know which you meant, and both are legal. She was lucky. The wrong set held a name the `characters` dictionary doesn't have, and the lookup failed loudly. Had the line printed names, it would have said "missing: one zero" with a straight face, and the report would have blamed the two figures that are covered and kept silent about 62 letters that aren't.

Say the subtraction aloud when you write it: "what should be there, minus what is there, leaves what's missing".

## Step 5: Words to type

A list of 76 glyph names is hard to act on. A row of characters can be pasted into a Glyph window, with the feature switched on, and looked at:

```python
WIDTH = 60


def as_text(names, characters):
    text = "".join(sorted(characters[name] for name in names))
    return text[:WIDTH] + ("..." if len(text) > WIDTH else "")


print(as_text(covered, characters))
print(as_text(missing, characters))
```

```text
abcdefgh
ijklmnopqrstuvwxyzßàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿăćčěğĩıĳńňœŕ...
```

`sorted` puts the characters in code point order, plain letters first. The slice cuts a long row at 60 characters and the dots admit the cut. The value-with-a-choice from chapter 37 adds them only when something was cut.

The first row is what Tobias can set in small caps today: "a bad head", "a faded badge", and little more. The second row is Ines's list of what's still to draw.

The two rows do different jobs. Paste the first into a Glyph window, switch the feature on, and every character should change. If one doesn't, the feature text and the compiled feature disagree, and it's time for the Compile button. Paste the second and nothing should change. I haven't watched either happen, and the place where a Glyph window lets you switch features on is something to find in FontLab's own manual.

## The whole script

```python
#FLM: Feature Coverage
# For each feature in WANTED, compares the glyphs its rules replace
# with the glyphs that ought to be replaced. Changes nothing.
import unicodedata

import halfmoon
from fly import fl
import fly.ap.core.scripting as scripting

WANTED = {"smcp": ["Ll"], "numr": ["Nd"], "dnom": ["Nd"]}
WIDTH = 60


def replacements(text):
    pairs = []
    for line in text.splitlines():
        words = line.split("#")[0].replace(";", " ").split()
        if len(words) == 4 and words[0] == "sub" and words[2] == "by":
            pairs.append((words[1], words[3]))
    return pairs


def by_categories(font, categories):
    found = {}
    for glyph in font.glyphs:
        code = glyph.unicode
        if code is not None and unicodedata.category(chr(code)) in categories:
            found[glyph.name] = chr(code)
    return found


def as_text(names, characters):
    text = "".join(sorted(characters[name] for name in names))
    return text[:WIDTH] + ("..." if len(text) > WIDTH else "")


def report(tag, text, font):
    pairs = replacements(text)
    sources = {source for source, target in pairs}
    characters = by_categories(font, WANTED[tag])
    should = set(characters)
    covered = should & sources
    missing = should - sources
    extra = sources - should
    print(f"{tag}: {len(pairs)} rules, {len(covered)} of {len(should)} covered")
    print(f"  try:     {as_text(covered, characters)}")
    print(f"  missing: {as_text(missing, characters)}")
    if extra:
        print(f"  also:    {' '.join(sorted(extra))}")
    return len(missing)


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    blocks = scripting.read_feature_blocks(package)
    texts = dict(blocks["features"])
    total = 0
    for tag in WANTED:
        if tag not in texts:
            print(f"{tag}: no such feature")
            continue
        total += report(tag, texts[tag], font)
    print(f"{total} glyphs not covered.")


main()
```

Save it as `feature_coverage.py`. It prints:

```text
smcp: 10 rules, 8 of 84 covered
  try:     abcdefgh
  missing: ijklmnopqrstuvwxyzßàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿăćčěğĩıĳńňœŕ...
  also:    one zero
numr: 10 rules, 10 of 10 covered
  try:     0123456789
  missing: 
dnom: 10 rules, 10 of 10 covered
  try:     0123456789
  missing: 
76 glyphs not covered.
```

Notes on the listing.

`WANTED` maps a tag to a list of categories, where chapter 91's table held one category per row. A feature for capitals and lowercase together could say `["Lu", "Ll"]`.

`frac` isn't in the table. Its rules replace classes, and `replacements` would find two four-word rules in it, one of them between classes, `sub @frac_plain by @frac_up`. A coverage figure built on that would be nonsense, so the script doesn't offer one. `liga` is left out for a similar reason: nobody can say which letter sequences ought to have a ligature.

`report` prints and also returns a number, the count of missing glyphs, which `main` adds up. Chapter 93 kept finding and printing apart. This script is small enough to get away with mixing them, and chapter 100 will ask it to stop.

The `try` row for `numr` is the test string for the fraction figures. Type it with the feature on once Ines has drawn them, and ten small raised figures should appear.

## Break it on purpose

Make a new glyph called `i.sc`. A copy of `I` will do, or an empty glyph from chapter 40's script. Run the coverage script:

```text
smcp: 10 rules, 8 of 84 covered
```

Still 8. The glyph is in the font and the report doesn't see it, because the report reads the feature's rules and the feature was written before `i.sc` existed. This is chapter 91's lesson from another side. Feature text is a list somebody wrote on a certain day, and the font moves on without it.

Run `make_smcp.py` from chapter 88 again, so the feature is rebuilt from the suffixes, and then the coverage script: 11 rules, 9 of 84. Whenever glyphs are added, the order of work is to rebuild the feature, check it, measure its coverage and compile it. Chapter 100 puts the middle two into one run.

## What the rule can't know

Look at the end of the missing list. The script cut it at 60 characters, and the last two of the 76 are `fi` and `fl`. Unicode files the two ligature characters under lowercase letters, so the script wants small caps for them. No designer draws those. In a sound font, small caps are applied before ligatures or the ligature rules leave small caps alone, and "fi" in small caps is an F and an I.

The same goes for `germandbls`, the ß. Its small cap is often two glyphs, SS, which a one-for-one rule can't express.

So the 76 is an upper limit, and the true to-do list is a few shorter. A category is a fair first guess at "what should be covered". Ines's judgment is the second. Exercise 2 gives the script a way to hear it.

## What you learned

Whether a feature is valid and whether it's complete are separate questions, and the second is a comparison of two sets. `&` gives what two sets share, and `-` gives what the first has and the second lacks, so the order of a subtraction decides the answer. `dict` turns a list of pairs into a dictionary you can look things up in. A report that prints characters to type is more use to a proofreader than a list of glyph names.

## Try it yourself

1. Add `"zero": ["Nd"]` to `WANTED` and run the script. The answer is 1 of 10 covered. Is that a fault in the feature? Say why a slashed-zero feature and this table don't fit together.
2. Add a set `NO_SMALL_CAP = {"fi", "fl", "germandbls"}` at the top and subtract it from `should` when the tag is `smcp`. What does the last line of the report say now?
3. Tobias wants words, not rows of letters. Take a list of ten words from the cookbook and print the ones that use only covered characters: a word passes when `set(word) - set(as_text(covered, characters))` is empty. Mind the dots that `as_text` may add.

## Next

Eight features are written, checked and measured. The words the font can set are in order. There are other words inside a font: its own name, which a menu shows before anyone sees a glyph. Chapter 95 reads the family name and its relatives out of Font Info.
