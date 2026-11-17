---
this_file: src_docs/md/part4-space/069-what-kerning-is.md
---

# 69. What kerning is

Thursday of week thirteen. The sidebearings are in order, and Mira wants to see what they can do on their own. She sets a headline from the catalog, `AVOCADO TOAST`, and switches the kerning off in the layout program.

She winces. Between the `A` and the `V` there's a hole you could park a bicycle in. Between the `T` and the `O` there's another. The letters `C`, `A`, `D` sit together like strangers on a bench.

Nothing is wrong with the sidebearings. A sidebearing is one number for one side of one letter, and it has to serve next to every neighbor the letter will ever have. The `A` leans away from the letter on its right. Next to an `H`, that's fine: the `H` stands straight and the space between them is an honest wedge. Next to a `V`, which leans the same way, the two slopes run side by side and the wedge becomes a channel.

No value for the `A`'s right side can be right for both. So a font keeps a second list, of exceptions: for this letter followed by that one, move them this much closer, or this much further apart. That list is the font's kerning, and one line of it is a kerning pair.

Today you read the list. You change nothing.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `rich` and `tell`.

I couldn't run today's code in FontLab 9. The pairs and values come from Plum's source file, and your font should print the same. The practice font's kerning hasn't been touched by any chapter so far.

## Step 1: What the sidebearings give

Start with the hole. The gap between two letters is the right side of the first plus the left side of the second, as in chapter 61:

```python
import halfmoon
from fly import fl

def gap(font, first, second, master):
    one = halfmoon.rich(font, font[first])
    two = halfmoon.rich(font, font[second])
    return one.getRSB(master) + two.getLSB(master)


font = fl.CurrentFont()
print(gap(font, "H", "H", "Regular"))
print(gap(font, "A", "V", "Regular"))
```

```text
146
21
```

Read those two with care, because they seem to say the opposite of what Mira saw. Two `H`s have 146 units between them, and `A` and `V` have 21, a seventh of that. And the `AV` is the pair that looks too open.

The number measures the wrong thing. A sidebearing runs from the edge of the letter's box to the outermost point of the drawing. For an `H` the outermost point is a stem, top to bottom, and 146 units is what you see. For an `A` the outermost point is the tip of a foot, down on the baseline. The `V`'s is the tip of an arm, up at the cap height. Those two tips are 21 units apart, sideways. But one is at the bottom and the other at the top, and between them runs a white stripe as wide as the letters lean.

The eye judges the white area between two letters. It doesn't measure the nearest points. Stems make the two agree, which is why chapters 61 to 68 could work with plain numbers. Diagonals, overhangs and round shapes pull them apart, and those are the letters a kerning list is full of.

## Step 2: Read the list

The font keeps one kerning list for each master. `kerning_pairs` reads one of them:

```python
import fly.ap.core.scripting as scripting

package = scripting.current_package()
pairs = scripting.kerning_pairs(package, "Regular")
print(len(pairs))
```

```text
106
```

`scripting.current_package()` you've used since chapter 29, each time as the first half of an Undo step. Here it's the way in. Kerning belongs to the font as a whole and not to any glyph, so you ask the font's package for it.

106 pairs. That's a small list. A text face from a big foundry may carry several thousand. Plum is a display face with a short alphabet, and somebody kerned it by hand, pair by pair.

## Step 3: Ask for a pair

`pairs` is a dictionary. The value is a number of units. The key has to name two glyphs at once, and you know from chapter 64 what can and can't be a key: a list can't, and a tuple can. So the key is a tuple of two names:

```python
print(pairs[("A", "V")])
```

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
KeyError: ('A', 'V')
```

That's today's mistake, and it's an instructive one. `KeyError` is chapter 21's complaint: no such key. Yet Mira saw with her own eyes that the font tightens `AV` when the kerning is on. The pair has to be there.

When a dictionary says a key is missing and you're sure it isn't, look at the keys it does have:

```python
for pair in sorted(pairs)[:6]:
    print(pair)
