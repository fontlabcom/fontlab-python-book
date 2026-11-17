---
this_file: src_docs/md/part3-shapes/056-build-them-all.md
---

# 56. Build them all

Monday of week eleven. Over the weekend Mira did something that needed no computer. She took the two lists from chapter 25, the Polish letters and the Czech ones that Plum lacks, and wrote next to each letter what it's made of. `Ć` is a `C` with an acute. `ů` is a `u` with a ring. `ě` is an `e` with a caron. It filled a page.

Last Wednesday you built one of those letters with a script that had the base and the accent typed into it as constants. To build `Ć` you'd change two constants and run it again, and then again for `ć`. Mira's page has thirty lines. And she already knows the page will grow, because the publisher mentioned Slovak on Friday, in the tone people use for things they haven't decided yet.

So the page shouldn't live inside a script. It should be a text file that Mira can open, read and add to, and the script should do whatever the file says. A line in such a file is usually called a **recipe**: it names a dish and what goes into it.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py`, with `rich`, `choose_text_file`, `ask` and `tell`.
- The anchors on `dotlessi` from chapter 55, and the `nacute` from chapter 53. The script copes if either is missing, and your numbers will differ from mine.
- Bring the Font window to the front before you run the whole script. The tool that makes glyphs refuses while a Glyph window is the active one.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. The writing at the end is read from the code of the tools.

## Step 1: Write the recipes down

Make a text file called `accents.txt` in the folder where `Plum-practice` lives. Every line has four words with spaces between them: the character, the name of the glyph, the base and the accent.

```text
# Accented letters for the Polish and Czech editions.
# character  glyph name  base  accent

# Polish
Ą Aogonek A ogonek
ą aogonek a ogonek
Ć Cacute C acute
ć cacute c acute
Ę Eogonek E ogonek
ę eogonek e ogonek
Ń Nacute N acute
ń nacute n acute
Ś Sacute S acute
ś sacute s acute
Ź Zacute Z acute
ź zacute z acute
Ż Zdotaccent Z dotaccent
ż zdotaccent z dotaccent

# Czech
Č Ccaron C caron
č ccaron c caron
Ď Dcaron D caron
Ě Ecaron E caron
ě ecaron e caron
Ň Ncaron N caron
ň ncaron n caron
Ř Rcaron R caron
ř rcaron r caron
Š Scaron S caron
š scaron s caron
Ť Tcaron T caron
Ů Uring U ring
ů uring u ring
Ž Zcaron Z caron
ž zcaron z caron

# Already in the font, on the dotlessi
í iacute dotlessi acute
î icircumflex dotlessi circumflex
ï idieresis dotlessi dieresis
ì igrave dotlessi grave
```

That's 34 recipes. Three things about the list before any code.

The character comes first because it carries the Unicode value. In chapter 53 you typed `324` for `ń`. Here the script can ask `ord` what the number is, as in chapter 23, and Mira never looks one up.

Four letters from the two lists aren't in the file. The Polish `Ł` and `ł` are an `L` and an `l` with a stroke through them, and that's drawn, not assembled. The Czech `ď` and `ť` carry a caron that looks like an apostrophe, which will need its own accent glyph. Mira leaves all four for the drawing list.

And the last four lines are glyphs Plum has. I put them in on purpose. Two of them have accents that sit off their new anchors, and you made a `nacute` on Wednesday that's ten units off in the Bold. A script that builds what the recipes say should also notice a glyph that's there and wrong.

Save the file as UTF-8. Most text editors do that without being asked. If the script later reads `Ä…` where you typed `ą`, the editor saved it another way.

## Step 2: Read a line into four names

`halfmoon.read_names` from chapter 40 reads a file with one name on a line. Here a line has four parts, so the script needs to cut it. You met `split` in chapter 9, where `name.split(".")` cut a glyph name at its dots. Call it with nothing in the parentheses and it cuts at spaces:

```python
line = "ń nacute n acute"
print(line.split())
character, name, base, mark = line.split()
print(base, mark)
```

```text
['ń', 'nacute', 'n', 'acute']
n acute
```

`split()` with no argument does two kind things. It treats any run of spaces or tabs as one cut, so you can line the columns up in the file if you like. And it drops the line ending along with them, so there's nothing to strip.

The second line of the sample takes the list of four apart into four names. Now see what a careless line does. Suppose Mira forgot the accent:

