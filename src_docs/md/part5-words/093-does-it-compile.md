---
this_file: src_docs/md/part5-words/093-does-it-compile.md
---

# 93. Does it compile?

Wednesday of week eighteen. Oskar's leave ended on Monday. He's back three days a week, the sheet he left is on the wall with nine lines through it, and he hasn't said a word about it. At the coffee machine he tells a story. Two years ago a Friday export stopped with a message about features. Someone had tidied a feature by hand on Thursday evening and lost a semicolon. Nobody found it until Monday, and the fonts went out three days late.

Plum had two features when it came to you. It has eight now, six added by scripts of yours and one rewritten, and none has been through a compiler since you wrote it. Compiling turns feature text into the tables a layout program reads, and the compiler is the only judge of whether the text is valid.

I know of no call that compiles from Python. You do it with the **Compile** button in the Features panel. A script can still do something useful first: it can read the text and catch the cheap mistakes, a missing semicolon, a brace left open, a glyph that isn't in the font. Today you write that script and learn how far to trust it.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py`.
- The eight features the font has after chapter 92: `liga`, `cpsp`, `smcp`, `ss01`, `zero`, `numr`, `dnom`, `frac`.

I couldn't run the code in FontLab 9. I ran the checker in plain Python on Plum's two features plus the text that chapters 88 to 92 produce, and on the broken strings below. I haven't seen FontLab's compiler accept or refuse any of it.

## Step 1: Words

Most of what can be checked comes down to one question: is every word in a rule something the font or the feature language knows? So cut a line into words. Feature code glues punctuation to names, as in `[zero one];` so turn each punctuation mark into a space first. `replace` from chapter 30 does one mark at a time:

```python
PUNCTUATION = "[];<>"


def words_of(code):
    for mark in PUNCTUATION:
        code = code.replace(mark, " ")
    return code.split()


print(words_of("sub f i by fi;"))
print(words_of("pos @cpsp <5 0 10 0>;"))
```

```text
['sub', 'f', 'i', 'by', 'fi']
['pos', '@cpsp', '5', '0', '10', '0']
```

Each word is then one of four things: a word of the language, a number, a class, or a glyph name. The numbers need a test. `isdigit` says whether a string is all digits, and it trips on a minus sign:

```python
print("35".isdigit(), "-35".isdigit())
```

```text
True False
```

Kerning taught you that font numbers are often negative. `lstrip("-")` returns the string without any minus signs at its left end, and then `isdigit` can answer:

```python
def is_number(word):
    return word.lstrip("-").isdigit()
```

## Step 2: Check a line

The checker never stops at the first problem. It collects every problem as a sentence in a list and hands the list back, so one run shows everything that's wrong:

```python
WORDS = {"sub", "by", "from", "pos", "="}


def check_line(code, known, classes):
    problems = []
    words = words_of(code)
    if "=" in words and words[0].startswith("@"):
        classes.add(words[0])
        words = words[1:]
    for word in words:
        if word in WORDS or is_number(word):
            continue
        if word.startswith("@"):
            if word not in classes:
                problems.append(f"class {word} is not defined")
        elif word not in known:
            problems.append(f"no glyph {word}")
    return problems
```

`known` is the set of glyph names in the font. `classes` is the set of class names defined so far. A line that defines a class, such as `@frac_up = [...]`, adds its name to that set before its members are checked. A class has to be defined above the line that uses it, and reading from the top down gets that right without extra work.

## Step 3: The mistake

Mira wraps a loop around `check_line`, runs it over the font, and gets this:

```text
frac line 10: class @frac_up' is not defined
8 features checked, 1 problems.
```

Line 10 of `frac` is the rule with the mark: `sub [fraction @frac_down] @frac_up' by @frac_down;`. The class `@frac_up` is defined, seven lines higher. The checker is looking for a class called `@frac_up'`, with the mark stuck to it, because nobody told `words_of` that `'` is punctuation.

The feature is fine and the checker is wrong. This is worse than it looks. A checker that raises a false alarm gets ignored, and it will be ignored on the day the alarm is real. Add the mark:

```python
PUNCTUATION = "[];'<>"
```

