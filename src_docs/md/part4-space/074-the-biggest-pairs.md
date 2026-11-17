---
this_file: src_docs/md/part4-space/074-the-biggest-pairs.md
---

# 74. The biggest pairs

Thursday of week fourteen. Yesterday Mira mended one pair in the Bold, `AV`, which had the Light's value and pulled the letters into each other. She doesn't believe it was the only one.

"Which pairs do the most work?" she asks. "Show me the big ones, and I'll look at those first."

It's a fair way to check a hundred pairs when you have time for ten. This chapter builds that list, finds that it's the wrong list, and builds a better one. Nothing in the font changes today.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `rich`.
- The font as chapters 68, 72 and 73 left it. If you skipped one of them, your numbers will differ from mine, and the method won't. The Bold table in step 3 also assumes you ran `copy_sb.py` on the Bold's accented letters, as chapter 68 suggested.

I couldn't run the code in FontLab 9. The tables below are worked out from Plum's source file, with the changes of the earlier chapters applied by hand.

## Step 1: Sort by size

Chapter 69 sorted the kerning list by value, most negative first. That puts the four pairs that add space at the far end, as if they mattered least. "Big" should mean far from zero in either direction, and chapter 36 had the function for that: `abs`.

```python
import fly.ap.core.scripting as scripting

package = scripting.current_package()
pairs = scripting.kerning_pairs(package, "Regular")


def by_size(item):
    return abs(item[1])


big = sorted(pairs.items(), key=by_size, reverse=True)
for (first, second), value in big[:8]:
    print(f"{first:<14}{second:<12}{value:>6.0f}")
```

`big[:8]` is a slice, as in chapter 10: the first eight of a list. Since the list is sorted, they're the eight biggest. Sort, then slice: that's how you take the top of anything.

```text
L             T             -113
quoteright    c             -112
quoteright    @R_oacute     -112
quoteright    g             -112
...
```

I've cut the output short, because below the first line I can't tell you what order you'll see. Nine pairs share the value −112. `sorted` keeps things that are equal in the order they came in, and they came in the order the font happens to hold them. Run it tomorrow on another machine and the eight may be a different eight of the nine.

A list that can change between two runs is a poor thing to hand to somebody. The cure is to give the sort a second thing to go by when the first is equal, and a key function does that by returning a tuple:

```python
def by_size(item):
    (first, second), value = item
    return (-abs(value), first, second)


big = sorted(pairs.items(), key=by_size)
```

Python compares tuples the way you'd compare words in a dictionary: by the first part, then, if those are equal, by the second, and so on. So this sorts by size, then by the first name, then by the second.

The minus sign replaces `reverse=True`. I want the biggest size first and the names from A to Z, and `reverse` would turn both around. Negating the number turns only the number around.

```text
L             T             -113
quoteright    @R_eacute     -112
quoteright    @R_oacute     -112
quoteright    c             -112
quoteright    ccedilla      -112
quoteright    d             -112
quoteright    e             -112
quoteright    g             -112
```

## Step 2: The wrong list

Mira reads it and shrugs. Seven of the eight lines are the apostrophe before a round letter. She sets `l'eau` and `d'où`, and they're fine.

In the Bold it's the same picture, with −124 in place of −112 and ten such pairs at the top. The pair she mended yesterday stood at −69, far down the list, and it was the one that collided.

That's today's mistake, and it was in the question. The size of a pair says how far the second glyph moves. It doesn't say where the glyph ends up. The apostrophe has a lot of white beside it and the pair takes most of it away, which is the pair doing its job. The `A` and the `V` in the Bold had no white to give, and a middling pair pushed them together.

So measure each pair against the space it acts on. Chapter 61 gave you that: the right side of the first glyph plus the left side of the second. Add the pair's value, and you have what's left:

```python
import halfmoon
from fly import fl

font = fl.CurrentFont()
a = halfmoon.rich(font, font["quoteright"])
b = halfmoon.rich(font, font["e"])
space = a.getRSB("Regular") + b.getLSB("Regular")
print(space, space + pairs[("quoteright", "e")])
```

```text
54 -58.0
```

54 units of white before kerning and −58 after. A negative number here means the boxes around the two shapes overlap. Whether the shapes touch is another matter, and I'll come back to it.

## Step 3: A stand-in for a class

Half the pairs name a class, and a class has no sidebearings. Which glyph should stand for `@L_A`?

Chapter 72 kept the first member in front for this moment: by custom, the first member of a class stands for the rest. Since the members were grouped because their sides are alike, any of them would give nearly the same number.

```python
def stand_in(side, classes):
    if side.startswith("@"):
        members, place = classes[side[1:]]
        return members[0]
    return side


classes = scripting.kerning_classes(package, "Regular")
print(stand_in("@L_A", classes), stand_in("V", classes))
```

```text
A V
```

`side[1:]` is a slice of a string: everything from the second character on, which takes off the `@`. The kerning list writes class names with the sign and the dictionary of classes has them without.

## Step 4: Sort by what's left

Now each pair becomes a row of five: two names, the value, the space, and what's left. Sort by the last, smallest first, with the names to settle ties:

```python
def by_left(row):
    first, second, value, space, left = row
    return (left, first, second)
```

In the Bold, the top of that list is the apostrophe again: nine pairs with −105 left. Mira looks at `l'eau` in the Bold. The apostrophe sits above the `e`, and the two never meet. The measurement is of boxes, and these two shapes are at different heights.

She says to leave the apostrophe out. A script can't see that for itself, so it gets a list, and you decide what goes on it:

```python
HIGH = ["quoteright"]
```

## The whole script

