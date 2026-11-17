---
this_file: src_docs/md/part5-words/089-features-from-suffixes.md
---

# 89. Features from suffixes

Thursday of week seventeen. The small caps work in the typesetter's test file, and she has already asked what else there is. There's plenty. Ines's Plum has glyphs ending in `.sc`, `.alt`, `.ss01`, `.tf`, `.onum` and `.case`, and each suffix wants a feature of its own.

Mira starts the obvious way. She opens `make_smcp.py`, changes `TAG` and `SUFFIX`, runs it, changes them again. On the third round she types `onum` in one constant and forgets the other, and writes old-style figures into the `tnum` feature.

A pair of constants you edit six times is a table that hasn't been written down yet. Today you write it down.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- Your suffixed glyphs from Part 2: ten ending in `.sc`, four in `.ss01` (`a`, `g`, `y`, `ampersand`), and `zero.alt`.
- `rename_suffix.py` from chapter 31. The script below defines `tell` and `ask` from [chapter 39](../part2-a-toolbox/039-ask-the-user.md) again, so it runs by itself.
- The `smcp` feature from chapter 88. If you skipped the write there, today's script adds it.

I couldn't run the code in FontLab 9. I ran the counting and the text building in plain Python on Plum's glyph names plus those fifteen. The write is the one from chapter 88, and I haven't seen it work.

## Step 1: Which suffixes are there?

Before a table of suffixes, a list of the ones the font has. The suffix is what follows the first period in a name. `split(".", 1)` cuts at the first period only, as it cut at the first colon in chapter 85, and the tally is the one from chapter 22:

```python
from fly import fl

font = fl.CurrentFont()
names = [glyph.name for glyph in font.glyphs]
tally = {}
for name in names:
    if "." in name:
        suffix = name.split(".", 1)[1]
        tally[suffix] = tally.get(suffix, 0) + 1
print(tally)
```

```text
{'notdef': 1, 'sc': 10, 'ss01': 4, 'alt': 1}
```

## Step 2: The mistake

Three of those are suffixes. The first isn't. `.notdef` is a whole name that happens to start with a period, and the split did what you asked:

```python
print(".notdef".split(".", 1))
```

```text
['', 'notdef']
```

An empty base and a "suffix" of `notdef`. There was no error and nothing looked broken. If the next step had been a feature, the script would have gone looking for a tag for `notdef`.

This kind of mistake is the reason to print a tally before you build on it. Four entries are few enough to read, and you know your font well enough to see which one doesn't belong. The mend is a second condition:

```python
def suffixes(names):
    tally = {}
    for name in names:
        if "." in name and not name.startswith("."):
            suffix = name.split(".", 1)[1]
            tally[suffix] = tally.get(suffix, 0) + 1
    return tally


print(suffixes(names))
```

```text
{'sc': 10, 'ss01': 4, 'alt': 1}
```

## Step 3: The table

A dictionary from suffix to feature tag:

```python
TAGS = {"sc": "smcp", "ss01": "ss01"}
```

The suffix is the studio's habit. The tag is fixed by the OpenType specification. `ss01` happens to be both, which is why the alternates were renamed in chapter 31. For `sc` the two differ, and only the table knows that they belong together.

Walk the tally and look each suffix up:

```python
for suffix in suffixes(names):
    print(suffix, TAGS[suffix])
```

```text
sc smcp
ss01 ss01
KeyError: 'alt'
```

The font has a suffix the table doesn't. You met `KeyError` in chapter 21. Here it would be a poor way to stop, because a font will always have a stray suffix or two, and the script should say so and carry on with the rest:

```python
for suffix, count in suffixes(names).items():
    if suffix not in TAGS:
        print(f".{suffix:<6}{count:>3}  no tag in the table, skipped")
        continue
    print(f".{suffix:<6}{count:>3}  {TAGS[suffix]}")
```

```text
.sc     10  smcp
.ss01    4  ss01
.alt     1  no tag in the table, skipped
```

A skipped line in a report is a question for a person. Here the person is you.

## Step 4: What is `zero.alt`?

Fly has an opinion on the question. It carries a table like yours, a much longer one:

```python
from fly.ap.features.identity_tools.feature_explorer.suffix_report import suggested_tag

for suffix in suffixes(names):
    print(suffix, suggested_tag(suffix))
```

```text
sc smcp
ss01 ss01
alt salt
```

