---
this_file: src_docs/md/part5-words/087-what-features-do.md
---

# 87. What features does this font have?

Tuesday of week seventeen. The cookbook's typesetter wants small caps in the chapter openings and asks which OpenType features Plum has. Ines says "ligatures, I think" and looks at Mira. Mira looks at Oskar's chair.

A font's features are a text. Somebody wrote it, or a program did, and FontLab keeps it with the font. You can read it in the Features panel. Today a script reads it, because a script can count what it reads and Ines wants a summary she can paste into an email.

It's also the first step toward writing features, which starts tomorrow. Nobody should write into a text they haven't read.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The `tell` function from [chapter 39](../part2-a-toolbox/039-ask-the-user.md). The script below defines it again, so it runs by itself.

I couldn't run the code in FontLab 9. I ran the text handling in plain Python on the feature text stored in Plum's source file, and the output below comes from that. I'm assuming Fly's reader hands back that same text, wrapper lines included. If your first printout looks different from mine, trust yours and adjust the tests in Step 4.

This chapter changes nothing in the font.

## Step 1: Get the text

Fly reads the features in one call:

```python
from fly import fl
import fly.ap.core.scripting as scripting

package = scripting.current_package()
blocks = scripting.read_feature_blocks(package)
print(list(blocks))
print(len(blocks["prefix"]))
print(len(blocks["features"]))
```

```text
['prefix', 'features']
916
2
```

`scripting.current_package()` is the way in that you used for kerning in chapter 69. `blocks` is a dictionary with two keys. `prefix` is one string of 916 characters: the part of the feature text that comes before any feature and serves them all. `features` has two items.

## Step 2: The mistake

Plum has a `liga` feature. `blocks["features"]` sounds like a dictionary from tag to text, so ask for it by tag:

```python
print(blocks["features"]["liga"])
```

```text
TypeError: list indices must be integers or slices, not str
```

Read the complaint from the left. "List indices": Python is telling you that `blocks["features"]` is a list. A list wants a position, a whole number, and you handed it a word.

Look at what the list holds:

```python
for tag, code in blocks["features"]:
    print(tag, len(code))
```

```text
liga 106
cpsp 93
```

It's a list of pairs, tag and text. There's a reason it's a list. Features apply in the order they're written, so the order is part of the data, and a list is the type whose business is order.

When you want to look one up by tag, turn the pairs into a dictionary. `dict` takes a list of pairs and makes each pair an entry:

```python
by_tag = dict(blocks["features"])
code = by_tag["liga"]
```

Chapter 82 turned a dictionary round. This turns a list of pairs into one. Keep the list for walking through in order and the dictionary for asking by name.

## Step 3: One string, many lines

Print the `liga` text:

```python
print(code)
```

```text
feature liga {
# GSUB feature: Standard Ligatures
# Lookups: 1

  sub f i by fi;
  sub f l by fl;
} liga;
```

Seven lines on screen. To Python it's still one string, 106 characters long. The line breaks are characters in it, the `\n` you met at the end of every line in chapter 26. Loop over the string and you'd get `f`, `e`, `a`, one character at a time.

To work line by line, cut the string at its line breaks:

```python
lines = code.splitlines()
print(len(lines))
print(lines[4])
```

```text
7
  sub f i by fi;
```

`splitlines` returns a list of strings, one for each line, with the breaks removed. A file gave you its lines one at a time in a loop. A string in memory gives them all at once with this method. After that the work is the same.

## Step 4: Which lines are rules?

Of the seven lines, two do something. `sub f i by fi;` says: where `f` is followed by `i`, substitute the glyph `fi`. The rest is packaging. The first and last lines open and close the feature. Lines that start with `#` are comments, and one line is empty.

Comments in feature text start with `#`, the same sign Python uses, and can also follow code on a line. The prefix has one of those:

```text
languagesystem DFLT dflt; # Default default
```

One cut handles both cases. Split the line at `#` and keep the first piece:

```python
print("languagesystem DFLT dflt; # Default default".split("#")[0].strip())
print([" # Lookups: 1".split("#")[0].strip()])
```