```

```text
('@L_A', '@R_C')
('@L_A', '@R_O2')
('@L_A', '@R_U2')
('@L_A', '@R_W2')
('@L_A', '@R_Y2')
('@L_A', '@R_wacute')
```

Tuples of two, as I said. `sorted` puts tuples in order by their first item and, among equals, by their second, and `@` comes before the letters. But these aren't glyph names. Plum has no glyph called `@L_A`.

A name that starts with `@` stands for a group of glyphs that kern alike. The font's makers called this one `L_A`, and from the name you can guess what's in it: the `A`, as the left-hand letter of a pair, and probably its accented forms. Such a group is a kerning class. One pair with a class in it does the work of many plain pairs. Chapter 71 opens the classes up. For today, treat `@L_A` as "the `A` and its relatives, standing first".

Now you can find the pair. Ask for every key whose second half is `V`:

```python
print(sorted([pair for pair in pairs if pair[1] == "V"]))
```

```text
[('@L_A', 'V'), ('L', 'V'), ('R', 'V')]
```

Three pairs end in `V`: one for the `A` family, one for `L` and one for `R`. `pair[1]` is the second item of the tuple, since a tuple is indexed like a list.

```python
print(pairs[("@L_A", "V")])
```

```text
-55.0
```

There it is. Negative means closer: when a `V` follows an `A`, the font moves the `V` 55 units to the left. The value is a decimal number, like a width, and for the same reason. FontLab stores its measurements that way.

So the real distance between the tips is 21 minus 55, which is −34. The foot of the `A` reaches 34 units under the arm of the `V`. On the page that looks right. The boxes overlap and the drawings don't touch.

## Step 4: Walk the whole list

A dictionary hands you key and value together through `.items()`, as in chapter 22. Here each key is itself a pair, and you can unpack it in the same line by putting it in parentheses:

```python
for (first, second), value in sorted(pairs.items())[:4]:
    print(f"{first:<14}{second:<12}{value:>5.0f}")
```

```text
@L_A          @R_C          -13
@L_A          @R_O2          -7
@L_A          @R_U2         -20
@L_A          @R_W2         -41
```

`(first, second), value` mirrors the shape of what comes out: a tuple of two, then a number. Leave the parentheses off and Python expects three things, finds two, and complains.

Alphabetical order is fine for looking something up, and it tells you little about the font. Order by value says more. Chapter 36's key function does that. Each item is a `(pair, value)` couple, so the value is item 1:

```python
def by_value(item):
    return item[1]


for (first, second), value in sorted(pairs.items(), key=by_value)[:3]:
    print(first, second, value)
```

```text
L T -113.0
quoteright @R_eacute -112.0
quoteright @R_oacute -112.0
```

The tightest pair in the Regular is `LT`, at 113 units. Think of the shapes: the `L` has an empty corner at top right and the `T` an empty corner at bottom left, and the two fit like a hand in a glove. Then come the apostrophe pairs, `quoteright` before a small round letter, as in `l'eau`.

## The whole script

```python
#FLM: List Kerning
# Reports the kerning pairs of one master: how many, the tightest, the loosened.
import halfmoon
import fly.ap.core.scripting as scripting

MASTER = "Regular"
HOW_MANY = 8


def by_value(item):
    return item[1]


def show(title, items):
    print(title)
    for (first, second), value in items:
        print(f"  {first:<14}{second:<12}{value:>5.0f}")


def busiest(pairs):
    tally = {}
    for first, second in pairs:
        tally[first] = tally.get(first, 0) + 1
    return sorted(tally.items(), key=by_value, reverse=True)


def main():
    package = scripting.current_package()
    if package is None:
        halfmoon.tell("Open a font first.")
        return
    pairs = scripting.kerning_pairs(package, MASTER)
    if not pairs:
        print(f"No kerning in {MASTER}.")
        return

    ordered = sorted(pairs.items(), key=by_value)
    looser = [item for item in ordered if item[1] > 0]
    print(f"{len(pairs)} pairs in {MASTER}: {len(pairs) - len(looser)} tighten, {len(looser)} loosen.")
    show(f"The {HOW_MANY} tightest:", ordered[:HOW_MANY])
    show("Loosened:", looser)
    print("Most pairs begin with:")
    for first, count in busiest(pairs)[:3]:
        print(f"  {first:<14}{count:>3}")


main()
```