It agrees with you twice and suggests `salt`, stylistic alternates, for `alt`. That's a fair guess from the name. It's what the function answers for any suffix it doesn't know, too, so it is a guess and no more.

You know something the function doesn't. Chapter 31 left `zero.alt` out of the renaming because it's the slashed zero, and OpenType has a feature for that glyph alone, called `zero`. The suffix says "alternate". The glyph is something more particular.

You could add `"alt": "zero"` to the table. That would be true today and false the day someone draws `q.alt`. The better mend is in the font: give the glyph a name that says what it is. Open `rename_suffix.py`, set `NEW_SUFFIX = ".zero"`, empty the `SKIP` set, do the dry run, read the one line, and then do it for real. Put `NEW_SUFFIX` and `SKIP` back afterward. Then add the entry the name has earned:

```python
TAGS = {"sc": "smcp", "ss01": "ss01", "zero": "zero"}
```

So the table is yours, and Fly's function is a second opinion to ask when you meet a suffix you didn't invent. The script uses your table because your table holds what the studio decided.

## Step 5: One write for all of them

For each suffix in the table you make the pairs and the text as in chapter 88. All the new features then go into the font in a single write. One write is one step to undo, and the font is never left with half the set.

The new features replace old ones with the same tags and leave the others alone:

```python
new_tags = [tag for tag, text in made]
kept = [(tag, code) for tag, code in blocks["features"] if tag not in new_tags]
updated = {"prefix": blocks["prefix"], "features": kept + made}
```

Chapter 88 filtered on one tag with `!=`. With a list of tags the test becomes `not in`. Nothing else changes.

## The whole script

```python
#FLM: Features From Suffixes
# Writes or replaces one feature for each suffix in TAGS.
# Does not compile: do that in the Features panel afterward.
from fly import fl, qt
import fly.ap.core.scripting as scripting
import fly.ap.features.code as fea_code
from fly.ap.ui.dialogs import run_standard_message_box

TITLE = "Halfmoon"


def tell(text):
    box = qt.QtGui.QMessageBox
    run_standard_message_box(qt, fl.MainWindow(), TITLE, text, "Information", box.Ok)


def ask(question):
    box = qt.QtGui.QMessageBox
    answer = run_standard_message_box(
        qt, fl.MainWindow(), TITLE, question, "Question", box.Yes | box.No
    )
    return answer == box.Yes


TAGS = {"sc": "smcp", "ss01": "ss01", "zero": "zero"}
DRY_RUN = True


def suffixes(names):
    tally = {}
    for name in names:
        if "." in name and not name.startswith("."):
            suffix = name.split(".", 1)[1]
            tally[suffix] = tally.get(suffix, 0) + 1
    return tally


def plan(names, tags):
    made = []
    used = []
    for suffix, count in suffixes(names).items():
        if suffix not in tags:
            print(f".{suffix:<6}{count:>3}  no tag in the table, skipped")
            continue
        tag = tags[suffix]
        if tag in [done for done, text in made]:
            print(f".{suffix:<6}{count:>3}  {tag} is already made, skipped")
            continue
        pairs = fea_code.suffix_pairs(names, suffix)
        print(f".{suffix:<6}{count:>3}  {tag}  {len(pairs)} paired")
        if pairs:
            made.append((tag, fea_code.feature_text(tag, pairs)))
            used = used + [name for pair in pairs for name in pair]
    return made, used


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    names = [glyph.name for glyph in font.glyphs]
    made, used = plan(names, TAGS)
    if not made:
        print("Nothing to write.")
        return

    package = scripting.current_package()
    blocks = scripting.read_feature_blocks(package)
    new_tags = [tag for tag, text in made]
    kept = [(tag, code) for tag, code in blocks["features"] if tag not in new_tags]
    print(f"{len(made)} features to write: {' '.join(new_tags)}")
    print(f"{len(kept)} features kept: {' '.join(tag for tag, code in kept)}")

    if DRY_RUN:
        print("Dry run. Nothing written.")
        return
    if not ask(f"Write {len(made)} features?"):
        return
    updated = {"prefix": blocks["prefix"], "features": kept + made}
    result = scripting.write_feature_blocks(
        package, blocks, updated,
        references=used, undo_name="Write features from suffixes")
    print(result)
    print("Now compile in the Features panel.")


main()
```

Save it as `features_from_suffixes.py`. The dry run:

