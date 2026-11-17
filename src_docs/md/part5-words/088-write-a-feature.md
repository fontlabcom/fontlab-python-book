---
this_file: src_docs/md/part5-words/088-write-a-feature.md
---

# 88. Write a feature

Wednesday of week seventeen. The typesetter's answer came overnight: no small caps feature, no small caps in the cookbook. The glyphs exist. Ines has drawn sixty of them in her Plum since March. But a layout program doesn't go looking for glyphs called `a.sc`. It switches on a feature called `smcp`, and the feature has to say, glyph by glyph, what replaces what.

Sixty lines that differ only in a name. You know what that sentence means by now.

Yesterday you read feature text. Today a script writes some, and for the first time in this book the thing your script produces is itself a program, in another language, that another piece of software will read.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- The ten `.sc` glyphs your practice font has by now: `a.sc`, `b.sc` and `c.sc` from chapter 8, and `d.sc` to `h.sc`, `zero.sc` and `one.sc` from chapter 40. With fewer or more, your lists differ from mine in length and in nothing else.
- `list_features.py` from chapter 87. The script below defines `tell` and `ask` from [chapter 39](../part2-a-toolbox/039-ask-the-user.md) again, so it runs by itself.

I couldn't run the code in FontLab 9. The text building is plain Python and I ran all of it. The step that writes the text into the font follows Fly's source, and I haven't seen it work.

## Step 1: One rule

The rule you need for one glyph is short:

```text
sub a by a.sc;
```

Substitute `a` by `a.sc`. The words `sub` and `by` are fixed, the semicolon ends the rule, and the two names change. That's an f-string with two holes:

```python
base = "a"
alternate = "a.sc"
print(f"sub {base} by {alternate};")
```

```text
sub a by a.sc;
```

## Step 2: Which glyphs?

You want every glyph whose name ends in `.sc`, paired with the glyph it stands in for. The base name is the name with the last three characters cut off:

```python
from fly import fl

SUFFIX = ".sc"

font = fl.CurrentFont()
names = [glyph.name for glyph in font.glyphs]
pairs = []
for name in names:
    if name.endswith(SUFFIX):
        base = name[:-len(SUFFIX)]
        if base in names:
            pairs.append((base, name))
pairs.sort()
print(len(pairs))
print(pairs[:3])
print(pairs[-2:])
```

```text
10
[('a', 'a.sc'), ('b', 'b.sc'), ('c', 'c.sc')]
[('one', 'one.sc'), ('zero', 'zero.sc')]
```

`name[:-len(SUFFIX)]` is the slice from chapter 10 with a computed end: everything except the last three characters, and still right if you change `SUFFIX` to `.ss01` tomorrow.

`pairs.sort()` puts the pairs in alphabetical order, so the feature comes out the same whatever order the glyphs were made in. Tuples sort by their first item, as chapter 86 showed.

The inner `if` matters. A rule that names a glyph the font doesn't have won't compile, and one bad rule takes the whole feature text down with it. If someone has made `Q.sc` and deleted `Q`, the script must leave that pair out. Note the dot in `SUFFIX`, too. Without it, a glyph called `disc` would count as a small cap of `di`.

## Step 3: The mistake

Now the text. You have a list, you want its items on separate lines, and chapter 25 gave you `join` for gluing a list into a string. Glue with a line break:

```python
print("\n".join(pairs))
```

```text
TypeError: sequence item 0: expected str instance, tuple found
```

`join` glues strings. Item 0 of `pairs` is `('a', 'a.sc')`, a tuple, and Python won't guess how you'd like a tuple written out. In chapter 25 the list held glyph names, which were strings already, so the question never came up.

The pairs are data. The lines are text made from the data. Make the text first, one string for each pair, and then join:

```python
lines = []
for base, alternate in pairs:
    lines.append(f"    sub {base} by {alternate};")
body = "\n".join(lines)
print(body)
```

```text
    sub a by a.sc;
    sub b by b.sc;
    sub c by c.sc;
    sub d by d.sc;
    sub e by e.sc;
    sub f by f.sc;
    sub g by g.sc;
    sub h by h.sc;
    sub one by one.sc;
    sub zero by zero.sc;
```

The four spaces at the start of each f-string are indentation for the human who reads the feature later. The feature language doesn't care about them.

