---
this_file: src_docs/md/part4-space/064-spacing-groups.md
---

# 64. Letters that space alike

Thursday of week twelve. Mira has drawn two columns on the back of a proof. Over one she's written *starts like n*, and under it `b h k l m p r`. Over the other, *starts like o*, and under it `c d e g q`. It took her under a minute.

"That's how I think about it," she says. "Not thirty rules. A few families."

Yesterday's dictionary had one entry for each follower: `d` follows `o`, `q` follows `o`, `g` follows `o`. Mira's paper has it the other way up, one entry for each model, with a list of followers. Her way is shorter to write and easier to check by eye. Yesterday's way is what a script needs for looking things up. This chapter keeps both: you write the families, and four lines of Python turn them into the follower map.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `rich` and `tell`.
- The font as chapters 62 and 63 left it: the Bold `m` with 32 on the right, the Bold `i` with 56 on the left, and the Light `d`, `g` and `q` with 50 on the left.

This chapter reads and prints. It changes nothing in the font. I couldn't run it in FontLab 9, and the numbers come from Plum's source file with those three changes applied.

## Step 1: Let the font show its families

Before you write Mira's columns down, see whether the font agrees with her. Go through the lowercase and put each letter into a list with the others that have the same left sidebearing. That's the dictionary of lists from chapter 52, where the key was a base glyph. Here the key is a number:

```python
import halfmoon
from fly import fl

font = fl.CurrentFont()
groups = {}
for name in "abcdefghijklmnopqrstuvwxyz":
    left = halfmoon.rich(font, font[name]).getLSB("Regular")
    if left not in groups:
        groups[left] = []
    groups[left].append(name)

for left in sorted(groups):
    print(left, " ".join(groups[left]))
```

```text
-61 j
1 x
8 v w y
25 t
26 f z
33 s
38 c d e g o q
47 a
60 i
66 u
70 b h k l m n p r
```

`sorted(groups)` gives the keys in order. Asked to sort a dictionary, Python sorts what `in` looks at: the keys.

There they are. The last line is Mira's first column plus the `n` itself. The line for 38 is her second column plus the `o`. She didn't look anything up; the Regular was spaced by somebody who thought the same way.

Now look at the line for 26: `f z`. Those two don't begin alike at all. The `f` starts with a thin crossbar and the `z` with a flat stroke. They happen to have the same number. So a script can find letters that share a value, but it can't tell a family from a coincidence. That knowledge is Mira's, and it has to be written down by a person.

## Step 2: Write the families down

A dictionary again, with the model as the key and the list of followers as the value:

```python
LEFT = {
    "n": ["b", "h", "k", "l", "m", "p", "r"],
    "o": ["c", "d", "e", "g", "q"],
}

print(LEFT["o"])
print(len(LEFT), len(LEFT["n"]))
```

```text
['c', 'd', 'e', 'g', 'q']
2 7
```

Two families, and seven followers in the first. Spread over several lines like this, with a comma after the last entry too, the dictionary reads much as Mira's paper does. Python doesn't mind the line breaks inside the braces, and it doesn't mind the last comma.

The `i` and the `u` aren't in it. In the Regular the `i` has 60 and the `u` has 66, where the `n` has 70. Mira says that's on purpose: a single stem needs a touch less white than a stem with an arch behind it. So they stay out. A family is a decision, and leaving a letter out is a decision too.

## Step 3: The mistake

Chapter 63's script wants the map the other way round: follower first, model second. So turn it. My first try went through the families and stored each model under its followers:

```python
like = {}
for model, members in LEFT.items():
    like[members] = model
```

```text
Traceback (most recent call last):
  File "<string>", line 3, in <module>
TypeError: unhashable type: 'list'
```

"Unhashable" is one of Python's less helpful words. What it means here: a list can't be a key. A dictionary finds its keys fast because it trusts them never to change, and a list can change, with `append` for one. Text, numbers and tuples can be keys. Lists can't.

But the message, odd as it is, points at the real slip. I didn't want the whole list `["b", "h", "k", ...]` to be one key. I wanted seven keys, one for each letter in it. `members` is a list, and I used it as if it were a name.

## Step 4: Turn it round

Seven keys from one list means a loop inside the loop:

```python
like = {}
for model, members in LEFT.items():
    for name in members:
        like[name] = model

print(like)
```