```python
#FLM: Top Pairs
# For each master, lists the kerning pairs that leave the least room
# between the two glyphs, and counts the ones that go deeper than DEEP.
import halfmoon
import fly.ap.core.scripting as scripting
from fly import fl

MASTERS = ["Light", "Regular", "Bold"]
HOW_MANY = 8
DEEP = -70
# Glyphs that sit above the lowercase and pass over it.
HIGH = ["quoteright"]


def stand_in(side, classes):
    if side.startswith("@"):
        members, place = classes[side[1:]]
        return members[0]
    return side


def by_left(row):
    first, second, value, space, left = row
    return (left, first, second)


def pair_rows(font, package, master):
    pairs = scripting.kerning_pairs(package, master)
    classes = scripting.kerning_classes(package, master)
    rows = []
    for (first, second), value in pairs.items():
        a = stand_in(first, classes)
        b = stand_in(second, classes)
        if a in HIGH or b in HIGH:
            continue
        space = halfmoon.rich(font, font[a]).getRSB(master) + halfmoon.rich(font, font[b]).getLSB(master)
        rows.append((first, second, value, space, space + value))
    return sorted(rows, key=by_left)


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    for master in MASTERS:
        rows = pair_rows(font, package, master)
        deep = [row for row in rows if row[4] < DEEP]
        print(f"{master}: {len(rows)} pairs measured, {len(deep)} leave less than {DEEP}.")
        for first, second, value, space, left in rows[:HOW_MANY]:
            print(f"  {first:<14}{second:<12}{value:>6.0f}{space:>7}{left:>7.0f}")


main()
```

Save it as `top_pairs.py`. On the practice font it should print:

```text
Light: 75 pairs measured, 1 leave less than -70.
  @L_Y          @R_A2          -90     18    -72
  @L_Y          e             -103     44    -59
  @L_A          @R_Y2          -90     40    -50
  @L_Y          o              -96     46    -50
  @L_Y          z              -62     23    -39
  V             @R_A2          -69     34    -35
  @L_A          T              -63     33    -30
  @L_A          V              -69     42    -27
Regular: 81 pairs measured, 1 leave less than -70.
  L             T             -113     20    -93
  @L_Y          @R_A2          -65     -1    -66
  @L_A          @R_Y2          -71     19    -52
  @L_A          T              -61     12    -49
  T             y              -55      6    -49
  @L_Y          e              -72     24    -48
  @L_Y          o              -72     24    -48
  T             e              -84     36    -48
Bold: 77 pairs measured, 17 leave less than -70.
  T             w             -105      1   -104
  @L_Y          @R_A2          -90     -8    -98
  T             @R_wacute      -94      1    -93
  L             V              -90      4    -86
  @L_A          @R_Y2          -90      5    -85
  @L_Y          e             -103     19    -84
  T             e             -108     28    -80
  T             o             -108     28    -80
```

The three columns of numbers are the pair's value, the space before kerning, and what's left.

Notes on the listing.

`pair_rows` returns its rows already sorted, so `main` can slice them and count in them without thinking about order.

`deep` is a comprehension with a condition, as in chapter 37, and only its length is used. Counting the things that pass a test is a list of them and `len`.

The count comes before the slice in the output, and it's the more useful of the two. A top eight always has eight lines, whatever the state of the font. The count tells you whether those eight are the whole problem or the visible part of it.

`DEEP` is −70 because below it the Light and the Regular have one pair each. It's a line drawn from this font, and another design would need another number.

## What the list says

Read the three headings together. One pair goes deeper than −70 in the Light, one in the Regular, and seventeen in the Bold.

The Bold's kerning is too strong throughout, as `AV` suggested. Chapter 69's first exercise showed why: most of its values are the Light's, copied over. The Light has wide sidebearings and can afford a pair of −90. In the Bold the same −90 lands on 5 units of white.

Mira won't mend seventeen pairs one at a time, and the seventeen are only the ones past the line. The whole Bold wants its kerning turned down in proportion. That's chapter 79.

Two lines get a mark in pencil. `L T` in the Regular leaves −93, where the Light leaves −10 and the Bold −66. A master in the middle shouldn't be the extreme one. And `T w` in the Bold leaves −104: the arm of the `T` would reach halfway across the `w`. She sets both in a Glyph window, and both are wrong.

The script found them, and it was Mira who judged them. `L T` with −93 could have been right, since the bar of a `T` does go over the foot of an `L`. A measurement of boxes can't say what two shapes do inside their boxes, and that's why the apostrophe had to be left out by hand.

Ines gets out Oskar's sheet. The next open line reads: *Find kerning pairs that are larger than they should be.* The list on the screen is that line done, so she crosses it out: nine of eleven. Finding was the chore. The mending takes the rest of this part.

## What you learned

To take the top of a list, sort it and slice it: `rows[:8]`. A key function that returns a tuple settles ties, and a minus sign in the key turns one part around where `reverse=True` would turn all of them. The size of a kerning value says how far a glyph moves, and the space plus the value says where it ends up. A list like this one points at pairs, and you still have to look at them.

## Try it yourself

1. Print the three pairs in the Regular that are farthest from the top of the size list, with `big[-3:]`. Chapter 10 had that slice too. Are they pairs you'd miss if they were gone? Chapter 75 asks the same question of the whole font.
2. Add `"quotedbl"` and `"asterisk"` to `HIGH` and run the script. Does any count change? Why not? Look at which glyphs Plum's pairs name.
3. Sort the Bold's rows by `space`, smallest first, and print the top eight. These are the pairs where the letters were already close before kerning. Which of them does the `left` list also show?

## Next

The far end of the size list holds pairs of 7 and 8 units. Does anyone see them? Chapter 75 finds the pairs too small to matter and removes them, after a dry run that shows what would go.
