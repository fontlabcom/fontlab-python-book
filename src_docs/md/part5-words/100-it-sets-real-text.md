---
this_file: src_docs/md/part5-words/100-it-sets-real-text.md
---

# 100. It sets real text

Friday of week nineteen. This afternoon the publisher's typesetter installs Plum in her layout program and pours a real chapter into it: a cover line in capitals, a recipe with ½ cup of flour, a heading in small caps. Nobody at Halfmoon will be in the room.

Four weeks ago Mira couldn't have said whether the font was fit to go. Now she has a folder of scripts that each answer one question: are the names good, does every character have one glyph, do the features mention glyphs that exist, does Font Info say the same thing everywhere. Oskar's worry is a different one. "There are nineteen of them," he says. "On a Friday, you'll run nine."

So the last script of Part 5 adds nothing new to the font. It asks the old questions in one run and gives one answer.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py`.
- The work of chapters 81 to 99 done. If you skipped some, the pre-flight will tell you which.

I couldn't run the code in FontLab 9. I ran the script in plain Python against a stand-in built from Plum's source file plus the glyphs and features this part added, and then against the same font with five faults put in. Your counts will differ from mine wherever your font does.

## Step 1: Every check has the same shape

Chapter 80 collected the spacing checks in a list and ran them in a loop. That works when every check takes the same things and gives back the same things. Here each one takes the font and its package, and returns how many things it looked at and a list of sentences:

```python
def check_unicodes(font, package):
    owners = {}
    for glyph in font.glyphs:
        if glyph.unicode is None:
            continue
        if glyph.unicode not in owners:
            owners[glyph.unicode] = []
        owners[glyph.unicode].append(glyph.name)
    problems = []
    for code, names in owners.items():
        if len(names) > 1:
            problems.append(f"U+{code:04X} belongs to {' and '.join(names)}")
    return len(owners), problems
```

This is chapter 84's question asked backwards. That chapter looked for a glyph with two characters. This one looks for a character with two glyphs, which a typesetter meets as the wrong letter appearing when she types.

The function prints nothing. Chapter 93 kept finding and printing apart, and chapter 94 mixed them and said it would have to stop. Here's why. A check that prints can only be used where its printing is wanted. A check that returns a list can be counted, sorted, saved to a file, or shown in a window in Part 7.

## Step 2: Short versions, and why

The pre-flight doesn't call `name_check.py` or `check_features.py`. Each of those files ends with the line `main()`, so importing one would run it, as you saw in chapter 33. The pre-flight carries its own short version of each question instead. Chapter 81 has six rules about names, and the pre-flight has two. The long scripts are still the ones to run when a short check complains.

The features check is the newest idea in the listing. It collects every word in the feature text and asks which suffixed glyphs aren't among them:

```python
def check_features(font, package):
    blocks = scripting.read_feature_blocks(package)
    text = blocks["prefix"] + " ".join(code for tag, code in blocks["features"])
    for ch in "[];'<>{}":
        text = text.replace(ch, " ")
    words = set(text.split())
    suffixed = [glyph.name for glyph in font.glyphs if "." in glyph.name[1:]]
    problems = [f"{name}: no feature mentions it" for name in suffixed if name not in words]
    return len(suffixed), problems
```

A glyph called `i.sc` that no feature mentions can't be reached by anybody who types. That was chapter 94's lesson, when a new small cap sat in the font and the feature didn't know. `glyph.name[1:]` skips the first character, so `.notdef` isn't taken for a suffixed glyph.

## Step 3: The mistake

One check that crashes shouldn't stop the other four. Mira knows `try` and `except`, so her loop reads:

```python
for label, check in CHECKS:
    try:
        looked, problems = check(font, package)
    except Exception:
        continue
```

`Exception` is the family that nearly every error belongs to, `ValueError` and `KeyError` and `AttributeError` among them. Catching it catches them all.

Then she mistypes a field name in the Font Info check, `copyrihgt`, and runs:

```text
Glyph names   274 looked at   ok
Unicode       235 looked at   ok
Features       35 looked at   ok
Metrics         8 looked at   ok
5 checks, 0 problems.
Version 1.001: ready for the hand tests.
```

Four lines for five checks, and the word "ready". The Font Info check crashed part way, the loop moved on in silence, and the total stayed at zero. She only notices because she counts the lines.

This is the worst thing a checking script can do. A check that didn't run has told you nothing, and the script reported it as a pass. Chapter 80 asked what silence means. Here it meant a crash.

The repair is to say so, count it in a `broken` total that starts at zero, and refuse to call the font ready:

```python
for label, check in CHECKS:
    try:
        looked, problems = check(font, package)
    except Exception as problem:
        broken += 1
        print(f"{label:<13}DID NOT RUN: {type(problem).__name__}: {problem}")
        continue