```text
{'b': 'n', 'h': 'n', 'k': 'n', 'l': 'n', 'm': 'n', 'p': 'n', 'r': 'n', 'c': 'o', 'd': 'o', 'e': 'o', 'g': 'o', 'q': 'o'}
```

Twelve entries from two. That's the follower map in the form chapter 63 used, and nobody typed it.

There's a trap left in those four lines, and you know it from yesterday. Suppose Mira, on a tired afternoon, writes the `u` into two families of the same side. The second `like["u"] = ...` would overwrite the first with no error, and which family won would depend on the order of the lines. So check before you store:

```python
like = {}
doubles = []
for model, members in LEFT.items():
    for name in members:
        if name in like:
            doubles.append(name)
        like[name] = model
```

If `doubles` isn't empty at the end, the script should say so and stop. A letter can follow one model on each side, not two.

## Step 5: Who is out of line?

With families written down, one question can be asked of the whole font: which followers don't have their model's value? For one follower and one model, in all three masters:

```python
MASTERS = ["Light", "Regular", "Bold"]
model = halfmoon.rich(font, font["o"])
rich = halfmoon.rich(font, font["c"])

offs = [rich.getLSB(master) - model.getLSB(master) for master in MASTERS]
print(offs)
print(", ".join([f"{off:+}" for off in offs]))
```

```text
[3, 0, 0]
+3, +0, +0
```

The `c` stands 3 units further in than the `o` in the Light, and matches it in the other two.

`{off:+}` is a small new thing for f-strings. The `+` after the colon asks for the sign to be shown always, so 3 prints as `+3`. For a list of differences that's what you want: you see at once which way each one goes.

And `any(offs)` tells you whether there's anything to report. Chapter 44 used `any` on a list of `True` and `False`. On numbers it works the same way, since 0 counts as false and every other number as true.

## The whole script

```python
#FLM: Spacing Groups
# Checks families of letters that should share a sidebearing,
# and prints the follower maps for copy_sb.py.
import halfmoon
from fly import fl

MASTERS = ["Light", "Regular", "Bold"]
LEFT = {
    "n": ["b", "h", "k", "l", "m", "p", "r"],
    "o": ["c", "d", "e", "g", "q"],
}
RIGHT = {
    "n": ["a", "h", "m"],
    "o": ["b", "p"],
    "l": ["d", "g", "q", "u"],
}


def follower_map(families):
    like = {}
    doubles = []
    for model, members in families.items():
        for name in members:
            if name in like:
                doubles.append(name)
            like[name] = model
    return like, doubles


def side_values(font, name, side):
    rich = halfmoon.rich(font, font[name])
    if side == "left":
        return [rich.getLSB(master) for master in MASTERS]
    return [rich.getRSB(master) for master in MASTERS]


def report(font, families, side):
    differ = 0
    for model, members in families.items():
        wanted = side_values(font, model, side)
        print(f"{side} like {model}: " + ", ".join([str(value) for value in wanted]))
        for name in members:
            values = side_values(font, name, side)
            offs = [value - want for value, want in zip(values, wanted)]
            if any(offs):
                differ += 1
                cells = "".join([f"{value:>5}" for value in values])
                print(f"  {name:<3}{cells}   off by " + ", ".join([f"{off:+}" for off in offs]))
    return differ


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    left_like, left_doubles = follower_map(LEFT)
    right_like, right_doubles = follower_map(RIGHT)
    if left_doubles or right_doubles:
        print("In two families of one side:", " ".join(left_doubles + right_doubles))
        return
    names = list(LEFT) + list(RIGHT) + list(left_like) + list(right_like)
    missing = sorted(set([name for name in names if font[name] is None]))
    if missing:
        print("No glyph named:", " ".join(missing))
        return

    differ = report(font, LEFT, "left") + report(font, RIGHT, "right")
    print(f"{differ} of {len(left_like) + len(right_like)} followers differ from their model.")
    print()
    print(f"LEFT_LIKE = {left_like}")
    print(f"RIGHT_LIKE = {right_like}")


main()
```