Before you believe a report from a tool you wrote, read the line it complains about.

## Step 4: The shape of a feature

Three more checks look at a feature as a whole. It should open with `feature TAG {` and close with `} TAG;`. Every line of code should end with a semicolon or an opening brace. And the braces should balance, which is counting. A string's `count` method says how many times a piece occurs in it:

```python
opened = 0
for code in ["feature frac {", "lookup a {", "} a;"]:
    opened = opened + code.count("{") - code.count("}")
print(opened)
```

```text
1
```

One brace is still open at the end, so something is missing.

## Step 5: Test the checker

How do you know a checker catches what it should? The font's features are all sound, so running it over the font proves only that it stays quiet. Feed it bad text on purpose. Take the smallest feature and break it four ways. The snippet calls `check_feature`, which is in the whole script below, and `known` is the set of the font's glyph names, as in step 2:

```python
good = "feature zero {\n    sub zero by zero.zero;\n} zero;"
tests = [
    good.replace("zero.zero", "zero.zreo"),
    good.replace("zero.zero;", "zero.zero"),
    good.replace("} zero;", "} zreo;"),
    good.replace("\n} zero;", ""),
]
for text in tests:
    print(check_feature("zero", text, known, set()))
```

```text
[('zero', 2, 'no glyph zero.zreo')]
[('zero', 2, 'no semicolon at the end')]
[('zero', 3, 'should close with: } zero;')]
[('zero', 2, 'should close with: } zero;'), ('zero', 0, "braces don't balance: 1 left open")]
```

Each broken text gets the complaint it deserves, with the line number. `replace` made the breaks, so each test differs from the good text in one place and you can see which. The last one gets two, both true. Keep these four lines in a file of their own. When you change the checker next month, run them again.

## The whole script

```python
#FLM: Check Features
# Reads the feature text and reports what a compiler would trip over.
# Changes nothing. It does not compile: the Features panel does that.
import halfmoon
from fly import fl
import fly.ap.core.scripting as scripting

WORDS = {"sub", "by", "from", "pos", "="}
PUNCTUATION = "[];'<>"


def words_of(code):
    for mark in PUNCTUATION:
        code = code.replace(mark, " ")
    return code.split()


def is_number(word):
    return word.lstrip("-").isdigit()


def check_line(code, known, classes):
    problems = []
    words = words_of(code)
    if "=" in words and words[0].startswith("@"):
        classes.add(words[0])
        words = words[1:]
    for word in words:
        if word in WORDS or is_number(word):
            continue
        if word.startswith("@"):
            if word not in classes:
                problems.append(f"class {word} is not defined")
        elif word not in known:
            problems.append(f"no glyph {word}")
    return problems


def check_feature(tag, text, known, classes):
    classes = set(classes)
    problems = []
    rows = []
    for number, line in enumerate(text.splitlines(), 1):
        code = line.split("#")[0].strip()
        if code:
            rows.append((number, code))
    if not rows:
        return [(tag, 0, "empty")]
    number, code = rows[0]
    if code != "feature " + tag + " {":
        problems.append((tag, number, f"should open with: feature {tag} {{"))
    number, code = rows[-1]
    if code != "} " + tag + ";":
        problems.append((tag, number, f"should close with: }} {tag};"))
    opened = 0
    for number, code in rows:
        opened = opened + code.count("{") - code.count("}")
        if not code.endswith(";") and not code.endswith("{"):
            problems.append((tag, number, "no semicolon at the end"))
        first = code.split()[0]
        if first in ["feature", "lookup"] or first.startswith("}"):
            continue
        for sentence in check_line(code, known, classes):
            problems.append((tag, number, sentence))
    if opened != 0:
        problems.append((tag, 0, f"braces don't balance: {opened} left open"))
    return problems


def prefix_classes(prefix):
    classes = set()
    for line in prefix.splitlines():
        code = line.split("#")[0].strip()
        if code.startswith("@") and "=" in code:
            classes.add(code.split("=")[0].strip())
    return classes


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    known = {glyph.name for glyph in font.glyphs}
    package = scripting.current_package()
    blocks = scripting.read_feature_blocks(package)
    classes = prefix_classes(blocks["prefix"])
    problems = []
    seen = []
    for tag, text in blocks["features"]:
        if tag in seen:
            problems.append((tag, 0, "this tag appears twice"))
        seen.append(tag)
        problems = problems + check_feature(tag, text, known, classes)
    for tag, number, sentence in problems:
        print(f"{tag} line {number}: {sentence}")
    print(f"{len(blocks['features'])} features checked, {len(problems)} problems.")
    if not problems:
        print("Now compile in the Features panel. That is the real test.")


main()
```