```text
languagesystem DFLT dflt;
['']
```

A line with a trailing comment keeps its code. A line that's nothing but a comment becomes an empty string, and you already skip those. So:

```python
def rule_lines(code):
    rules = []
    for line in code.splitlines():
        line = line.split("#")[0].strip()
        if line == "" or line.startswith("feature") or line.startswith("}"):
            continue
        rules.append(line)
    return rules


print(rule_lines(code))
```

```text
['sub f i by fi;', 'sub f l by fl;']
```

This is a filter made of four plain tests, and it will be wrong about feature text more elaborate than Plum's. A glyph name can't contain `#`, so that cut is safe. But a feature may hold named groups of rules called lookups, with their own opening and closing lines, and this function would count the opening line as a rule. For a first look at a small font it does the job. I'll say more under "What the summary leaves out".

## Step 5: What kind of rules?

The first word of a rule says what it does. `sub` substitutes one glyph or several for others. `pos` moves glyphs or changes their spacing. Count the first words with the tally from chapter 22:

```python
def tally_words(rules):
    tally = {}
    for rule in rules:
        word = rule.split()[0]
        tally[word] = tally.get(word, 0) + 1
    return tally
```

`split()` with nothing in the parentheses cuts at any run of spaces, so `[0]` is the first word.

The prefix needs a different look. It holds two kinds of code line. A line that starts with `@` defines a class, a named list of glyphs in square brackets. The others are declarations such as `languagesystem`. For a class, the summary should give the name and the size, not sixty-three glyph names:

```python
rule = "@cpsp = [A B C];"
name = rule.split("=")[0].strip()
members = rule.split("[")[1].split("]")[0].split()
print(name, len(members))
```

```text
@cpsp 3
```

The middle line is three splits in a row. Cut at `[` and take what follows. Cut that at `]` and take what precedes. Cut the result at spaces. Each split works on what the one before handed over, left to right.

Run the whole script:

```text
Prefix: 37 lines, 3 of them code
  class @cpsp: 63 glyphs
  languagesystem DFLT dflt;
  languagesystem latn dflt;
liga  7 lines, 2 rules: 2 replace
      sub f i by fi;
      sub f l by fl;
cpsp  6 lines, 1 rules: 1 move
      pos @cpsp <5 0 10 0>;
```

That's all of it. Plum has two features. `liga` swaps in the two ligatures. `cpsp`, capital spacing, adds a little room around each of 63 capitals when a typesetter asks for it: that's what the four numbers in angle brackets do to the class `@cpsp`. There are no small caps. Mira writes the typesetter one line, and Ines adds "yet".

## Step 6: Comments can be wrong

Thirty-four of the prefix's 37 lines aren't code. Print them and read:

```python
for line in blocks["prefix"].splitlines():
    if line.startswith("# G") or line.startswith("# Font"):
        print(line)
```

```text
# Generated on: 2021-6-16 4:23
# Generated by: FontLab 7.1.5
# Font PostScript name: Vegur-Regular
# GSUB lookups: 1
# GSUB features: 1 (liga)
# GPOS lookups: 2
# GPOS features: 2 (cpsp, kern)
```

A program wrote this header in 2021, and the name in it is `Vegur-Regular`, which isn't this font's name. It lists three features. The text below it has two: there's no `kern` block. As far as I know FontLab builds that one from the kerning table at export, so it needn't be written here.

The header was true once. Nothing kept it true. Your script counted what's there, and the comment reports what a program saw in 2021. When the two disagree, believe the count. The same goes for comments in your own scripts, which is a reason to keep them few.

## The whole script