```python
character, name, base, mark = "ń nacute n".split()
```

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ValueError: not enough values to unpack (expected 4, got 3)
```

On Friday a tool complained about too many values, and this is the same complaint from the other side. Four names are waiting and three pieces arrived. The message is honest and useless to Mira, because it doesn't say which line of her file is short. For today the fix is to open the file and look. Tomorrow's chapter makes the script say where.

The function that reads the file is `read_names` with one more step:

```python
def read_recipes(path):
    recipes = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            character, name, base, mark = line.split()
            recipes.append((character, name, base, mark))
    return recipes
```

It hands back a list of tuples. A loop can take each one apart in its `for` line, as you did with pairs last week.

## Step 3: Find the shift

Thursday's `possible_shifts` gave every shift the anchors allow, and for `u` with an acute it gave two. A script that builds glyphs has to pick one. Mine walks through the accent's loops in the order of their names and takes the first one for which the base has a peg:

```python
def shift_for(font, base, mark, master):
    pegs = anchors.anchor_points(layer_for(font, base, master))
    loops = anchors.anchor_points(layer_for(font, mark, master))
    for loop in sorted(loops):
        family = loop[1:]
        if loop.startswith("_") and family in pegs:
            bx, by = pegs[family]
            mx, my = loops[loop]
            return round(bx - mx), round(by - my)
    return None
```

`loop[1:]` is a slice from chapter 10, used on a string: everything from the second character on. It turns `_acute` into `acute`. Sorted, `_acute` comes before `_acuteHigh`, so the plain peg wins when a letter has both. That's a rule I made up. It gives the designer's own result for every built glyph in Plum that has a matching pair, and I checked that before I trusted it.

The function ends in two ways. When a pair fits, `return` inside the loop hands back the shift and the loop stops there. When no pair fits, the loop runs out and the last line hands back `None`.

A glyph needs a shift in all three masters, so one more function asks three times and gives up if any answer is missing:

```python
def shifts_for(font, base, mark):
    shifts = {}
    for master in MASTERS:
        shift = shift_for(font, base, mark, master)
        if shift is None:
            return None
        shifts[master] = shift
    return shifts
```

## Step 4: Three things can be true of a recipe

Take one recipe whose base and accent are both in the font and whose anchors fit. The glyph it names is in one of four states.

It isn't there. Then the script describes it, as on Wednesday: a width for each master taken from the base, a Unicode value, and two parts in each master.

```python
def new_glyph(font, character, name, base, mark, shifts):
    layers = []
    components = []
    for master in MASTERS:
        dx, dy = shifts[master]
        width = round(layer_for(font, base, master).advanceWidth)
        layers.append((master, width))
        components.append(creation.Part(master, base, 0, 0))
        components.append(creation.Part(master, mark, dx, dy))
    return creation.NewGlyph(
        name=name,
        layers=tuple(layers),
        unicodes=(ord(character),),
        components=tuple(components),
    )
```

It's there, and its accent sits where the anchors say. Then there's nothing to do.

It's there, and its accent sits somewhere else. Last Wednesday you saw that the tool for new glyphs refuses a name that exists, and it's right to. So this state needs a different tool, one that moves a component that's already in a glyph. It works like Friday's anchor writer. An edit is a pair: which component, and where its shift should be. A row of work is a glyph, a layer and a list of edits.

```python
def moves_for(font, name, shifts):
    rich = halfmoon.rich(font, font[name])
    rows = []
    for master in MASTERS:
        layer = layer_of(rich.fl, master)
        accent = parts.components(layer)[1]
        if parts.offset(accent) != shifts[master]:
            rows.append((rich.fl, layer, [(accent.id, shifts[master])]))
    return rows
```

`accent.id` is new. Every shape in a layer has an identity that FontLab gives it, and the moving tool wants that and not the shape itself. You don't need to print it or understand it. It's a ticket you hand over.

`!=` compares two pairs here. `parts.offset` gives `(54.0, 0.0)` and the shift is `(52, 0)`. Python treats `54.0` and `54` as equal, so a pair of whole numbers and a pair of numbers with `.0` compare as you'd hope.

If all three masters agree, `rows` stays empty, and an empty list is how this function says "fine as it is".

The fourth state comes from Friday. It's there, and FontLab builds it. Chapter 55 said that no keyword opens such a glyph to a script, and the moving tool would refuse the whole batch over one of them. So the script asks first:

```python
def is_auto(font, name):
    rich = halfmoon.rich(font, font[name])
    return any([layer_of(rich.fl, master).autoLayer for master in MASTERS])
