---
this_file: src_docs/md/part5-words/090-ligatures.md
---

# 90. Ligatures

Friday of week seventeen. The typesetter sends a scan of a proof with one word circled: *office*. In the middle of it sit an `ff` ligature and then a plain `i` with its dot crowding the hook of the second `f`. Ines drew an `ffi` ligature years ago for this very collision. The font has the glyph. The feature never reaches it.

Ines's Plum has eleven ligatures, and the `liga` feature that lists them was typed by hand, one rule at a time, in the order in which the glyphs were drawn. The order turns out to matter.

A ligature's name already says what it's made of. Today a script reads the rule out of each name and puts the rules in the right order.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- Two new, empty glyphs called `f_f` and `f_f_i`. Make them as you made the small caps in chapter 8, with **Font > New Glyph…**. They don't need drawings today.
- `list_features.py` from chapter 87. The script below defines `tell` and `ask` from [chapter 39](../part2-a-toolbox/039-ask-the-user.md) again, so it runs by itself.

I couldn't run the code in FontLab 9. I ran the name reading and the sorting in plain Python on Plum's glyph names plus those two. The write is the one from chapter 88, and I haven't seen it work.

## Step 1: A name that is a recipe

The convention is old and simple. A ligature is named after its parts, joined with underscores: `f_f_i` replaces `f`, `f`, `i`. You have cut names at periods since chapter 9. This cut is at another character:

```python
print("f_f_i".split("_"))
```

```text
['f', 'f', 'i']
```

That list is the left side of the rule. Join it with spaces, which is `join` from chapter 88 with a different glue:

```python
name = "f_f_i"
parts = name.split("_")
print(f"sub {' '.join(parts)} by {name};")
```

```text
sub f f i by f_f_i;
```

Don't confuse this with `list(name)`, which cuts a string into its characters and would give you `['f', '_', 'f', '_', 'i']`, underscores included.

## Step 2: The two that don't follow the rule

Plum has two ligatures already, and neither has an underscore:

```python
print("fi".split("_"))
```

```text
['fi']
```

One part. A string without the separator comes back whole, in a list of one. `fi` and `fl` got their names decades before the underscore convention, and nearly every font still uses them. No rule will read `f` and `i` out of `fi`, because the same rule would read `m` and `u` out of `mu`.

When a pattern covers most cases and a short list covers the rest, write the short list down:

```python
LEGACY = {"fi": ["f", "i"], "fl": ["f", "l"]}


def recipe(name):
    if name in LEGACY:
        return LEGACY[name]
    if "_" in name and not name.startswith("."):
        return name.split("_")
    return []
```

Table first, pattern second, and an empty list for every glyph that isn't a ligature. The glyph called `underscore`, by the way, is safe. Its name has no underscore character in it.

## Step 3: Collect the rules

Walk the font and keep each glyph that has a recipe. As in chapter 88, a rule may only name glyphs the font has:

```python
from fly import fl

font = fl.CurrentFont()
names = [glyph.name for glyph in font.glyphs]
known = set(names)
rules = []
for name in names:
    parts = recipe(name)
    if not parts:
        continue
    missing = [part for part in parts if part not in known]
    if missing:
        print(f"{name}: no glyph {' '.join(missing)}, left out")
        continue
    rules.append((parts, name))
print(rules)
```

```text
[(['f', 'i'], 'fi'), (['f', 'l'], 'fl'), (['f', 'f'], 'f_f'), (['f', 'f', 'i'], 'f_f_i')]
```

Four rules, in font order: the two old ones, then the two you made this morning. `known` is a set, as in chapter 25, because all the script ever asks of it is whether a name is in the font.

## Step 4: Why the order matters

Write those four rules into a feature in that order and set the word *office*. A layout program walks along the text. At each glyph it tries the rules it has for that spot and takes the first that fits. It arrives at the first `f`. `f i`? No, the next glyph is another `f`. `f l`? No. `f f`? Yes. It swaps in `f_f` and moves on, and the next glyph is `i`, alone. The rule for `f f i` was fourth in line and never got its turn.

That's the proof on Ines's desk. Nothing is wrong with any single rule. The short rule stands in front of the long one that starts the same way.