```text
.sc     10  smcp  10 paired
.ss01    4  ss01  4 paired
.zero    1  zero  1 paired
3 features to write: smcp ss01 zero
2 features kept: liga cpsp
Dry run. Nothing written.
```

After the real run, `list_features.py` shows the two new ones behind `smcp`:

```text
ss01  6 lines, 4 rules: 4 replace
      sub a by a.ss01;
      sub ampersand by ampersand.ss01;
      sub g by g.ss01;
      sub y by y.ss01;
zero  3 lines, 1 rules: 1 replace
      sub zero by zero.zero;
```

Notes on the listing.

`plan` prints as it goes and returns two things, the features and the glyph names they mention. Printing inside the function that decides keeps each reason next to its decision.

The two numbers on a line can differ. The first counts glyphs with the suffix, the second counts those whose base glyph exists. `.sc  11  smcp  10 paired` means one small cap has nothing to replace, and you'd go and find out which.

`' '.join(tag for tag, code in kept)` has a comprehension without its square brackets. Inside the parentheses of a call you may leave them off.

`smcp` moved. It's written again from the glyphs, as it would have to be the day Ines adds `i.sc`, and it now sits after `cpsp` with the other new ones.

Mira's run on the real Plum is longer. Her table has six entries, with `"tf": "tnum"` and `"onum": "onum"` for the two extra sets of figures and `"case": "case"` for the punctuation that sits higher between capitals. The dry run prints six lines and one surprise: `.sc  60  smcp  59 paired`. Somebody drew `germandbls.sc`, and the base glyph in that file is still called `uni00DF`. Chapter 82's script mends the base name, and the second dry run says 60.

## Break it on purpose

Change the table so that two suffixes claim one tag: `"zero": "ss01"`. Dry run:

```text
.sc     10  smcp  10 paired
.ss01    4  ss01  4 paired
.zero    1  ss01 is already made, skipped
2 features to write: smcp ss01
```

A tag may appear once in a font's features. Without the check in `plan`, the script would hand Fly two `ss01` blocks and Fly would refuse the lot, small caps included. With it, one line tells you which table entry to look at. Put `"zero": "zero"` back.

If you want two suffixes in one feature, say `.alt` and `.ss01` both under `ss01`, the rules have to be merged into one block. Exercise 3.

## What the table can't know

Order. Features apply in the order they're written, and two of yours touch the same letters. With `ss01` and small caps both on, `a` meets `smcp` first and becomes `a.sc`. The `ss01` rule looks for `a`, finds `a.sc`, and does nothing. Turn the order round and you'd get `a.ss01`, which `smcp` has no rule for. Neither result is the small cap of the alternate `a`. That glyph, `a.ss01.sc` or whatever you'd call it, doesn't exist. I'm reasoning from how features are documented to work, and haven't tested the two together.

The script takes suffixes in the order it finds them in the font. For Plum that's good enough. In a family where it matters, the table becomes a list of pairs in the order you choose, for the reason chapter 87 gave.

Meaning. The table says `.sc` glyphs go under `smcp`. It can't check that `a.sc` is a small cap. A glyph with the wrong suffix gets the wrong feature without complaint, as `zero.alt` nearly did.

## What you learned

A dictionary used as a table turns a choice you'd make by editing constants into data the script loops over. A split can succeed on a name it was never meant for, so print what you collected before you build on it. When a table lacks an entry, report the gap and carry on. When a name misleads the script, mending the name usually serves better than teaching the script an exception.

## Try it yourself

1. Add a line to the dry run for every table entry the font has no glyphs for. Put `"case": "case"` in the table to test it. You'll need the keys of `TAGS` and the keys of the tally, and chapter 25's set subtraction.
2. Make `A.sc` and `B.sc`. They belong under `c2sc`, capitals to small caps, and `smcp` should keep only lowercase bases and figures. Filter the pairs for `sc` into two lists with `base[0].isupper()`, and build two features from one suffix.
3. Let the table map a tag to a list of suffixes: `{"ss01": ["ss01", "alt"]}`. Collect the pairs for every suffix in the list into one list, then call `feature_text` once. What does `feature_text` say when `a.alt` and `a.ss01` both exist? It's the error chapter 88 met: `Duplicate substitution source glyphs.`

## Next

Plum's `liga` feature has two ligatures, `fi` and `fl`. Ines's has eleven, with names like `f_f_i`. Chapter 90 reads a rule out of each name.