Save it as `list_kerning.py`. On Plum it prints:

```text
106 pairs in Regular: 102 tighten, 4 loosen.
The 8 tightest:
  L             T            -113
  quoteright    @R_eacute    -112
  quoteright    @R_oacute    -112
  quoteright    c            -112
  quoteright    ccedilla     -112
  quoteright    d            -112
  quoteright    e            -112
  quoteright    g            -112
Loosened:
  questiondown  exclamdown     11
  r             @R_yacute      14
  r             y              14
  t             quoteright     14
Most pairs begin with:
  quoteright     25
  T              14
  @L_A           11
```

The order among the seven pairs at −112 may not be this one. `sorted` keeps equal items in the order it met them, and I can't tell you from here in which order FontLab hands the pairs over. If yours come out shuffled, the font is the same.

A few notes on the listing.

`for first, second in pairs:` loops over the dictionary itself, which gives the keys. Each key is a tuple of two, and the loop unpacks it. No parentheses are needed this time, because there's no value alongside.

`by_value` serves twice. An item from `pairs.items()` is `(pair, value)` and an item from `tally.items()` is `(name, count)`. In both, item 1 is the number to sort by. The function doesn't care what item 0 is.

`if not pairs:` is the empty test of chapter 35. An empty dictionary counts as false, as an empty list does.

## Reading the report

**102 tighten, 4 loosen.** Kerning is nearly always a matter of closing holes. The four that open something up are worth knowing. `r` before `y`: the arm of the `r` and the arm of the `y` would touch. `t` before an apostrophe, as in `don't`: the same. And the two Spanish opening marks, `¿¡`, which would otherwise sit too close.

**Most pairs begin with `quoteright`.** A quarter of the list is about the apostrophe. It's a small mark hung high in a wide box, with empty space under it, and every low letter that follows needs pulling in.

**Then `T` and the `A` family.** An overhang and a diagonal: the two kinds of shape from step 1.

Mira reads down the report with the headline in front of her. `AV`: there, −55. `TO`? She runs the search from step 3 with `pair[0] == "T"` and finds fourteen pairs, with `a`, `e`, `o`, `u`, `w`, `y` and some classes, and none with a capital `O`. She tries the classes: nothing named `@R_O2` after `T` either. So the hole she saw between `T` and `O` isn't a pair that got switched off. It was never kerned.

"How do I know that for sure?" she asks. "I looked for `('A', 'V')` and that wasn't there either, and it was kerned all along."

It's a fair question, and today's tools can't answer it. To say what the font does for a given pair of letters, you have to know which classes each letter belongs to and try every combination. FontLab has a call that does that, and it's tomorrow's first line.

## What you learned

A sidebearing has to serve every neighbor, and kerning is the list of exceptions for particular pairs. `scripting.kerning_pairs(package, master)` gives one master's pairs as a dictionary whose keys are tuples of two names and whose values are units, negative for closer. A tuple can be a key where a list can't, and `for (first, second), value in pairs.items():` unpacks key and value in one line. A name starting with `@` is a kerning class, a group that stands in for its members.

## Try it yourself

1. Change `MASTER` to `"Light"` and then to `"Bold"`. You should get 100 pairs and 102. Then print the pairs that begin with `@L_A` in each of the two, side by side. Ten of the eleven values are the same. A Bold and a Light don't want the same kerning. What does that suggest about how the Bold's list was made?
2. Write a loop that prints every pair whose first half is `T`, with its value, tightest first. There are fourteen. Which is tighter in the Regular: `T` before `a`, or `T` before `@R_aacute`? Keep your answer for chapter 71.
3. Yesterday you gave the Bold `A` a right side of 9 where it had −33. Every Bold pair that begins with the `A` family was made for the old value. Print them. How many are there, and what would you have to do to each value to put the letters back where they stood on Tuesday? Don't do it. Chapter 79 comes back to this.

## Next

Mira's question stands: what does the font do for `T` and `O`, or for `T` and `ó`, when the pair you look up isn't in the list under that name? Chapter 70 asks FontLab for the value that applies, and puts it next to the value that's written down.