Look at what `join` does and doesn't do. It puts the glue between items: nine line breaks for ten lines. Nothing goes before the first or after the last. That's why the list approach beats adding `"\n"` to a growing string in a loop, where you always end up with one break too many or too few.

## Step 4: The wrapper

A feature needs an opening line and a closing line around its rules. You saw both yesterday:

```python
TAG = "smcp"
text = "feature " + TAG + " {\n" + body + "\n} " + TAG + ";"
print(text)
```

```text
feature smcp {
    sub a by a.sc;
    sub b by b.sc;
    sub c by c.sc;
    sub d by d.sc;
    sub e by e.sc;
    sub f by f.sc;
    sub g by g.sc;
    sub h by h.sc;
    sub one by one.sc;
    sub zero by zero.sc;
} smcp;
```

That's a complete feature. I used `+` here where an f-string would have done, for one reason: curly braces. Inside an f-string a `{` opens a hole, and the feature language wants a real one. You can write a real brace in an f-string by doubling it, `{{`, and it gets hard to read fast.

The tag appears twice and must match. Keeping it in one constant means it can't disagree with itself.

## Step 5: Fly has this already

Collecting suffix pairs and wrapping them is common enough that Fly carries both as functions:

```python
import fly.ap.features.code as fea_code

pairs = fea_code.suffix_pairs(names, "sc")
print(fea_code.feature_text("smcp", pairs) == text)
```

```text
True
```

The same text, character for character. You built it by hand so that you know what's inside. From here on the script uses Fly's two functions, for what they add. `suffix_pairs` leaves out pairs whose base is missing, as yours did, and also names that would be unsafe in feature text. It returns the pairs sorted by name, so the feature comes out in the same order every time. `feature_text` checks the tag and refuses a list in which the same glyph is replaced twice.

It doesn't refuse an empty list. With no `.sc` glyphs you'd get a feature with nothing in it:

```python
print(fea_code.feature_text("smcp", []))
```

```text
feature smcp {

} smcp;
```

The script has to catch that case itself, before it writes.

## Step 6: Into the font

Writing follows the shape you know: read, build the new state, show it, ask, write.

```python
import fly.ap.core.scripting as scripting

package = scripting.current_package()
blocks = scripting.read_feature_blocks(package)
others = [(tag, code) for tag, code in blocks["features"] if tag != TAG]
updated = {"prefix": blocks["prefix"],
           "features": others + [(TAG, text)]}
```

`blocks` is what the font has now. `updated` is what you want it to have: the same prefix, every feature except an old `smcp`, and the new `smcp` at the end. Leaving the old one out first means the script can run a second time, after Ines draws ten more small caps, and replace its own work. A feature tag may appear only once, so appending twice would be refused.

`blocks` itself stays untouched. The comprehension and the `+` each make a new list, which is the lesson of chapter 84 put to use.

Then the write:

```python
used = [name for pair in pairs for name in pair]
result = scripting.write_feature_blocks(
    package, blocks, updated,
    references=used, undo_name="Write smcp feature")
print(result)
```

```text
{'changed': 1}
```

The call takes both states. It compares `blocks` with the font as it is at that moment, and refuses if someone edited the features after you read them. `references` is the list of glyph names your new text mentions, flattened from the pairs by a comprehension with two `for` parts, the kind you met in chapter 85. Fly checks that each one is still in the font. `undo_name` is what the change should be called under **Edit > Undo**, if it lands there as the source says.

Run `list_features.py` afterward:

```text
smcp  12 lines, 10 rules: 10 replace
      sub a by a.sc;
      sub b by b.sc;
      sub c by c.sc;
      sub d by d.sc;
      sub e by e.sc;
      sub f by f.sc;
      sub g by g.sc;
      sub h by h.sc;
      sub one by one.sc;
      sub zero by zero.sc;
```

## Text isn't a working feature

The font now holds the text. It doesn't yet act on it. Feature text has to be compiled, turned into the tables a layout program reads, and Fly's feature code says in its own words that it never does that. I know of no call that compiles from Python.

Open **Window > Panels > Features**. You should see `smcp` in the list with your ten rules. Click the panel's **Compile** button, look in the Output panel for complaints, then type `abc` in a Glyph window's text and switch the feature on. If the three letters change to your small caps, the feature works. If the panel reports an error, it will name a line. Read the line. Your script wrote it.