The cure is to put longer rules first. Then `f f i` is tried before `f f`, and the short rule only catches what the long one leaves.

A caution about how sure I am. The specification for the feature language says a compiler should sort ligature rules this way by itself. Some do. I haven't seen what FontLab 9 does, and the hand-typed feature in Ines's font suggests that somewhere along the way nobody did. Sorting costs one line, and sorted text is right under either behavior.

## Step 5: The mistake

Longest first. `sorted` takes a `key`, and `len` measures length:

```python
by_len = sorted(rules, key=len)
print(by_len == rules)
```

```text
True
```

Nothing moved. The list came back as it went in, and there was no error to say why.

Ask what `len` measured:

```python
print([len(rule) for rule in rules])
```

```text
[2, 2, 2, 2]
```

Every rule is a pair, parts and name, and the length of a pair is two. You wanted the length of the first item in the pair. `sorted` did its job on four equal keys, and when keys are equal it keeps the old order.

Chapter 36 said that `sorted` hands the key function a whole row. `len` is a function like any other, and it measured what it was handed. Reaching inside the row is up to you, so write a key that does:

```python
def longest_first(rule):
    parts, name = rule
    return (-len(parts), name)


for parts, name in sorted(rules, key=longest_first):
    print(f"sub {' '.join(parts)} by {name};")
```

```text
sub f f i by f_f_i;
sub f f by f_f;
sub f i by fi;
sub f l by fl;
```

The key is a tuple, as in chapter 86. Its first part is the number of parts with a minus sign, so that 3 becomes -3 and sorts ahead of -2. That's a way to get largest first for one part of a key while the rest stays in the usual order. The second part is the name, which settles ties and makes the output the same on every run.

## Step 6: Replace in place

Chapter 88 took the old feature out and put the new one at the end. For `liga` that would be a change nobody asked for: it's the font's first feature, and chapter 87 said features apply in the order they're written. So this time the new text goes where the old text was:

```python
features = []
found = False
for tag, code in blocks["features"]:
    if tag == TAG:
        code = text
        found = True
    features.append((tag, code))
if not found:
    features.append((TAG, text))
```

A loop that copies every item and changes one on the way through. `found` is a flag: it starts as `False`, and the loop sets it if it meets the tag. After the loop, the flag tells you whether there was anything to replace. If there wasn't, the feature goes at the end after all.

## The whole script

```python
#FLM: Make Ligature Feature
# Writes or replaces the liga feature from ligature glyph names.
# Does not compile: do that in the Features panel afterward.
from fly import fl, qt
import fly.ap.core.scripting as scripting
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


TAG = "liga"
LEGACY = {"fi": ["f", "i"], "fl": ["f", "l"]}
DRY_RUN = True


def recipe(name):
    if name in LEGACY:
        return LEGACY[name]
    if "_" in name and not name.startswith("."):
        return name.split("_")
    return []


def collect(names):
    known = set(names)
    rules = []
    for name in names:
        parts = recipe(name)
        if not parts:
            continue
        missing = [part for part in parts if part not in known]
        if missing:
            print(f"{name}: no glyph {' '.join(missing)}, left out")
            continue
        rules.append((parts, name))
    return rules


def longest_first(rule):
    parts, name = rule
    return (-len(parts), name)


def feature_text(tag, rules):
    lines = []
    for parts, name in sorted(rules, key=longest_first):
        lines.append(f"    sub {' '.join(parts)} by {name};")
    return "feature " + tag + " {\n" + "\n".join(lines) + "\n} " + tag + ";"


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    names = [glyph.name for glyph in font.glyphs]
    rules = collect(names)
    if not rules:
        print("No ligature glyphs. Nothing to write.")
        return
    text = feature_text(TAG, rules)
    print(text)

    package = scripting.current_package()
    blocks = scripting.read_feature_blocks(package)
    features = []
    found = False
    for tag, code in blocks["features"]:
        if tag == TAG:
            code = text
            found = True
        features.append((tag, code))
    if not found:
        features.append((TAG, text))
    verb = "Replace" if found else "Add"
    print(f"{verb} {TAG}: {len(rules)} rules")

    if DRY_RUN:
        print("Dry run. Nothing written.")
        return
    if not ask(f"{verb} the {TAG} feature with {len(rules)} rules?"):
        return
    used = []
    for parts, name in rules:
        used = used + parts + [name]
    updated = {"prefix": blocks["prefix"], "features": features}
    result = scripting.write_feature_blocks(
        package, blocks, updated,
        references=used, undo_name=f"Write {TAG} feature")
    print(result)
    print("Now compile in the Features panel.")


main()
```

