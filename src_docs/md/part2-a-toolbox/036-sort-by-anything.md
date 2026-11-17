---
this_file: src_docs/md/part2-a-toolbox/036-sort-by-anything.md
---

# 36. Sort by anything

Friday. Mira has her table of sidebearings and widths, and it comes out in whatever order she clicked the cells. She wants the widest glyph at the top. Ines wants the most lopsided at the top. Tomas has asked for the whole font in alphabetical order, and he means his alphabet, where `a` comes after `A` and not after `Z`.

That's three orders for the same rows. You've had `sorted` since chapter 10, and it knows one order. Today you teach it the others. In chapter 29 you handed a function to `commit`. Today you hand one to `sorted`.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `metrics_rows` and `glyphs_of` from [chapter 35](035-lists-of-lists.md). They're repeated below, so you don't need the old script.
- The same six glyphs selected: `H`, `O`, `A`, `n`, `o` and `v`.

Start every listing in this chapter with these lines. They are the two functions from chapter 35, copied in so that each listing runs by itself:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph
import fly.ap.core.scripting as scripting


def glyphs_of(font, only_selected=False):
    if not only_selected:
        return font.glyphs
    glyphs = []
    for name in scripting.names_selected_names():
        glyphs.append(font[name])
    return glyphs


def metrics_rows(font, only_selected=False):
    rows = []
    for glyph in glyphs_of(font, only_selected):
        measured = pGlyph(font, glyph)
        if not measured.isEmpty():
            rows.append((glyph.name, measured.getLSB(), int(glyph.width), measured.getRSB()))
    return rows


font = fl.CurrentFont()
rows = metrics_rows(font, only_selected=True)
```

## Step 1: What sorted does to rows

Hand the table to `sorted` as it is:

```python
for row in sorted(rows):
    print(row)
```

```text
('A', 13, 596, 11)
('H', 76, 672, 70)
('O', 36, 708, 36)
('n', 70, 523, 66)
('o', 38, 520, 38)
('v', 8, 455, 3)
```

It worked, and you can see the rule it used. `sorted` compares rows by their first field. The names are the first field, so the table is in name order, capitals first, as chapter 10 warned. If two rows had the same first field, `sorted` would go on to the second to break the tie, and then to the third. That's how you'd sort a pile of index cards: by the top line, and by the next line when the top lines match.

So one way to sort by width would be to build the rows with the width in front. But then the table is in the wrong shape for everything else, and the day Ines wants a different order you'd have to rebuild it again. The rows should stay as they are. What needs to change is what `sorted` looks at.

## Step 2: Tell it what to look at

`sorted` has an optional slot called `key`. You fill it by name, as chapter 34 showed. What goes in it is a function: one that takes a row and hands back the thing to sort by.

```python
def by_width(row):
    return row[2]


for row in sorted(rows, key=by_width):
    print(row)
```

```text
('v', 8, 455, 3)
('o', 38, 520, 38)
('n', 70, 523, 66)
('A', 13, 596, 11)
('H', 76, 672, 70)
('O', 36, 708, 36)
```

`by_width` is as small as a function gets. Give it a row and it hands back the third field. `sorted` calls it once for every row, lines the rows up by the numbers it gets back, and hands you the rows. The numbers are thrown away afterward. They were only for comparing.

Picture a teacher lining up a class by height. She doesn't rearrange the children's heights, she rearranges the children. Height is what she looks at to decide who stands where. The `key` function tells `sorted` what to look at.

Now look hard at this part of the line:

```python
sorted(rows, key=by_width)
```

There are no parentheses after `by_width`. You've seen that once before. In chapter 29 you handed `widen` to `history.commit` without parentheses, and I compared it to handing over a recipe card. This is the same thing. With parentheses, `by_width(row)` runs the function now and gives you a number. Without them, `by_width` is the function itself, handed to `sorted` for `sorted` to use when it needs it.

A function is a value. It lives in a box with a name on it, as a number does. You can put it in a slot or hand it to another function.

## Step 3: The parentheses that don't belong

Your fingers have learned that a function's name is followed by parentheses, so sooner or later you'll type this:

```python
for row in sorted(rows, key=by_width()):
    print(row)