I'm describing this from the User Guide for FontLab 8, and haven't pressed that button in FontLab 9.

## The whole script

```python
#FLM: Make Small Caps Feature
# Writes or replaces the smcp feature from the font's .sc glyphs.
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


TAG = "smcp"
SUFFIX = "sc"
DRY_RUN = True


def main():
    font = fl.CurrentFont()
    if font is None:
        tell("Open a font first.")
        return
    names = [glyph.name for glyph in font.glyphs]
    pairs = fea_code.suffix_pairs(names, SUFFIX)
    if not pairs:
        print(f"No .{SUFFIX} glyphs with a base. Nothing to write.")
        return
    text = fea_code.feature_text(TAG, pairs)

    package = scripting.current_package()
    blocks = scripting.read_feature_blocks(package)
    others = [(tag, code) for tag, code in blocks["features"] if tag != TAG]
    verb = "Add"
    if len(others) < len(blocks["features"]):
        verb = "Replace"
    print(text)
    print(f"{verb} {TAG}: {len(pairs)} rules")

    if DRY_RUN:
        print("Dry run. Nothing written.")
        return
    if not ask(f"{verb} the {TAG} feature with {len(pairs)} rules?"):
        return
    updated = {"prefix": blocks["prefix"],
               "features": others + [(TAG, text)]}
    used = [name for pair in pairs for name in pair]
    result = scripting.write_feature_blocks(
        package, blocks, updated,
        references=used, undo_name=f"Write {TAG} feature")
    print(result)
    print("Now compile in the Features panel.")


main()
```

Save it as `make_smcp.py`. First run, with `DRY_RUN = True`:

```text
feature smcp {
    sub a by a.sc;
    sub b by b.sc;
    sub c by c.sc;
    sub d by d.sc;
    sub e by e.sc;
    sub f by f.sc;
    sub g by g.sc;
    sub h by h.sc;
    sub one by one.sc;
    sub zero by zero.sc;
} smcp;
Add smcp: 10 rules
Dry run. Nothing written.
```

Notes on the listing.

`SUFFIX` has no dot here. `suffix_pairs` accepts it with or without one and adds its own, so `disc` is safe either way.

`verb` is worked out by comparing two lengths. If filtering by tag made the list shorter, there was an old `smcp` and this run replaces it. The reader of the dry run should know which.

The script has no `try`. If the write is refused, Fly raises an error with a sentence such as "Feature source changed; refresh the preview before applying." That sentence in the Output panel tells you more than anything I'd wrap around it. Run the script again and it will read the features afresh.

## Break it on purpose

Change `TAG` to `"smallcaps"` and run with `DRY_RUN = True`:

```text
ValueError: Feature tag must contain four ASCII letters or digits.
```

The error comes from `feature_text`, before anything touches the font. Feature tags are four characters, always, and layout programs know the registered ones by heart. `smcp` means small capitals from lowercase. A tag you invent is a feature no program will offer its user. Put `smcp` back.

## What you learned

Text for another program is built in two stages: one string for each item, then `join` to put the separators between them. `join` takes strings only, so data has to be formatted before it's glued. A write that replaces its own earlier output can be run again without harm, and that's worth arranging on purpose. A feature written into the font is text until FontLab compiles it.

## Try it yourself

1. Make `A.sc` in the Font window and run the dry run. The script proposes `sub A by A.sc;` under `smcp`. That's wrong: capitals to small caps is a different feature, `c2sc`. Split the pairs into two lists with `base[0].isupper()` and print two features. Don't write them yet.
2. Build the text for `smcp` yourself again, as in Steps 3 and 4, but with each rule followed by a comment that gives the base glyph's code point: `sub a by a.sc;  # U+0061`. You have the format from chapter 23.
3. After a real run, undo with **Edit > Undo** and run `list_features.py`. Is `smcp` gone? Write down what you saw. I couldn't check it, and chapter 100 will want to know.

## Next

Small caps are one suffix. Ines's Plum has six: `.sc`, `.alt`, `.ss01`, `.tf`, `.onum`, `.case`. Chapter 89 makes a feature for each from one table.