```

`autoLayer` is true for a layer that FontLab builds from a recipe of its own. An automatic glyph gets a row that says `auto`, and nothing else happens to it.

## The whole script

Here is `build_accents.py`:

```python
#FLM: Build Accented Letters
# Reads recipes from a text file: character, glyph name, base, accent.
# Builds the glyphs that are missing and moves accents that sit off their
# anchors. A recipe it can't follow is skipped without a word.
from pathlib import Path

import fly.ap.anchors.writer as anchors
import fly.ap.components.writer as parts
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.glyphs.creation as creation
import halfmoon
from fly import fl
from fly.pens import layer_of

MASTERS = ["Light", "Regular", "Bold"]


def read_recipes(path):
    recipes = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            character, name, base, mark = line.split()
            recipes.append((character, name, base, mark))
    return recipes


def layer_for(font, name, master):
    return layer_of(halfmoon.rich(font, font[name]).fl, master)


def shift_for(font, base, mark, master):
    pegs = anchors.anchor_points(layer_for(font, base, master))
    loops = anchors.anchor_points(layer_for(font, mark, master))
    for loop in sorted(loops):
        family = loop[1:]
        if loop.startswith("_") and family in pegs:
            bx, by = pegs[family]
            mx, my = loops[loop]
            return round(bx - mx), round(by - my)
    return None


def shifts_for(font, base, mark):
    shifts = {}
    for master in MASTERS:
        shift = shift_for(font, base, mark, master)
        if shift is None:
            return None
        shifts[master] = shift
    return shifts


def new_glyph(font, character, name, base, mark, shifts):
    layers = []
    components = []
    for master in MASTERS:
        dx, dy = shifts[master]
        width = round(layer_for(font, base, master).advanceWidth)
        layers.append((master, width))
        components.append(creation.Part(master, base, 0, 0))
        components.append(creation.Part(master, mark, dx, dy))
    return creation.NewGlyph(
        name=name,
        layers=tuple(layers),
        unicodes=(ord(character),),
        components=tuple(components),
    )


def moves_for(font, name, shifts):
    rich = halfmoon.rich(font, font[name])
    rows = []
    for master in MASTERS:
        layer = layer_of(rich.fl, master)
        accent = parts.components(layer)[1]
        if parts.offset(accent) != shifts[master]:
            rows.append((rich.fl, layer, [(accent.id, shifts[master])]))
    return rows


def is_auto(font, name):
    rich = halfmoon.rich(font, font[name])
    return any([layer_of(rich.fl, master).autoLayer for master in MASTERS])


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    folder = Path(font.path).parent if font.path else ""
    path = halfmoon.choose_text_file("Choose a recipe file", folder)
    if path is None:
        return

    recipes = read_recipes(path)
    print(f"{len(recipes)} recipes read.")
    have = {glyph.name for glyph in font.glyphs}
    specs = []
    work = []
    moved = 0
    fine = 0
    auto = 0
    for character, name, base, mark in recipes:
        if base not in have or mark not in have:
            continue
        shifts = shifts_for(font, base, mark)
        if shifts is None:
            continue
        if name not in have:
            specs.append(new_glyph(font, character, name, base, mark, shifts))
            state = "new"
        elif is_auto(font, name):
            auto += 1
            state = "auto"
        else:
            rows = moves_for(font, name, shifts)
            if rows:
                work = work + rows
                moved += 1
                state = "move"
            else:
                fine += 1
                state = "fine"
        text = ", ".join([f"{shifts[m][0]} {shifts[m][1]}" for m in MASTERS])
        print(f"{name:<13}{state:<6}{base} + {mark}: {text}")
    print(f"{len(specs)} to build, {moved} to move, {fine} fine as they are, {auto} automatic.")

    if not specs and not work:
        return
    if not halfmoon.ask(f"Build {len(specs)} glyphs and move the accents in {moved}?"):
        return

    package = scripting.current_package()
    if work:
        facts = history.scan_auto_facts(package)
        parts.require_safe(work, facts)
        parts.apply_work(work, "Move accents to their anchors", facts, parts.MoveEditor())
    if specs:
        facts = history.scan_auto_facts(package)
        creation.create_glyphs(package, specs, "Build accented letters", facts)
    halfmoon.tell(f"Built {len(specs)} glyphs. Moved the accents in {moved}.")


