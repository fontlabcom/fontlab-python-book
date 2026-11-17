---
this_file: src_docs/md/part3-shapes/053-build-an-accented-letter.md
---

# 53. Build an accented letter

Wednesday. The publisher has sold the cookbook twice more, to Prague and to Warsaw. Ines forwards the email with one line of her own on top: "Can Plum do Czech and Polish by the end of the month?"

Mira types a Polish word from the sample chapter into a Glyph window: *koń*, a horse. The `k` and the `o` come up. Where the `ń` should be there's a gap.

Chapter 25 saw this coming. Its script compared the characters a language needs with the characters Plum has, and Polish came out short. What's new is that you can now do something about it. You read components yesterday. Today you make a glyph that has them: an `n`, an acute over it, and a shift that puts the acute in the right place. It'll be one glyph, built slowly, and the chapters after this do the rest of the alphabet.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `rich` and `box`.
- The Font window in front when you run the last two steps. The tool that adds glyphs refuses to work while a Glyph window is the active one.

The outputs below were computed from Plum's source file, not copied from FontLab's Output panel. The two refusals you'll read are quoted from the tool's own code.

## Step 1: What's there and what isn't

A new accented letter needs a base and an accent. Ask the font for both, and for the glyph you're about to make. You know from chapter 6 that a name the font doesn't have gives `None`:

```python
from fly import fl

font = fl.CurrentFont()
for name in ["n", "acute", "nacute", "e", "caron", "ecaron"]:
    print(f"{name:<8}{font[name] is not None}")
```

```text
n       True
acute   True
nacute  False
e       True
caron   False
ecaron  False
```

The Polish `ń` can be built today: Plum has the `n` and the acute. The Czech `ě` can't. Its accent, the caron, isn't in the font, and no script will draw a caron that suits Plum. Mira puts "caron" on her own list, under the small caps, and you and I get on with Polish.

The new glyph needs a name and a Unicode value. The name follows the pattern of the 85 glyphs you listed yesterday: base name, then accent name, with nothing between them.

```python
BASE = "n"
MARK = "acute"
CHARACTER = "ń"

name = BASE + MARK
print(name, ord(CHARACTER), f"U+{ord(CHARACTER):04X}")
```

```text
nacute 324 U+0144
```

If you can't type an `ń` on your keyboard, write `chr(324)` in its place. Chapter 23 showed that the two are the same thing.

## Step 2: A first guess

Where does the acute go? The plain answer is "in the middle, over the letter". You can work that out. `halfmoon.box` gives the left and right edge of anything with an outline, and the middle is halfway between them:

```python
import halfmoon


def center(font, name, master):
    left, bottom, right, top = halfmoon.box(font, font[name], master)
    return (left + right) / 2


print(center(font, "n", "Regular"), center(font, "acute", "Regular"))
print(center(font, "n", "Regular") - center(font, "acute", "Regular"))
```

```text
263.5 250.0
13.5
```

The middle of the `n` is at 263.5. The acute, as it's drawn in its own glyph, has its middle at 250. Shift it 13.5 units to the right and the two middles meet.

Before you build anything on that number, test the idea on a letter where you know the right answer. Plum has an `oacute`, and its designer placed that acute by eye. Do the same sum for `o`, and then read what the designer did, with yesterday's functions:

```python
import fly.ap.components.writer as parts
from fly.pens import layer_of

print(center(font, "o", "Regular") - center(font, "acute", "Regular"))
layer = layer_of(halfmoon.rich(font, font["oacute"]).fl, "Regular")
for part in parts.components(layer):
    print(parts.base_of(part), parts.offset(part))
```

```text
10.0
o (0.0, 0.0)
acute (50.0, 0.0)
```

The sum says 10. The designer said 50. That's 40 units apart, and 40 units is a lot for an accent.

The sum is right, and it answers a different question. An acute leans. Its box runs from the bottom-left tip to the top-right end, and the middle of that box is somewhere along the slope. But the eye reads an acute by its lower end, the part that points at the letter. The designer put that end where it looked right. The box knows nothing about it.

A number you can compute is not always the number you want, and the cheap way to find out is to try the sum on a case that's already solved.

## Step 3: Borrow the designer's eye

You can't compute where an acute looks right. But somebody already decided that for the `o`, and the `n` is a similar letter: about as wide, the same height, round on top. So take the decision from the `o` and correct it for the difference between the two letters.

The `n` has its middle 3.5 units to the right of the middle of the `o`: 263.5 against 260. Move the acute by the same 3.5, and it sits over the `n` as it sits over the `o`.

