---
this_file: src_docs/md/part6-families/108-make-the-instances.md
---

# 108. Make the instances

Wednesday of week twenty-one. The client has answered Mira's email. Five weights now, the four outer ones when there are drawings for them, and could the list please be in the font by Friday.

"In the font" means instances. A master is a drawing. An instance is an order: make me a font at this place on the axis, and call it this. Yesterday's report said Plum has none of its own.

Five instances could be typed by hand in two minutes. Oskar's old families had nine weights in four widths, and he typed all thirty-six, twice, because the first time he put the SemiBold of the Condensed at 500. So today the list comes out of a table, and the table is the one you already have.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, and saved.
- `halfmoon.py` with `tell`.
- `list_instances.py` from chapter 107.

I couldn't run the code in FontLab 9. The planning is plain Python and I ran it. What FontLab does with the result I describe from the User Guide, and I say where I'm guessing.

## Where this chapter stops, and why

I'll say this before the steps, since it shapes them.

FontLab has a call that adds an instance to a font from Python. I found it in the list of everything FontLab offers to scripts. I didn't find one script, in Fly or in any of the tools around it, that uses the call. Nobody I can read has tried it and written down what happened. I don't know whether **Edit > Undo** takes it back.

A book that told you to run that on a font you care about would be doing you no favor. So the script in this chapter plans, and a person does the last step in **Font Info**, where FontLab's own buttons do the writing. The call itself is at the end, marked for what it is.

A script that does nine tenths of a job and hands the last tenth to a person, with the text ready to paste, is a respectable script. The typing was where Oskar's mistake happened, and the typing is what you take away.

## Step 1: A plan is a table with one more column

You have the client's table as `WANTED`, a list of pairs. A plan says, for each row, what's to be done about it. That's a third value, so each row becomes a record, as yesterday's masters did:

```python
def plan(wanted, low, high, taken):
    rows = []
    for name, value in wanted:
        if value < low or value > high:
            status = "outside the masters"
        elif value in taken:
            status = "already there"
        else:
            status = "new"
        rows.append({"name": name, "value": value, "status": status})
    return rows
```

`low` and `high` are the outermost masters, and `taken` is a list of the places where the font already has an instance. Three outcomes, tested in an order that matters: a weight outside the masters is refused first, whatever else is true of it.

Try it without FontLab, with numbers you make up:

```python
rows = plan([("Thin", 100), ("Regular", 400), ("Medium", 500)], 300, 700, [400.0])
for row in rows:
    print(row)
```

```text
{'name': 'Thin', 'value': 100, 'status': 'outside the masters'}
{'name': 'Regular', 'value': 400, 'status': 'already there'}
{'name': 'Medium', 'value': 500, 'status': 'new'}
```

A function that takes plain lists and numbers can be tested at your desk with no font open. That's worth arranging whenever you can.

## Step 2: The mistake

My first `plan` didn't take places. It took names:

```python
names = ["Light", "(Regular)", "Bold"]
wanted = [("Light", 300), ("Regular", 400), ("Medium", 500)]
print([name for name, value in wanted if name not in names])
```

```text
['Regular', 'Medium']
```

It wants to make a Regular, in a font that has one. The font's list says `(Regular)`, with parentheses, and `"Regular"` isn't `"(Regular)"`. To Python they're two strings with nothing in common but most of their letters.

The parentheses are FontLab's way of marking a word that's left out when names are joined: the style is "Bold", and "Bold Italic", and the plain one is "Regular" only when there's nothing else to say. Plum's source file writes its middle weight that way.

I could strip the parentheses before comparing. Then the next font would say "Semi Bold" with a space, or "Demi", and I'd be patching names forever. The name is a label for people. What makes an instance the same instance is where it sits. So compare places:

```python
taken = [300.0, 400.0, 700.0]
print([name for name, value in wanted if value not in taken])
```

```text
['Medium']
```

The font gives 400.0 and the table says 400, and `in` finds it all the same, since Python counts a whole number and its float as equal.

## Step 3: One line for Font Info

FontLab keeps a short list for each axis, which the User Guide calls the axis instances. It lives in **Font Info > Axes**, in a text field, and it reads like this:

```text
Light=300, (Regular)=400, Bold=700
```

A name, an equals sign, a place, and commas between. A name with a space goes in double quotes. That's a format a script can write:

```python
DEFAULT_STYLE = "Regular"


def axis_line(rows):
    parts = []
    for row in rows:
        if row["status"] == "outside the masters":
            continue
        name = row["name"]
        if name == DEFAULT_STYLE:
            name = f"({name})"
        if " " in name:
            name = f'"{name}"'
        parts.append(f"{name}={row['value']:g}")
    return ", ".join(parts)
```

The line holds every weight that's inside the masters, the ones already there too. You'll replace the field's contents, so the old entries have to be in the new text or they're gone.

`f'"{name}"'` is an f-string in single quotes so that it can hold double ones. You've seen the two kinds of quote take turns since chapter 2.

## The whole script