```

`type(problem).__name__` is the error's kind as a word, the same word that starts the last line of a traceback. With the typo still in place:

```text
Font Info    DID NOT RUN: AttributeError: 'Info' object has no attribute 'copyrihgt'
Metrics         8 looked at   ok
5 checks, 0 problems, 1 did not run.
Not ready.
```

FontLab's wording after `AttributeError:` will differ from my stand-in's. The first three words of the line won't.

Catching `Exception` is right in this one place, a loop whose job is to keep going and report. Everywhere else, catch the narrow error you expect, as you have since chapter 19. A wide `except` with nothing printed hides your own typos from you.

## The whole script

```python
#FLM: Preflight
# Five read-only checks before a font leaves the building:
# names, Unicode, features, Font Info, metrics. Changes nothing.
import halfmoon
from fly import fl
import fly.ap.core.scripting as scripting

ALLOWED = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._"
TEXT_FIELDS = ["familyName", "openTypeNameDesigner", "copyright", "openTypeNameVersion"]
METRICS = [
    "openTypeOS2TypoAscender", "openTypeOS2TypoDescender", "openTypeOS2TypoLineGap",
    "openTypeHheaAscender", "openTypeHheaDescender", "openTypeHheaLineGap",
    "openTypeOS2WinAscent", "openTypeOS2WinDescent",
]


def check_names(font, package):
    problems = []
    for glyph in font.glyphs:
        name = glyph.name
        if name == ".notdef":
            continue
        bad = [ch for ch in name if ch not in ALLOWED]
        if bad or name[0] in "0123456789.":
            problems.append(f"{name}: not a good glyph name")
    return len(font.glyphs), problems


def check_unicodes(font, package):
    owners = {}
    for glyph in font.glyphs:
        if glyph.unicode is None:
            continue
        if glyph.unicode not in owners:
            owners[glyph.unicode] = []
        owners[glyph.unicode].append(glyph.name)
    problems = []
    for code, names in owners.items():
        if len(names) > 1:
            problems.append(f"U+{code:04X} belongs to {' and '.join(names)}")
    return len(owners), problems


def check_features(font, package):
    blocks = scripting.read_feature_blocks(package)
    text = blocks["prefix"] + " ".join(code for tag, code in blocks["features"])
    for ch in "[];'<>{}":
        text = text.replace(ch, " ")
    words = set(text.split())
    suffixed = [glyph.name for glyph in font.glyphs if "." in glyph.name[1:]]
    problems = [f"{name}: no feature mentions it" for name in suffixed if name not in words]
    tags = [tag for tag, code in blocks["features"]]
    for tag in sorted(set(tags)):
        if tags.count(tag) > 1:
            problems.append(f"{tag}: this tag appears {tags.count(tag)} times")
    return len(suffixed), problems


def check_info(font, package):
    info = package.info
    problems = []
    for key in TEXT_FIELDS:
        if not getattr(info, key):
            problems.append(f"{key} is empty")
    wanted = f"Version {int(info.versionMajor)}.{int(info.versionMinor):03d}"
    if info.openTypeNameVersion != wanted:
        problems.append(f"the numbers say {wanted}, the name says {info.openTypeNameVersion}")
    return len(TEXT_FIELDS) + 1, problems


def check_metrics(font, package):
    seen = {key: set() for key in METRICS}
    original = package.master
    try:
        for master in package.masters:
            package.setMaster(master)
            for key in METRICS:
                seen[key].add(getattr(package.info, key))
    finally:
        package.setMaster(original)
    problems = [f"{key} differs between masters" for key in METRICS if len(seen[key]) > 1]
    return len(METRICS), problems


CHECKS = [
    ("Glyph names", check_names),
    ("Unicode", check_unicodes),
    ("Features", check_features),
    ("Font Info", check_info),
    ("Metrics", check_metrics),
]


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    total = 0
    broken = 0
    for label, check in CHECKS:
        try:
            looked, problems = check(font, package)
        except Exception as problem:
            broken += 1
            print(f"{label:<13}DID NOT RUN: {type(problem).__name__}: {problem}")
            continue
        total += len(problems)
        verdict = f"{len(problems)} problems" if problems else "ok"
        print(f"{label:<13}{looked:>4} looked at   {verdict}")
        for line in problems:
            print("   ", line)
    print(f"{len(CHECKS)} checks, {total} problems, {broken} did not run.")
    if total == 0 and broken == 0:
        print(f"{package.info.openTypeNameVersion}: ready for the hand tests.")
    else:
        print("Not ready.")