```text
left like n: 84, 70, 56
left like o: 50, 38, 30
  c     53   38   30   off by +3, +0, +0
  e     48   38   30   off by -2, +0, +0
right like n: 80, 66, 32
  a     80   66   41   off by +0, +0, +9
right like o: 50, 38, 8
  b     53   38    3   off by +3, +0, -5
  p     53   38    3   off by +3, +0, -5
right like l: 84, 70, 34
  d     84   70   29   off by +0, +0, -5
  g     85   70   29   off by +1, +0, -5
  q     84   70   29   off by +0, +0, -5
  u     84   70   36   off by +0, +0, +2
9 of 21 followers differ from their model.

LEFT_LIKE = {'b': 'n', 'h': 'n', 'k': 'n', 'l': 'n', 'm': 'n', 'p': 'n', 'r': 'n', 'c': 'o', 'd': 'o', 'e': 'o', 'g': 'o', 'q': 'o'}
RIGHT_LIKE = {'a': 'n', 'h': 'n', 'm': 'n', 'b': 'o', 'p': 'o', 'd': 'l', 'g': 'l', 'q': 'l', 'u': 'l'}
```

Some notes on the listing.

`follower_map` returns two things, the map and the list of doubles, and `main` takes them apart on one line. The function doesn't print or stop. It hands back what it found and leaves the decision to `main`, as the builder did with its problems in chapter 57.

`list(LEFT)` makes a list of a dictionary's keys, for the same reason `sorted(groups)` sorted them. The line after it collects every name the script is going to look up, models and followers alike, and `set` from chapter 25 drops the repeats before the missing ones are printed.

`report` is called twice, and its two results are added. Each call prints as it goes and returns how many followers were out of line.

The last two lines print a dictionary inside an f-string. Python writes a dictionary out in a form that Python can read back in. So those two lines of output are two lines of a script: you can copy them from the Output panel and paste them over the two constants at the top of `copy_sb.py`. A script has written part of another script. The first exercise does it.

Now read the report the way Mira does, by columns.

The middle column, the Regular, is clean. Every follower sits on its model, on both sides. That's the master Oskar and Mira looked at most.

The Light has small drifts: 3 units, 2 units, 1. They're slips of the hand, and nobody would defend them.

The Bold column is where the numbers get large, and Mira stops there. "Look at the models," she says. The Bold `o` has 30 on its left and 8 on its right. A round letter should be the same on both sides, or near it. The Bold `n` has 56 and 32. The Bold was made by fattening the Regular inside widths that were never looked at again, and the weight grew into the right sidebearings.

So the families can't mend the Bold yet. If you copy from a model that's wrong, you spread the mistake neatly over thirty glyphs. Her decision: use the left families now, where the models are sound in all three masters. Leave the right side of the Bold until its models have been put right. Chapter 67 finds them and chapter 68 changes them.

## What you learned

A dictionary of lists says "these belong to that" in the fewest words, and a loop inside a loop turns it into a dictionary that answers "whom does this one follow?". A list can't be a key, and `TypeError: unhashable type: 'list'` usually means you used a whole list where you meant each thing in it. Grouping by a measured value finds letters that share a number, and it can't tell a family from a coincidence. A copied sidebearing is only as good as its model.

## Try it yourself

1. Copy the `LEFT_LIKE` line from the Output panel into `copy_sb.py` from chapter 63, set `RIGHT_LIKE = {}` there, and run it. You should be offered two layers, the Light `c` (move -3, width 412 to 409) and the Light `e` (move 2, width 451 to 453), and then five accented letters whose widths follow: `ccedilla`, `eacute`, `ecircumflex`, `edieresis` and `egrave`, plus any you built on `c` and `e` in chapter 60. Run `spacing_groups.py` again. The count should be 7 of 21. Later chapters print their numbers for a font without this change, so undo it when you've looked.
2. Put `"u"` into the `"n"` list of `RIGHT` as well as the `"l"` list, and run the script. Then take the check out of `follower_map` and print `right_like["u"]`. Which family won, and why that one?
3. Change step 1 to group by the right sidebearing in the Bold. How many groups have more than one letter? Compare with the Regular, where `d g l q u` share 70. What does the difference tell you about the Bold?

## Next

Copying a sidebearing puts a number in a glyph, and the number goes stale the day the model changes. FontLab can hold the rule itself, as a short piece of text like `=n`, and do the sum whenever it's needed. Chapter 65 writes those rules by script.