```python
#FLM: Make Instances
# Plans the instances the client asked for and writes the plan to a file.
# The font is not changed: you paste one line into Font Info yourself.
from pathlib import Path

import fly.ap.core.scripting as scripting
import halfmoon
from fly import fl

WANTED = [
    ("Thin", 100),
    ("ExtraLight", 200),
    ("Light", 300),
    ("Regular", 400),
    ("Medium", 500),
    ("SemiBold", 600),
    ("Bold", 700),
    ("ExtraBold", 800),
    ("Black", 900),
]
DEFAULT_STYLE = "Regular"


def on_axis(axis, location):
    return float(axis.valueWeight(location, 0.0))


def plan(wanted, low, high, taken):
    rows = []
    for name, value in wanted:
        if value < low or value > high:
            status = "outside the masters"
        elif value in taken:
            status = "already there"
        else:
            status = "new"
        rows.append({"name": name, "value": value, "status": status})
    return rows


def axis_line(rows):
    parts = []
    for row in rows:
        if row["status"] == "outside the masters":
            continue
        name = row["name"]
        if name == DEFAULT_STYLE:
            name = f"({name})"
        if " " in name:
            name = f'"{name}"'
        parts.append(f"{name}={row['value']:g}")
    return ", ".join(parts)


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    axis = list(package.axes)[0]
    spots = [on_axis(axis, package.location(m)) for m in package.masters]
    taken = [on_axis(axis, i.location) for i in package.instances]
    rows = plan(WANTED, min(spots), max(spots), taken)
    for row in rows:
        print(f"{row['name']:<12}{row['value']:>5g}  {row['status']}")
    new = [row for row in rows if row["status"] == "new"]
    line = axis_line(rows)
    print(f"{len(new)} new instances. Axis instances for {axis.name}:")
    print(line)
    path = Path(font.path).parent / "instances-plan.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(line + "\n")
    print(f"Saved as {path.name}.")


main()
```

Save it as `make_instances.py` and run it:

```text
Thin          100  outside the masters
ExtraLight    200  outside the masters
Light         300  new
Regular       400  new
Medium        500  new
SemiBold      600  new
Bold          700  new
ExtraBold     800  outside the masters
Black         900  outside the masters
5 new instances. Axis instances for weight:
Light=300, (Regular)=400, Medium=500, SemiBold=600, Bold=700
Saved as instances-plan.txt.
```

If yesterday's report listed three instances in your font, the rows for Light, Regular and Bold say `already there` and the count is 2. The line is the same either way.

Notes on the listing.

`on_axis` is yesterday's function, copied. Two scripts now carry it, and by chapter 33's rule that's one too many: it belongs in `halfmoon.py`. Move it there if you like, and import it in both. I've left the listing whole so that it runs as printed.

`min(spots)` and `max(spots)` find the outer masters without sorting anything. Yesterday needed the order, to find neighbors. Today only the two ends matter.

The file is written the way chapter 26 wrote one, next to the font. A plan on paper outlives the Output panel, and Mira can attach it to her reply.

## The last step, by hand

Save the font first. Then:

1. Open **Font Info** and go to **Axes**. Select the weight axis.
2. Find the field for axis instances. Replace what's in it with the line from `instances-plan.txt`.
3. Go to **Instances** and click **From Axes**. By the User Guide, that replaces the list of instances with one for each axis instance.
4. Click **OK**.

I've read those pages and haven't clicked those buttons in FontLab 9. If a label differs on your screen, trust the screen.

Now run `list_instances.py`. It should say `5 instances:` and name them, and then run `make_instances.py` once more: five rows of `already there`, and `0 new instances`. The same script is the plan before the work and the check after it.

## The call I didn't use

For the record, this is what the list of FontLab's calls says would add one instance:

```python
instance = fl.flInstance("Medium", "Medium", fl.flLocation({"wt": 500}))
package.addInstance(instance)
```

The second `"Medium"` is the style name. `fl.flLocation` with a dictionary from the axis's short name to a place is proved: Fly uses it elsewhere. The other two calls are names in a list, and no more than that to me. If you try them, do it on a copy of the font, saved, and expect no Undo. Then run `list_instances.py` and see what the font says.

## Break it on purpose

Ines calls the 600 weight "Demi", and adds it to the table without looking for a 600 that's already there. Put `("Demi", 600),` after the SemiBold row and run:

```text
SemiBold      600  new
Demi          600  new
```

```text
6 new instances. Axis instances for weight:
Light=300, (Regular)=400, Medium=500, SemiBold=600, Demi=600, Bold=700
```

Two names for one place, and the plan passed them both. `plan` checks each row against the font. It never checks the rows against each other. Paste that line and you'd export two files that hold the same font under different names, and the client would ask which one is real.

Take the row out. Exercise 2 closes the hole.

## What you learned

A plan is the wanted table with a column added that says what to do about each row, and a function that builds it from plain lists can be tested with no font open. Things that have both a name and a place should be matched by the place, since names are spelled for people. A script can stop short of the write, hand a person the text to paste, and then serve as the check that the work was done. When a call exists and nobody has written down what it does, say so and keep it away from the font you care about.

## Try it yourself

1. Add `("Extra Light", 350)` to the table, with the space. Where does it land in the line, and is that where you'd want it? Sort the rows by value inside `axis_line`, using a key function as chapter 36 did.
2. Make `plan` notice two rows with one value. Keep a list of the values seen so far, and give the second row the status `same place as an earlier row`. `axis_line` should leave such rows out.
3. The client's names have no spaces and Ines would like "Semi Bold" on the menu. Write `spaced(name)` that puts a space before each capital letter but the first, using `isupper()` on each character. Then `axis_line` has to quote the result.

## Next

A new weight needs kerning as much as it needs outlines. Chapter 109 looks at the pairs in each master and finds the ones that exist in one master and are missing in the next.