```

```text
TypeError: by_width() missing 1 required positional argument: 'row'
```

You know this message from chapter 34: a slot that must be filled was left empty. The parentheses told Python to call `by_width` right there, before `sorted` had started, and with nothing in its slot. Python never got as far as sorting.

Read the message for what it's really telling you. You don't call a key function yourself. `sorted` does that, once per row, and it supplies the row. You only hand it over, so take the parentheses off.

## Step 4: Biggest first

Mira wanted the widest at the top, and so far it's at the bottom. `sorted` has a second optional slot for that:

```python
for name, lsb, width, rsb in sorted(rows, key=by_width, reverse=True):
    print(f"{name:<6}{lsb:>5}{width:>6}{rsb:>5}")
```

```text
O        36   708   36
H        76   672   70
A        13   596   11
n        70   523   66
o        38   520   38
v         8   455    3
```

`reverse=True` turns the order around. Its default is `False`, so you've been using this knob since chapter 10 without knowing it was there.

If you only want the top few, slice the sorted list. The slice comes from chapter 10. To get the five widest glyphs in the whole font, leave `only_selected` out so that the rows cover every glyph with a shape:

```python
rows = metrics_rows(font)
for name, lsb, width, rsb in sorted(rows, key=by_width, reverse=True)[:5]:
    print(f"{name:<12}{width:>5}")
```

```text
emdash       1000
OE            989
W             859
Wacute        859
Wcircumflex   859
```

That makes the plain `widest_glyph` from chapter 18 a special case. The widest glyph is the first row of the table sorted by width, biggest first. If you only want the single winner, Python has a shortcut that takes the same kind of key: `max(rows, key=by_width)` hands back the one row with the largest width, and `min` hands back the smallest.

## Step 5: Sort by something that isn't a column

The key function doesn't have to pick a field. It can work something out. Ines wants the most lopsided glyphs first, and lopsidedness is the difference between the two sidebearings:

```python
def lopsided(row):
    name, lsb, width, rsb = row
    return abs(lsb - rsb)


rows = metrics_rows(font, only_selected=True)
for row in sorted(rows, key=lopsided, reverse=True):
    print(row, lopsided(row))
```

```text
('H', 76, 672, 70) 6
('v', 8, 455, 3) 5
('n', 70, 523, 66) 4
('A', 13, 596, 11) 2
('O', 36, 708, 36) 0
('o', 38, 520, 38) 0
```

`abs(-6)` is 6: the size of a number without its sign. Inside `lopsided` the row is unpacked into named boxes, as chapter 35 recommended, so the sum reads as what it is.

The `H` is at the top, where Mira's note from yesterday said it would be. The two round letters share the bottom with a difference of 0. Look at their order: `O` before `o`. Neither is more lopsided than the other, so `sorted` had nothing to go on, and it left them in the order they came in. It always does that with ties. Rows that the key can't tell apart keep their original order, and you can rely on it.

Tomas's alphabet is the same trick. He wants `a` next to `A`, so the key is the name with its capitals flattened:

```python
def by_name_like_a_person(row):
    return row[0].lower()


names = []
for row in sorted(rows, key=by_name_like_a_person):
    names.append(row[0])
print(" ".join(names))
```

```text
A H n O o v
```

`lower()` is new: it hands back the string in small letters. `sorted` compares `"a"`, `"h"`, `"n"`, `"o"`, `"o"` and `"v"`, and then hands back the real names with their capitals intact. `O` and `o` tie, so they stay in the order they came.

## Step 6: Sort the tally from chapter 22

In chapter 22 you counted glyphs by width and got a dictionary. Chapter 22 left the tally unsorted. In chapter 32 you got another, the tally of statuses. A dictionary can't be sorted where it stands, but `items()` hands you its pairs, and pairs are rows of two:

`status_tally` is the counter from chapter 33. Here it is again, with the colour numbers it needs, so that this listing runs after the starter lines:

```python
RED = 1
YELLOW = 61
GREEN = 121

LEGEND = {
    0: "untouched",
    RED: "not-drawn",
    YELLOW: "needs-work",
    GREEN: "done",
}


def status_tally(font):
    tally = {}
    for glyph in font.glyphs:
        status = LEGEND.get(pGlyph(font, glyph).mark, "unknown-color")
        tally[status] = tally.get(status, 0) + 1
    return tally


tally = status_tally(font)


def by_count(pair):
    return pair[1]


for status, count in sorted(tally.items(), key=by_count, reverse=True):
    print(f"{status:<14}{count:>4}")