main()
```

Save it as `preflight.py`. On a font that has been through the whole part:

```text
Glyph names   274 looked at   ok
Unicode       235 looked at   ok
Features       35 looked at   ok
Font Info       5 looked at   ok
Metrics         8 looked at   ok
5 checks, 0 problems, 0 did not run.
Version 1.001: ready for the hand tests.
```

The 274 are Plum's 205 glyphs, the fifteen suffixed ones from Part 2, the thirty-one Part 3 built, and this part's two ligatures, `fraction` and twenty small figures. The 235 are the glyphs with a character: Plum's 204 and Part 3's thirty-one. The check counts glyphs, so the two extra characters on `space` and `hyphen` don't show. If you closed the practice font without saving at the end of chapter 60, yours says 243 and 204. The 35 are the suffixed glyphs: ten small caps, four alternates, the slashed zero, ten numerators and ten denominators. If you kept `i.sc` from chapter 94, yours says 36.

And on a font with five faults put in, which is the run that shows the script earns its place:

```text
Glyph names   277 looked at   1 problems
    a.sc-old: not a good glyph name
Unicode       236 looked at   ok
Features       38 looked at   3 problems
    a.sc-old: no feature mentions it
    i.sc: no feature mentions it
    mu.alt: no feature mentions it
Font Info       5 looked at   1 problems
    copyright is empty
Metrics         8 looked at   1 problems
    openTypeOS2WinAscent differs between masters
5 checks, 6 problems, 0 did not run.
Not ready.
```

The Unicode line went up by one and stayed `ok`. The planted `mu.alt` carries U+00B5, a character no other glyph in Plum has, so nothing is shared and that check has no complaint. Each line names a chapter's script to reach for: 81 for the name, 89 or 94 for the features, 98 for the copyright, 96 for the metrics.

Notes on the listing.

The Font Info check counts five: four text fields and the version. It compares the version name with the name built from the two numbers, the same `:03d` as chapter 97.

The metrics check puts each master's value into a set per field. A set with more than one member means the masters disagree. The `finally` puts the font back on the master you were looking at, as in chapter 95.

The last line prints the version name. When the typesetter writes back in a month, "ready" will mean something only if you know which file was ready.

## The hand tests

The script says "ready for the hand tests", and it chose those words with care. Python in FontLab can't press Compile and can't set a line of text. A person does these, every time:

1. Open **Window > Panels > Features** and click **Compile**. Read the Output panel.
2. In a Glyph window, type `İSTANBUL` with capital spacing on. The capitals of chapter 91 should stand apart evenly.
3. Type `1/2` and `3/16` with fractions on. Chapter 92's feature text has never been compiled by me, so this is the test I trust least.
4. Type `abcdefgh` with small caps on, then `fi ff ffi`.
5. If you did exercise 3 of chapter 88, look at what you wrote down about Undo.

Then export the font, install it, and set a paragraph in a program that isn't FontLab. Part 6 turns the export into a script. The looking stays with you.

## Break it on purpose

Make a new glyph called `j.sc`, the way you made `i.sc` in chapter 94, and run the pre-flight. You should get `j.sc: no feature mentions it` and `Not ready.` Delete the glyph.

Then change `"copyright"` in `TEXT_FIELDS` to `"copyrihgt"`. You should get the `DID NOT RUN` line. Replace the three lines under `except` with a bare `continue`, run again, and count the lines. Put everything back.

## What the pre-flight doesn't say

It doesn't say the features work. It says they mention the glyphs they should. It doesn't say the names are right, only that they're made of allowed characters. A pass means that nothing a script can see is wrong, which is narrower than "the font is good" and still worth having at four o'clock on a Friday.

Oskar takes the sheet from the first morning off the wall. *The family name and the version in every weight* gets its line through it. Ten of eleven are crossed out. The one left is the Friday export.

## What you learned

Checks that take the same arguments and return the same pair, a count and a list of sentences, can sit in a list and run in one loop. A check that returns its findings can be reused anywhere, and one that prints can't. Catching `Exception` keeps a loop of checks going, but a check that crashed must be printed and counted as "did not run", never passed over as a success. A script can check what's written in a font, and a person still has to compile the features and set real text.

## Try it yourself

1. Add a sixth check: every glyph with a Unicode value has a name that chapter 82's rule would give it. Start with the letters only.
2. Guard the last line of `check_features.py` with `if __name__ == "__main__":` from chapter 33. Now `import check_features` is safe. Call its `check_feature` from the pre-flight for each feature.
3. Write the report to `reports/preflight-<version>.txt` as well as printing it, with chapter 26's file writing. Collect the lines in a list first.

## Next

The font sets real text. It's still a FontLab file on one desk, and the last open line on the sheet says the whole family goes to a dated folder every Friday. Part 6 builds the script that does it.