Here's that as two functions. The second has five inputs. That's a lot, and each one is a plain name that says what goes in:

```python
def mark_shift(font, composite, mark, master):
    layer = layer_of(halfmoon.rich(font, font[composite]).fl, master)
    for part in parts.components(layer):
        if parts.base_of(part) == mark:
            return parts.offset(part)
    return None


def shift_like(font, base, model, mark, master):
    dx, dy = mark_shift(font, model + mark, mark, master)
    nudge = center(font, base, master) - center(font, model, master)
    return round(dx + nudge), round(dy)


for master in ["Light", "Regular", "Bold"]:
    print(master, shift_like(font, "n", "o", "acute", master))
```

```text
Light (42, 0)
Regular (54, 0)
Bold (72, 0)
```

`mark_shift` opens a glyph that's already built and finds the shift of one accent in it. `shift_like` calls it for the model, which is `oacute`, built from `model + mark`, the same way you built the new name. Then it adds the nudge.

Read the last line of `shift_like` again: `return round(dx + nudge), round(dy)`. There are two values after `return`, with a comma between them. That hands back a pair, a tuple of two, as `parts.offset` did yesterday. You don't need the parentheses. The comma makes the tuple.

One detail in the numbers. In the Bold, the sum is 70 plus 2.5, and `round(72.5)` gave 72, where school taught you 73. When a number sits halfway between two whole numbers, Python's `round` goes to the even one. So 72.5 becomes 72 and 53.5 becomes 54. For half a unit in a font nobody will mind, but now you know why your pocket calculator disagrees.

## Step 4: Describe the glyph before you make it

In chapter 30 a plan was a list of rows, and the script changed nothing until the plan was complete. Making a glyph works the same way. You write a description, and then you hand the description to a tool that does the work or refuses.

Fly has two small records for the description. Import them with the tool:

```python
import fly.ap.glyphs.creation as creation

part = creation.Part("Regular", "n", 0, 0)
print(part.base, part.x)
```

```text
n 0
```

A `Part` is one component in one master. It has four drawers: `master`, `base`, `x` and `y`. You fill them in that order. For the `ń` you need six parts, an `n` and an acute in each of three masters.

The other record is the glyph:

```python
spec = creation.NewGlyph(
    name="nacute",
    layers=(("Light", 499), ("Regular", 523), ("Bold", 523)),
    unicodes=(324,),
    components=(part,),
)
```

I've filled these slots by name, as chapter 34 showed, because four unnamed things in a row would be hard to read. `layers` holds one pair for each master: its name and the advance width the new glyph gets there. Those are the widths of the `n`. You saw yesterday that a component doesn't bring its width along, so the script has to.

Look at `unicodes=(324,)`. The comma is not a typo. The slot wants a tuple, because a glyph may have several Unicode values. And a tuple with one item needs that comma. Without it, the parentheses are only parentheses:

```python
print((324), (324,))
```

```text
324 (324,)
```

The first is the number 324 with brackets around it, as in arithmetic. The second is a tuple that holds one number. It looks odd.

## Step 5: Make it

Two lines from chapter 29 come back here. The tool wants to know which font file it's working on and what state it's in, and those lines tell it:

```python
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting

package = scripting.current_package()
facts = history.scan_auto_facts(package)
creation.create_glyphs(package, [spec], "Add nacute", facts)
```

`create_glyphs` takes the font, a list of descriptions, a title for the **Edit** menu, and the facts. The list has one item today. The glyph and its components arrive as one step, so one **Edit > Undo** should take the whole glyph away again. That is untested, so check it on your copy before you count on it.

The whole script is below. Run it with the Font window in front, and a new cell appears at the end of the font. Open it, type *koń* in the Glyph window, and look at where the acute sits.

Now run the script a second time, without changing anything:

```text
Traceback (most recent call last):
  ...
ValueError: Refused: nacute exists now. Check the list again.
```

I've cut the middle of the traceback, because most of it is inside Fly and none of it is yours. The last line is the one to read. The tool looked at the font before it touched anything, found a glyph with that name, and stopped. It changed nothing. A `ValueError` is how a function says "the thing you gave me is of the right kind, and I still can't use it".

A refusal is better than a second `nacute` or an overwritten one. A script that greets its user with a traceback could be kinder, though. So the finished script asks first, with the test from step 1, and says in a plain sentence what it found.

## The whole script

Here is `build_one_accent.py`:

```python
# Builds one accented letter from a base glyph and an accent. The accent is
# placed as it is in a model glyph the designer made, nudged by the
# difference between the two base letters.
# Run it with the Font window in front.
import fly.ap.components.writer as parts
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
import fly.ap.glyphs.creation as creation
import halfmoon
from fly import fl
from fly.pens import layer_of

MASTERS = ["Light", "Regular", "Bold"]
BASE = "n"
MARK = "acute"
MODEL = "o"
CHARACTER = "ń"


def center(font, name, master):
    left, bottom, right, top = halfmoon.box(font, font[name], master)
    return (left + right) / 2


def mark_shift(font, composite, mark, master):
    layer = layer_of(halfmoon.rich(font, font[composite]).fl, master)
    for part in parts.components(layer):
        if parts.base_of(part) == mark:
            return parts.offset(part)
    return None


def shift_like(font, base, model, mark, master):
    dx, dy = mark_shift(font, model + mark, mark, master)
    nudge = center(font, base, master) - center(font, model, master)
    return round(dx + nudge), round(dy)


def width_of(font, name, master):
    layer = layer_of(halfmoon.rich(font, font[name]).fl, master)
    return round(layer.advanceWidth)


def main():
    font = fl.CurrentFont()
    name = BASE + MARK
    if font[name] is not None:
        print(f"{name} is already in the font. Nothing done.")
        return
    for needed in [BASE, MARK, MODEL, MODEL + MARK]:
        if font[needed] is None:
            print(f"There's no {needed} in the font. Nothing done.")
            return

    layers = []
    components = []
    for master in MASTERS:
        dx, dy = shift_like(font, BASE, MODEL, MARK, master)
        layers.append((master, width_of(font, BASE, master)))
        components.append(creation.Part(master, BASE, 0, 0))
        components.append(creation.Part(master, MARK, dx, dy))
        print(f"{master:<9}{BASE} 0 0, {MARK} {dx} {dy}")

    spec = creation.NewGlyph(
        name=name,
        layers=tuple(layers),
        unicodes=(ord(CHARACTER),),
        components=tuple(components),
    )
    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    creation.create_glyphs(package, [spec], f"Add {name}", facts)
    print(f"Added {name}, U+{ord(CHARACTER):04X}.")


main()
```

```text
Light    n 0 0, acute 42 0
Regular  n 0 0, acute 54 0
Bold     n 0 0, acute 72 0
Added nacute, U+0144.
```

Run it again:

```text
nacute is already in the font. Nothing done.
```

Three things in `main` are worth a second look.

A bare `return` in the middle of a function leaves the function at once and hands back nothing. That's how `main` stops early without a tower of `if` and `else`. Check what could stop you, leave if it does, and the rest of the function can assume that all is well.

The script collects the layers and components in lists, because lists can grow, and turns them into tuples at the end with `tuple(...)`. That's the reverse of `list(...)` from chapter 51.

And the four capital-letter names at the top are the whole recipe. Change `BASE`, `MODEL` and `CHARACTER`, and the script builds a different letter.

Mira types *koń* again. The acute sits over the `n` about where it sits over the `o` next to it, in all three weights. She nudges nothing. Then she remembers that the Polish word for "horses" starts a sentence in the sample chapter, and that Plum has no capital `Ń` either.

## What you learned

A new accented letter is a description before it's a glyph: a name, a width for each master, a Unicode value, and one `Part` for each component in each master. `create_glyphs` turns the description into a glyph in one step, and refuses with a `ValueError` when it can't. A sum is worth testing on a case you already know, and where a sum can't see what the eye sees, you can borrow a decision the designer made and adjust it. A function can hand back two values with a comma, a one-item tuple needs its comma, and a bare `return` leaves a function early.

## Try it yourself

1. Build the capital. Set `BASE = "N"`, `MODEL = "O"` and `CHARACTER = "Ń"`, and predict the last number in each line before you run it. Where does that number come from? You met it yesterday.
2. Build `sacute` with `o` as the model, and look at it in all three weights. The Light gets a shift of −40. Does the acute look right over a letter as narrow as `s`, or has the model been stretched too far? Write down what you'd change by hand. Chapter 54 comes back to this.
3. Set `MARK = "caron"` and run the script. Read the sentence it prints. Then take away the loop over `needed`, run it again, and read what Python says in its place. Which message would you rather get from a colleague's script?

## Next

Typing a shift for every accent over every letter doesn't scale, and borrowing from a model only works while the letters are alike. Chapter 54 looks at anchors: named points that a glyph carries so that accents can find their own place.