```

```text
untouched      197
done             9
needs-work       3
not-drawn        3
unknown-color    1
```

Each pair is `(status, count)`. The key picks the count, and `reverse=True` puts the biggest first. That's the pattern for every "top ten" you'll ever be asked for: count into a dictionary, take the items, sort by the second field, slice.

??? info "Going deeper: key functions in one line"
    When you read other people's scripts you'll see key functions written in one line, with no `def` and no name:

    ```python
    sorted(rows, key=lambda row: row[2])
    ```

    `lambda` makes a small function on the spot. The part before the colon is its slot and the part after is what it returns. It does what `by_width` does. I've used `def` in this chapter because a name like `by_width` tells you what the sort is for, and because you can test a named function by itself. Use whichever you find easier to read.

## The whole script

Save this as `widest_first.py`. It carries its own copies of `glyphs_of` and `metrics_rows`, plus the two key functions, so it needs nothing but Fly:

```python
#FLM: Widest First
# Prints the metrics of the selected glyphs, widest first,
# and then the three most lopsided of them.
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph
import fly.ap.core.scripting as scripting

HOW_MANY = 3


def glyphs_of(font, only_selected=False):
    if not only_selected:
        return font.glyphs
    glyphs = []
    for name in scripting.names_selected_names():
        glyphs.append(font[name])
    return glyphs


def metrics_rows(font, only_selected=False):
    rows = []
    for glyph in glyphs_of(font, only_selected):
        measured = pGlyph(font, glyph)
        if not measured.isEmpty():
            rows.append((glyph.name, measured.getLSB(), int(glyph.width), measured.getRSB()))
    return rows


def by_width(row):
    return row[2]


def lopsided(row):
    name, lsb, width, rsb = row
    return abs(lsb - rsb)


font = fl.CurrentFont()
rows = metrics_rows(font, only_selected=True)

if not rows:
    print("Select some glyphs with shapes in them first.")
else:
    print(f"{'glyph':<8}{'LSB':>5}{'width':>7}{'RSB':>5}")
    for name, lsb, width, rsb in sorted(rows, key=by_width, reverse=True):
        print(f"{name:<8}{lsb:>5}{width:>7}{rsb:>5}")

    print()
    print("Most lopsided:")
    for row in sorted(rows, key=lopsided, reverse=True)[:HOW_MANY]:
        print(f"  {row[0]:<6}{lopsided(row):>3}")
```

```text
glyph     LSB  width  RSB
O          36    708   36
H          76    672   70
A          13    596   11
n          70    523   66
o          38    520   38
v           8    455    3

Most lopsided:
  H       6
  v       5
  n       4
```

`key=by_width` has no parentheses. You're handing the function on unopened, and `sorted` calls it for you. And the bare `print()` in the middle, with nothing in its slot, prints an empty line.

Mira will want this one every time she spaces, so put it in the menu, as you did with the Friday report in chapter 18. The first line, `#FLM: Widest First`, is the name the menu will show. Save a copy as `Widest First.py` in the `Halfmoon` folder inside FontLab's `Scripts` folder, and choose **Scripts > Refresh Scripts**. Select a few cells and pick it from the menu.

One caution about "lopsided". The `n` is meant to be lopsided, because a stem and an arch need different amounts of white. The script can't tell which differences were intended. It puts them in order so that a person who knows can look at the top of the list first. That's the limit you met in chapter 31, where `ok` meant the font would accept a rename and not that the rename was wise.

Ines looks at the list, says the `v` is fine and the `H` isn't, and Mira fixes the `H`.

## What you learned

`sorted` takes an optional `key`, a function that it calls on each item to get the thing to compare, and an optional `reverse=True` to put the biggest first. You hand the function over by name without parentheses, because a function is a value like any other. The key can pick a field or work something out, and items that tie keep the order they came in. To sort a dictionary, sort its `items()`.

## Try it yourself

1. Sort the six rows by right sidebearing, smallest first. Then write a key function `black_width(row)` that returns the width minus both sidebearings, and sort by that. Which of the six glyphs has the widest black shape?
2. The digits in Plum all have the same width, 490. Select them and sort by width, then sort by name. In what order do they come out the first time, and why? Now write a key function that returns `(row[2], row[0])`, a tuple of width and name. What does `sorted` do with a key that's a tuple? Step 1 has the answer.
3. Print the ten most common advance widths in the whole font, most common first, using the width tally from chapter 22 and the pattern from Step 6.

## Next

`metrics_rows` takes six lines to build a list. Python has a way to say the same thing in one. Chapter 37 shows it, and shows when not to use it.
