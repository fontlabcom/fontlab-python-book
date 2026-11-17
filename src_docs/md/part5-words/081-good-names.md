---
this_file: src_docs/md/part5-words/081-good-names.md
---

# 81. Good names

Monday of week sixteen. The typesetter's mail about the headings is an hour old when a second one arrives, from the same publisher and a different desk. Their production system has turned back Friday's test fonts. It quotes one glyph name, `uni0041.alt2 copy`, and says nothing else.

Ines knows where the name came from. Somebody duplicated an alternate `A` in the real Plum to try an idea, FontLab called the duplicate "copy", and nobody tidied up. She sends Mira a short list of other names she doesn't trust and asks for something that checks all of them, and the font's own, before the next export.

A glyph name is a string. This chapter is about asking a string what it is made of.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The `tell` function from [chapter 39](../part2-a-toolbox/039-ask-the-user.md). The script below defines it again, so it runs by itself.

I couldn't run the code in FontLab 9. The outputs below were computed in plain Python. I haven't seen which names FontLab itself refuses when you type them into the Font window, or what an export says about a bad one, so this chapter claims nothing about either.

## Step 1: What a name may contain

The rules for glyph names are older than FontLab and most font tools agree on them. A name is made of the letters `A` to `Z` and `a` to `z`, the digits, the period and the underscore. It doesn't start with a digit. It is at most 63 characters long. `.notdef` is the one name that starts with a period.

The period and the underscore each have a job. A period separates a glyph's base name from a suffix that says which variant it is: `a.sc`, `zero.alt`. An underscore joins the parts of a ligature: `f_i`. Chapters 89 and 90 build features from these two marks and no others, which is one reason to keep them clean now.

A space breaks the rules, and so does a hyphen. So does `ñ` as a name, though it looks harmless: the letter is called `ntilde`.

Fly's own rename tool allows the hyphen. Fonts that go to print shops and web servers shouldn't have it, so Mira's rule leaves it out.

## Step 2: Ask the whole string

In chapter 13 you asked a string `isupper()`. Strings answer other questions of that kind. One of them sounds like what you need: `isalnum()` is true when every character is a letter or a digit.

```python
for name in ["Aacute", "a.sc", "3quarters", "ñ"]:
    print(name, name.isalnum())
```

```text
Aacute True
a.sc False
3quarters True
ñ True
```

Three of the four answers are wrong for our purpose. `a.sc` is a good name and gets `False`, because a period is neither letter nor digit. `3quarters` is a bad name and gets `True`. And `ñ` gets `True`, because to Python it is a letter. Python knows the alphabets of the world. Glyph names know one.

A ready-made question answers what its author meant by it. Before you lean on one, try it on the cases you care about, good and bad.

## Step 3: Ask each character

So write the alphabet down yourself. A string can serve as a set of allowed characters, since `in` works on strings character by character:

```python
LOWER = "abcdefghijklmnopqrstuvwxyz"
DIGITS = "0123456789"
ALLOWED = LOWER + LOWER.upper() + DIGITS + "._"

print(len(ALLOWED))
print("a" in ALLOWED, " " in ALLOWED, "ñ" in ALLOWED)
```

```text
64
True False False
```

Twenty-six small letters, twenty-six capitals, ten digits, two marks. Now collect the characters of a name that aren't in it. This is a comprehension with a condition, as in chapter 37, looping over a string as chapter 9 did:

```python
def strays(text, allowed):
    return [ch for ch in text if ch not in allowed]


print(strays("a.sc", ALLOWED))
print(strays("uni0041.alt2 copy", ALLOWED))
print(strays("germandbls-old", ALLOWED))
```

```text
[]
[' ']
['-']
```

The function returns the offenders, not `True` or `False`. An empty list means the name is clean, and a list with something in it tells you what to look for. That matters with a space. `[' ']` shows it between quotes, where you can see it. Printed bare, a space at the end of a name is invisible.

`strays` takes the allowed characters as a parameter, so it can serve again with a different alphabet. It will, in step 5.