```python
#FLM: List Features
# Prints a summary of the font's feature text: classes and declarations
# in the prefix, then each feature with its rules. Changes nothing.
from fly import fl, qt
import fly.ap.core.scripting as scripting
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


MEANING = {"sub": "replace", "pos": "move"}
SHOW_RULES = True


def rule_lines(code):
    rules = []
    for line in code.splitlines():
        line = line.split("#")[0].strip()
        if line == "" or line.startswith("feature") or line.startswith("}"):
            continue
        rules.append(line)
    return rules


def tally_words(rules):
    tally = {}
    for rule in rules:
        word = rule.split()[0]
        tally[word] = tally.get(word, 0) + 1
    return tally


def show_prefix(prefix):
    rules = rule_lines(prefix)
    print(f"Prefix: {len(prefix.splitlines())} lines, {len(rules)} of them code")
    for rule in rules:
        if rule.startswith("@"):
            name = rule.split("=")[0].strip()
            members = rule.split("[")[1].split("]")[0].split()
            print(f"  class {name}: {len(members)} glyphs")
        else:
            print(f"  {rule}")


def show_feature(tag, code):
    rules = rule_lines(code)
    parts = []
    for word, count in tally_words(rules).items():
        parts.append(f"{count} {MEANING.get(word, word)}")
    print(f"{tag}  {len(code.splitlines())} lines, {len(rules)} rules: {', '.join(parts)}")
    if SHOW_RULES:
        for rule in rules:
            print(f"      {rule}")


def main():
    if fl.CurrentFont() is None:
        tell("Open a font first.")
        return
    package = scripting.current_package()
    blocks = scripting.read_feature_blocks(package)
    show_prefix(blocks["prefix"])
    for tag, code in blocks["features"]:
        show_feature(tag, code)
    if not blocks["features"]:
        print("No features.")


main()
```

Save it as `list_features.py`.

Notes on the listing.

`MEANING.get(word, word)` looks a word up and, when it isn't in the table, gives the word back unchanged. An unknown first word then prints as itself, and the summary still makes sense.

`SHOW_RULES` is for bigger fonts. A feature with four hundred substitutions shouldn't print four hundred lines into a summary. Set it to `False` and you get one line for each feature.

`rule_lines` serves both the prefix and the features. The prefix has no `feature` or `}` lines, so those two tests never fire there and do no harm.

## Break it on purpose

A class definition may run over several lines. People write them that way when the list is long. Try the function on one, with no font involved:

```python
text = "@caps = [A B C\n  D E F];\n"
print(rule_lines(text))
```

```text
['@caps = [A B C', 'D E F];']
```

Two "rules" from one definition. `show_prefix` would then report a class of three glyphs and print `D E F];` as a declaration. The function assumes one statement to a line, and feature text doesn't have to keep to that. What ends a statement is the semicolon.

A sturdier reader would join the whole text and cut at `;`. Exercise 3 asks for it.

## What the summary leaves out

The script reads feature text as lines of words. It doesn't understand the language. It can't tell you whether a rule is valid, whether the glyphs it names exist, or what the font does when a feature is switched on. Lookups, language-specific sections and contextual rules, the ones with a `'` after a glyph name, pass through as lines beginning with whatever word they begin with.

Chapter 91 checks glyph names in classes against the font. Chapter 93 looks at what can be checked short of compiling. For anything past that there's the Features panel, where FontLab reads the text with a real parser and tells you what it thinks.

## What you learned

A long text is one string with line-break characters in it, and `splitlines` turns it into a list you can loop over. A list of pairs keeps order and `dict` turns it into a lookup when you need one. Chained splits take a line apart from the outside in. A comment says what its author believed when they wrote it, and code that counts says what's there now.

## Try it yourself

1. Add `"languagesystem"` handling to `show_prefix`: collect the script tags, the second word of each such line, into a list and print one line, `scripts: DFLT latn`, in place of the two declarations.
2. The grammar of the summary is off: `1 rules`. Write `plural(count, word)` that returns `1 rule` or `2 rules` and use it in both places. Then decide what it should do with `0`.
3. Write `statements(code)` that removes comments line by line as `rule_lines` does, joins what's left with spaces, and cuts at `;`. Drop empty pieces. Test it on the two-line class above: you should get one statement. What happens to the `feature liga {` line now, and how would you take it out?

## Next

The typesetter wants small caps and Plum has no feature for them. Chapter 88 writes one, from the list of `.sc` glyphs you already have.