main()
```

```text
34 recipes read.
Cacute       new   C + acute: 88 210, 101 210, 111 210
cacute       new   c + acute: -4 0, 5 0, 15 0
Nacute       new   N + acute: 92 210, 119 210, 129 210
nacute       move  n + acute: 40 0, 52 0, 62 0
Sacute       new   S + acute: 18 210, 38 210, 48 210
sacute       new   s + acute: -34 0, -25 0, 15 0
Zacute       new   Z + acute: 33 210, 56 210, 66 210
zacute       new   z + acute: -20 0, -12 0, 28 0
Uring        new   U + ring: 57 210, 69 210, 69 210
uring        new   u + ring: 0 0, 12 0, 12 0
iacute       auto  dotlessi + acute: -147 0, -139 0, -140 0
icircumflex  auto  dotlessi + circumflex: -153 0, -139 0, -124 0
idieresis    auto  dotlessi + dieresis: -153 0, -137 0, -123 0
igrave       auto  dotlessi + grave: -116 0, -117 0, -140 0
9 to build, 1 to move, 0 fine as they are, 4 automatic.
```

The three numbers in each row are the Light, the Regular and the Bold.

`main` does all its reading and all its sums before it asks, and all its writing after. By the time the question appears, the list in the Output panel says what a yes would do. That order is worth keeping in every script that changes a font.

The facts are scanned twice, once before each kind of writing. The tools want facts that are fresh, and after the accents have moved, the first set describes a font that has changed.

The moves should be one step in the **Edit** menu, and the new glyphs one step each, as chapter 40 said of empty ones. So undoing everything takes ten trips to **Edit > Undo**, or one **File > Revert** if you saved before you ran it. Save before you run it.

## Read what it did

Nine glyphs are new. The capitals carry 210 in their shifts, and nobody typed it. Eight Polish letters are in the font now, counting the `ń` from Wednesday, and two Czech ones.

One glyph moved. The `nacute` went from 42, 54 and 72 to 40, 52 and 62, which settles Thursday's complaint. The script could move it because you made it yourself on Wednesday, as a plain glyph of two parts. The four `i` letters are FontLab's own, and the script left them alone. The numbers in their rows say where the anchors want the accents. For `iacute` and `igrave` that's where they are. The `î` and `ï` sit left of it, by 16 units in the Bold, and Mira writes both on her list, to be moved by hand in the Glyph window or left to FontLab's own rebuilding.

Run the script again and every row says `fine` or `auto`:

```text
0 to build, 0 to move, 10 fine as they are, 4 automatic.
```

Then run `list_anchors.py` from chapter 54 and read its last two lines:

```text
Agree with their anchors: 79. Differ: 2.
10 have no matching pair: IJ ij colon quotedbl semicolon guillemotleft guillemotright quotedblbase quotedblleft quotedblright
```

Now do a sum that the script didn't do for you. It read 34 recipes. It printed 14 rows. Twenty recipes went in and nothing came out: no row, no warning, no glyph. The comment at the top of the script admits it, "skipped without a word", and the two `continue` lines are where it happens.

Mira doesn't notice at first. She sets *Świętość* to admire the new `Ś` and `ć`, and gets a box where the `ę` should be. She checks the file. The line for `ę` is there, spelled correctly. The script said nothing about it. It costs her ten minutes.

## What you learned

A recipe file keeps the list of what to build outside the script, where the person who knows the letters can edit it. `line.split()` cuts a line at its spaces, and the pieces can go straight into as many names as there are pieces. A script that builds should check the states of each target: missing, right, there but wrong, and built by FontLab itself, which it reports and leaves alone. Existing components are moved with `parts.apply_work(work, title, facts, parts.MoveEditor())`, and all the reading comes before the question, all the writing after.

## Try it yourself

1. Add one `print` line before each `continue` in `main`, so that the script names every recipe it skips and says whether the base, the accent or the anchors were the trouble. How many are skipped for each reason? Which three accents does Mira have to draw?
2. Slovak needs `ŕ` and `Ŕ`, an `r` and an `R` with an acute. Add two recipes with the names `racute` and `Racute` and run the script. I get shifts of -75, -50 and -40 for the small one. Set the word *vŕba* and look at it in the Bold.
3. Slovak also needs `ĺ`, an `l` with an acute. Add the recipe, let the script build `lacute`, and open it. Something is wrong. Print the anchors of `l` and the box of `l`, compare the height of the `acute` peg with the height of the stem, and say what you'd change. The script did what the anchors said. Was the script wrong?

## Next

Twenty recipes vanished and the script kept quiet about every one. Chapter 57 makes it collect what went wrong, line by line, and hand Mira a list she can act on.