Save it as `check_features.py`. On the font as it stands:

```text
8 features checked, 0 problems.
Now compile in the Features panel. That is the real test.
```

Notes on the listing.

A problem is a tuple of three: the tag, the line number, the sentence. The functions that find problems only build the list, and `main` does all the printing. Chapter 100 will want problems from several checkers at once, in a simpler shape, and it can have them because nothing down here prints.

`classes = set(classes)` at the top of `check_feature` makes a copy. The classes from the prefix are visible to every feature. A class defined inside `frac` belongs to `frac`, and the copy keeps `check_line` from adding it to the shared set.

`enumerate(text.splitlines(), 1)` counts from 1. Chapter 78 started its count at 2 to match a spreadsheet, and here 1 matches the first line of a feature as the Features panel shows it. Comment lines and empty lines are skipped but still counted.

A brace in an f-string opens a slot, so to print a brace you write it twice: `{{` and `}}` print one each. Chapter 88 stepped round this with `+`. The line `f"should close with: }} {tag};"` looks odd and is correct.

Line number 0 means "the feature as a whole". It reads a little strangely in the report. Exercise 3 is about that.

## Break it on purpose

Now do Oskar's Thursday evening. Open **Window > Panels > Features**, find `zero`, and delete the semicolon after `zero.zero`. Run the script:

```text
zero line 2: no semicolon at the end
8 features checked, 1 problems.
```

Don't repair it yet. Click the panel's **Compile** button and read what FontLab says in the Output panel. I can't tell you the words, because I haven't seen them. Write them down next to the checker's sentence. Does the compiler name the feature? The line? Is its line number counted within the feature or from the top of all the feature text?

Put the semicolon back, run the script, compile again. You now know what both judges say about the same mistake, and you'll recognize the compiler's message when it comes on a Friday.

## What the checker can't know

The checker knows five words of a language that has dozens. Feature code also has `ignore`, `lookupflag`, `script`, `language`, `include` and more. Put `script latn;` into a feature and this script will say `no glyph script` and `no glyph latn`, two false alarms of the kind step 3 warned about. When you start using a new word, add it to `WORDS` before you run the check, and add a test string to step 5's list.

It's also blind in the other direction. `sub a b by c d;` passes every check here, with all its glyphs present and a semicolon at the end, and I'd expect a compiler to refuse it, since a rule can't replace two glyphs by two. The checker reads words and doesn't know the grammar.

So a clean report means that none of the cheap mistakes are there. It doesn't mean the features compile, which is why the last line the script prints sends you to the button.

## What you learned

A check that collects every problem in a list, as data, can report them all at once and can be reused by another script. To test a checker, feed it text you broke on purpose and see that each break gets its own complaint. A false alarm is a bug in the checker, and it costs trust, so read the line before you believe the report. `replace` in a loop turns punctuation into spaces, `count` counts pieces of a string, and `lstrip("-")` lets `isdigit` cope with negative numbers.

## Try it yourself

1. Add a fifth broken text to step 5: a rule that uses `@figs`, which nobody defined. What does the checker say, and on which line?
2. `liga` needs its long rules before its short ones, as chapter 90 explained. Write `check_order(text)` that returns a problem when a `sub` rule with fewer glyphs before `by` stands above one with more. Test it on a string with the two rules in the wrong order.
3. Change the printing in `main` so that a problem with line number 0 prints as `zero: empty`, without the words "line 0". One `if` will do it.

## Next

The features are written and checked. Which glyphs do they reach? The font has ten small caps and eighty-four lowercase letters, and a reader who switches small caps on will see the difference. Chapter 94 counts what each feature covers and what it leaves out.