## Step 4: The rules about position

The alphabet isn't the whole rule. Three more checks look at where a character stands, and each is one line with tools you have:

```python
name = "3quarters"
print(name[0] in DIGITS)

name = "a.sc."
print(name[-1] == ".")

name = "e..sc"
print(".." in name)
```

```text
True
True
True
```

`name[0]` is the first character and `name[-1]` the last. The square brackets you used on lists in chapter 10 work the same way on strings. `".." in name` asks whether two periods stand side by side anywhere: `in` on strings finds a run of characters, not only a single one. Neither `a.sc.` nor `e..sc` has a stray character. Both are typing slips that leave an empty piece where a suffix should be.

Put together, with the same shape as the checks in chapter 80: one name in, a list of plain sentences out.

```python
def name_problems(name):
    if name in SPECIAL:
        return []
    problems = []
    if len(name) > LONGEST:
        problems.append(f"is {len(name)} characters long, the limit is {LONGEST}")
    if name[0] in DIGITS:
        problems.append("starts with a digit")
    if name[0] == "." or name[-1] == ".":
        problems.append("starts or ends with a period")
    if ".." in name:
        problems.append("has two periods in a row")
    bad = strays(name, ALLOWED)
    if bad:
        problems.append(f"has characters that aren't allowed: {bad}")
    return problems
```

`SPECIAL` holds `.notdef`, which is let through before any rule can object to its period. Every `if` stands alone, with no `elif`, because one name can break several rules and the report should list them all.

## Step 5: Two kinds of good name

`uni0041.alt2 copy` has a second oddity, apart from its space. Its base says `uni0041` where you'd expect `A`.

Both are legal. `A` and `Aacute` are friendly names, the ones people read. `uni0041` and `uni00C1` say the same thing by code point: `uni` and then four hex digits, in capitals. You met hex in chapter 6. Programs can work out the character from such a name without a table, which is why exported fonts often carry them, and they are called production names. FontLab can show you friendly names while you work and write production names on export. I haven't found a call in Fly that translates one into the other, so this book doesn't use one.

In a working file a `uni` name is usually a glyph that came in from somewhere else and hasn't been given its friendly name. That's worth a note in the report, not a complaint. Recognising one takes `split` from chapter 9 to cut the suffix off, and `strays` again with a different alphabet:

```python
HEX = DIGITS + "ABCDEF"


def is_uni_name(name):
    base = name.split(".")[0]
    if not base.startswith("uni") or len(base) != 7:
        return False
    return not strays(base[3:], HEX)


for name in ["uni00C1", "uni00C1.sc", "unicorn", "uni00c1"]:
    print(name, is_uni_name(name))
```

```text
uni00C1 True
uni00C1.sc True
unicorn False
uni00c1 False
```

`base[3:]` is a slice, as on a list: everything after the first three characters. `not strays(...)` is true when the list is empty. `unicorn` has the right length and the wrong digits. `uni00c1` has small letters where the rule wants capitals, and tools that read production names won't recognise it. Chapter 82 turns names like these into friendly ones.

## The whole script