Save it as `make_liga.py`. The dry run:

```text
feature liga {
    sub f f i by f_f_i;
    sub f f by f_f;
    sub f i by fi;
    sub f l by fl;
} liga;
Replace liga: 4 rules
Dry run. Nothing written.
```

After a real run, `list_features.py` shows `liga` still in first place:

```text
liga  6 lines, 4 rules: 4 replace
```

Notes on the listing.

`"Replace" if found else "Add"` is the `if` with an `else` that chooses between two values, which you met inside a comprehension in chapter 37. It works anywhere a value can stand. Chapter 88 did the same job in three lines. Use the short form when both outcomes are plain values and the line stays readable. Otherwise write it out.

`feature_text` is your own this time. Fly's function of that name, which chapters 88 and 89 used, makes rules with one glyph on the left, and a ligature has several.

The comment lines that Plum's old `liga` text carried are gone, because the script writes the whole feature anew. A script that owns a feature owns all of it. If you want a comment in there, the script has to write it. Exercise 2.

`used` may name a glyph more than once, `f` six times here. I read Fly's source to see whether that's a problem. It only checks that every name is in the font.

## A second opinion

Fly has a ligature finder of its own:

```python
from fly.ap.features.identity_tools.feature_explorer.ligature_finder import run

for row in run(names):
    print(row)
```

By its source this should print two rows:

```text
('f_f', 'f f', 'Ready')
('f_f_i', 'f f i', 'Ready')
```

It reads underscore names and reports those whose parts are missing with a status that says so. It knows nothing of `fi` and `fl`, and it lists rules by name, short before long. That's why this chapter built its own. Fly's finder does one thing yours doesn't: for a name such as `f_i.ss01` it carries the suffix to every part and looks for `f.ss01` and `i.ss01`. Whether that's right depends on your font. In some, `f_i.ss01` is an alternate ligature of the plain `f` and `i`.

## Break it on purpose

Make a glyph called `c_t` and run the dry run. You get a fifth rule, `sub c t by c_t;`, under `liga`. Now ask Ines. The `ct` ligature with its looping bridge is ornament, and she'd never want it switched on in running text. It belongs to `dlig`, discretionary ligatures, which the user turns on by choice.

The name gave you the parts. It couldn't tell you the feature. That decision belongs to the designer, and the script needs a place to record it: a set of names, say, that go to `dlig`. Exercise 3. Delete `c_t` when you're done.

## What you learned

`split` works with any separator, and a string without the separator comes back whole in a list of one. A short table of exceptions in front of a pattern handles names that are older than the pattern. A key function receives the whole row, so a `len` that should measure one item needs a function that picks the item out. A minus sign in a tuple key sorts that part largest first and leaves the other parts alone.

## Try it yourself

1. Add `"ffi": ["f", "f", "i"]` and `"ff": ["f", "f"]` to `LEGACY`, without making glyphs of those names. Does the output change? Then say why a table entry for a glyph the font lacks costs nothing here.
2. Have `feature_text` write a first line inside the braces: `    # written by make_liga.py, 4 rules`. Run `list_features.py` and check that it still counts four rules. Chapter 87's comment handling is what makes that work.
3. Add `DISCRETIONARY = {"c_t", "s_t"}` and split the collected rules into two lists by `name in DISCRETIONARY`. Print two features, `liga` and `dlig`, in the dry run. Don't write them.

## Next

Chapter 87 found a class in the prefix, `@cpsp`, with 63 capitals in it. Nobody has checked since whether those 63 names are all still in the font. Chapter 91 reads classes, checks them and writes one.