```python
#FLM: Name Check
# Checks every glyph name in the font, and any names pasted into EXTRA,
# against the naming rules. Changes nothing.
from fly import fl, qt
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


EXTRA = [
    "uni0041.alt2 copy", "3quarters", "e..sc", "ñ",
    "germandbls-old", "a.sc.", "uni00C1", "A.alt2",
]

LOWER = "abcdefghijklmnopqrstuvwxyz"
DIGITS = "0123456789"
ALLOWED = LOWER + LOWER.upper() + DIGITS + "._"
HEX = DIGITS + "ABCDEF"
LONGEST = 63
SPECIAL = [".notdef"]


def strays(text, allowed):
    return [ch for ch in text if ch not in allowed]


def is_uni_name(name):
    base = name.split(".")[0]
    if not base.startswith("uni") or len(base) != 7:
        return False
    return not strays(base[3:], HEX)


def name_problems(name):
    if name in SPECIAL:
        return []
    problems = []
    if len(name) > LONGEST:
        problems.append(f"is {len(name)} characters long, the limit is {LONGEST}")
    if name[0] in DIGITS:
        problems.append("starts with a digit")
    if name[0] == "." or name[-1] == ".":
        problems.append("starts or ends with a period")
    if ".." in name:
        problems.append("has two periods in a row")
    bad = strays(name, ALLOWED)
    if bad:
        problems.append(f"has characters that aren't allowed: {bad}")
    return problems


def report(label, names):
    count = 0
    for name in names:
        for problem in name_problems(name):
            count = count + 1
            print(f"  {name!r} {problem}")
    print(f"{label}: {len(names)} names, {count} problems")
    coded = [name for name in names if is_uni_name(name)]
    if coded:
        print(f"  named by code point: {coded}")


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    report("font", [glyph.name for glyph in font.glyphs])
    if EXTRA:
        report("pasted list", EXTRA)


main()
```

Save it as `name_check.py`. With Ines's eight names in `EXTRA`, it should print:

```text
font: 251 names, 0 problems
  'uni0041.alt2 copy' has characters that aren't allowed: [' ']
  '3quarters' starts with a digit
  'e..sc' has two periods in a row
  'ñ' has characters that aren't allowed: ['ñ']
  'germandbls-old' has characters that aren't allowed: ['-']
  'a.sc.' starts or ends with a period
pasted list: 8 names, 6 problems
  named by code point: ['uni0041.alt2 copy', 'uni00C1']
```

The 251 is Plum's 205 glyphs, the fifteen you added in Part 2 and the thirty-one from Part 3. Your count depends on the exercises you did and saved. The zero is the part that should match: every glyph in the practice font was named by Plum's designer or by a script of yours that added a clean suffix.

Notes on the listing.

`{name!r}` is chapter 78's way of printing a text with its quotes. For a name that might end in a space, the quotes show where it stops.

`report` is called twice with a label and a list, once for the font and once for the pasted names. It neither knows nor cares where a list came from.

The font line prints even when there's nothing to report. Chapter 80 gave the reason: a check that stays silent when it passes can't be told from a check that never ran.

Empty `EXTRA` when you've dealt with its names. `if EXTRA:` then skips the second report.

## Break it on purpose

Take `SPECIAL` out of `name_problems` by making it an empty list, and run again. The font line should now say `1 problems`, with `'.notdef' starts or ends with a period` above it. The rule was written by people who also wrote its one exception, and a checker has to carry both. Put `.notdef` back.

## What the check doesn't say

A name can pass every rule here and still be wrong. `Aacute` on a glyph that draws a `B` is a good name. So is `a.sc` in a font where the other small caps end in `.smcp`. The script checks spelling. Whether a name is true, and whether the names agree with each other, takes the chapters that follow.

Mira runs it on the real Plum. Six lines, and she renames those glyphs by hand in the Font window, which for six is quicker than writing anything. Ines's reply is one line: "And the three hundred from the Greek import?"

## What you learned

A ready-made string question such as `isalnum` answers its author's idea of a letter, so test it on your own cases first. A string of allowed characters with `in` gives you an alphabet you control, and returning the offending characters is more use than returning `False`. `name[0]`, `name[-1]` and `".." in name` check position. Glyph names come in two kinds, friendly and production, and both are legal.

## Try it yourself

1. Add a rule: a name that contains `copy` gets the sentence `looks like a leftover duplicate`. Which of Ines's eight names should now have two problems?
2. Make a name of 64 characters with `"a" * 64` and pass it to `name_problems`. Then try 63.
3. `is_uni_name` rejects `uni00c1`. Write `is_sloppy_uni(name)` that is true for a `uni` name whose hex digits include small letters. You'll need a third alphabet.

## Next

Three hundred glyphs came in from another file with names like `glyph123`, each with its Unicode value intact. Chapter 82 gives them names from a lookup table, and a script renames glyphs again, which it last did in Part 2.
