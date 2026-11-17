---
this_file: src_docs/md/part4-space/065-metrics-expressions.md
---

# 65. Rules that FontLab keeps

Friday of week twelve. Mira has been looking at the Light `o` all morning and wants 2 more units of white on its left. That's a small change to one glyph. It's also the end of Wednesday's work: the `d`, the `g` and the `q` were given the number 50 because the `o` had 50, and when the `o` has 52 they'll still have 50.

You could run `copy_sb.py` again, and it would put them right. But somebody has to remember to run it, every time a model changes, for as long as the font lives. Oskar remembered. Then Oskar left.

FontLab has a way to store the rule in place of the number. Each layer has three small text fields, one for the left side, one for the right, one for the width. Leave a field empty and the number is yours to set. Write `=o` into the left one and you've told FontLab that this glyph's left side is whatever the `o`'s is. FontLab calls these linked metrics, and what you write in the field is a metrics expression.

For Python, the expression is a string. Python doesn't know what `=o` means and doesn't need to. Your script builds a piece of text, hands it over, and FontLab reads it. So this chapter is about building strings with care, for a reader that isn't a person.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed, and the Font window in front.
- `halfmoon.py` with `rich`, `ask` and `tell`.
- The `LEFT_LIKE` line that `spacing_groups.py` printed in chapter 64.

This chapter changes the font, in one Undo step. I couldn't run it in FontLab 9. I can show you what the script stores. What FontLab then does with it, and when, I've read about and not seen. Step 5 is a check for that, and you should trust the check over my description.

## Step 1: Read the three fields

The fields are called `metricsLeft`, `metricsRight` and `metricsWidth`, and they belong to the layer:

```python
import halfmoon
from fly import fl
from fly.pens import layer_of

font = fl.CurrentFont()
layer = layer_of(halfmoon.rich(font, font["g"]).fl, "Light")
print([str(layer.metricsLeft), str(layer.metricsRight), str(layer.metricsWidth)])
```

```text
['', '', '']
```

Three empty strings. Plum has no linked metrics anywhere; I checked its source file.

Two small habits in that line. `str(...)` around each field makes sure you have ordinary Python text, whatever kind of text FontLab hands back. And the three values are printed inside a list. Printed on its own, an empty string shows as nothing at all, and you can't tell it from a line that didn't print. Inside a list it shows with its quotes.

An empty string counts as false, as an empty list does. So "has this layer any rule?" is a short question:

```python
print(any([str(layer.metricsLeft), str(layer.metricsRight), str(layer.metricsWidth)]))
```

```text
False
```

## Step 2: Write one rule

Chapter 64's report had one odd line in the Light: the `g` has 85 on its right where the `l`, its model, has 84. One unit. Give the `g` a rule for it:

```python
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting

rich = halfmoon.rich(font, font["g"])


def change():
    layer.metricsRight = "=l"


package = scripting.current_package()
facts = history.scan_auto_facts(package)
history.commit("Link metrics", [layer], [rich.fl], change,
               operation="geometry", facts=facts, allow_bases=True)

print([str(layer.metricsLeft), str(layer.metricsRight), str(layer.metricsWidth)])
print(rich.getLSB("Light"), rich.getAdvance("Light"), rich.getRSB("Light"))
```

The commit carries `allow_bases=True` because `gbreve` borrows the `g`, as chapter 55 explained. Save the font first. The first `print` will show the rule in its place:

```text
['', '=l', '']
```

The second is the one I can't show you. If FontLab has worked the rule out at once, you'll see `50 519 84`: the right side has come down from 85 to 84 and the width with it. If you see `50 520 85`, the rule is stored and the sum hasn't been done yet. Open the `g` in a Glyph window, look at the Metrics table, and run the last line again.

A word on what `=l` means in that field. The expression is in the *right* field and names a glyph, and as far as I've been able to read, that means the same side of the named glyph: the right sidebearing of the `l`. In the left field `=l` would mean its left sidebearing. In the width field it would mean its advance width.

The equals sign is part of the text. The scripts I've read all write it, and I'd write it always.

The Light `g` now carries this rule, and nothing later in the part needs it. Take it off again: put `""` in place of `"=l"` in `change` and run the lines once more.

To take a rule away, store the empty string: `layer.metricsRight = ""`. The number that's there stays.

## Step 3: The mistake

The `u` was left out of the `n` family in chapter 64, on purpose. Its left side isn't the `n`'s. But look at the two in all three masters: 80 and 84 in the Light, 66 and 70 in the Regular, 52 and 56 in the Bold. The `u` stands 4 units closer than the `n` every time. That's a rule too, and an expression can say it: `=n-4`.

To build that text from a model's name and a number, I tried the obvious thing:

```python
model = "n"
extra = -4
text = "=" + model + extra
```

```text
Traceback (most recent call last):
  File "<string>", line 3, in <module>
TypeError: can only concatenate str (not "int") to str
```

Python won't glue a number onto text. It's the refusal you met in Part 1, and an f-string cures it: it turns the number into text for you.

```python
print(f"={model}{extra}")
```

```text
=n-4
```

That looks right, and it's right by luck. The minus sign came with the number. Try it with 10:

```python
extra = 10
print(f"={model}{extra}")
```

```text
=n10
```

No error this time, and that's worse. `=n10` is a perfectly good string. To FontLab it would be a rule about a glyph called `n10`, which Plum doesn't have. A person reading `n10` might guess what you meant. A program reads what's there.

## Step 4: Build the text properly

Chapter 64 had the tool for this: `{extra:+}` prints a number with its sign, always.

```python
for extra in [10, -4, 0]:
    print(f"={model}{extra:+}")
```

```text
=n+10
=n-4
=n+0
```

The first two are what you want. The third works as a sum but reads badly, and Mira will be reading these in the Metrics table for years. So make the plain case plain, in a function of its own:

```python
def rule(model, extra):
    if extra == 0:
        return f"={model}"
    return f"={model}{extra:+}"


print(rule("n", 10), rule("n", -4), rule("o", 0))
```

```text
=n+10 =n-4 =o
```

There's a habit worth taking from this. When a script writes text for another program to read, put the writing in one small function and try it on the awkward cases before you use it: a positive number, a negative one, zero. A slip in a sentence for a person costs a frown. A slip here goes into thirty-nine layers without a sound.

## Step 5: Ask the font whether the rules hold

You can't see into FontLab's arithmetic, but you can do the same sum yourself and compare. For each follower, the number its rule should give is the model's left sidebearing plus the extra:

```python
LEFT_LIKE = {"c": "o", "e": "o", "u": "n"}
LEFT_EXTRA = {"u": -4}

for name, model in LEFT_LIKE.items():
    want = halfmoon.rich(font, font[model]).getLSB("Light") + LEFT_EXTRA.get(name, 0)
    have = halfmoon.rich(font, font[name]).getLSB("Light")
    print(name, have, want, f"{have - want:+}")
```

```text
c 53 50 +3
e 48 50 -2
u 80 80 +0
```

`LEFT_EXTRA.get(name, 0)` is the `get` from chapter 22: the extra if there is one, and 0 for everybody else. Only the exceptions need writing down.

If you did the first exercise of chapter 64, the `c` and the `e` are at 50 already and all three lines end in `+0`.

Run this before you write the rules and again after. Before, it tells you which glyphs will move. After, it tells you whether they did.

## The whole script

```python
#FLM: Link Metrics
# Stores a left-sidebearing rule such as =n or =n-4 in each follower,
# in every master, and checks whether the numbers agree with the rules.
import halfmoon
import fly.ap.core.history.glyphs as history
import fly.ap.core.scripting as scripting
from fly import fl
from fly.pens import layer_of

MASTERS = ["Light", "Regular", "Bold"]
LEFT_LIKE = {'b': 'n', 'h': 'n', 'k': 'n', 'l': 'n', 'm': 'n', 'p': 'n', 'r': 'n', 'c': 'o', 'd': 'o', 'e': 'o', 'g': 'o', 'q': 'o', 'u': 'n'}
LEFT_EXTRA = {"u": -4}
CLEAR = False


def rule(model, extra):
    if extra == 0:
        return f"={model}"
    return f"={model}{extra:+}"


def link_rows(font):
    rows = []
    for name, model in LEFT_LIKE.items():
        text = "" if CLEAR else rule(model, LEFT_EXTRA.get(name, 0))
        rich = halfmoon.rich(font, font[name])
        for master in MASTERS:
            layer = layer_of(rich.fl, master)
            if str(layer.metricsLeft) != text:
                rows.append((rich, layer, text))
    return rows


def off_rule(font):
    lines = []
    for name, model in LEFT_LIKE.items():
        rich = halfmoon.rich(font, font[name])
        base = halfmoon.rich(font, font[model])
        for master in MASTERS:
            off = rich.getLSB(master) - base.getLSB(master) - LEFT_EXTRA.get(name, 0)
            if off != 0:
                lines.append(f"  {name:<4}{master:<9}{off:+}")
    return lines


def show_off(font):
    lines = off_rule(font)
    print(f"{len(lines)} of {len(LEFT_LIKE) * len(MASTERS)} layers are off their rule.")
    for line in lines:
        print(line)


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    names = list(LEFT_LIKE) + list(LEFT_LIKE.values())
    missing = sorted(set([name for name in names if font[name] is None]))
    if missing:
        halfmoon.tell(f"No glyph named: {' '.join(missing)}")
        return

    rows = link_rows(font)
    texts = {}
    owners = {}
    for rich, layer, text in rows:
        texts[rich.name] = text
        owners[rich.name] = rich.fl
    for name, text in texts.items():
        print(f"{name:<4}left  {text}")
    print(f"{len(rows)} layers to change.")
    show_off(font)
    if not rows or not halfmoon.ask(f"Store rules in {len(rows)} layers?"):
        return

    def change():
        for rich, layer, text in rows:
            layer.metricsLeft = text

    package = scripting.current_package()
    facts = history.scan_auto_facts(package)
    layers = [layer for rich, layer, text in rows]
    history.commit("Link metrics", layers, list(owners.values()), change,
                   operation="geometry", facts=facts, allow_bases=True)
    show_off(font)


main()
```

The first part of what it prints I'm sure of:

```text
b   left  =n
h   left  =n
k   left  =n
l   left  =n
m   left  =n
p   left  =n
r   left  =n
c   left  =o
d   left  =o
e   left  =o
g   left  =o
q   left  =o
u   left  =n-4
39 layers to change.
2 of 39 layers are off their rule.
  c   Light    +3
  e   Light    -2
```

Thirteen followers in three masters make 39 layers. Answer Yes, and the script stores the rules and asks the font again. If FontLab has done its sums by then, the last line is:

```text
0 of 39 layers are off their rule.
```

If it still says 2, the rules are in and the numbers haven't caught up. Open the Light `c` in a Glyph window, look at its left field in the Metrics table, where `=o` should stand, and run the script again. It will find nothing to store, print `0 layers to change.` and report the count once more. Tell me which of the two you saw; it's one of the things in this book I most want to know.

Some notes on the listing.

`LEFT_LIKE` is the line chapter 64 printed, pasted in, with the `u` added by hand at the end. `LEFT_EXTRA` holds the one exception.

`link_rows` skips a layer whose field already holds the right text. That's what makes a second run harmless, and it's the same idea as the builder in chapter 56 that left good glyphs alone.

`texts` and `owners` are both dictionaries used to keep one of each: three rows for the `b`, one line in the list, one glyph for the Undo step.

`CLEAR = True` turns the script into its own opposite. Every rule becomes the empty string, and the layers that hold a rule get it taken away. When you write a script that sets something up, it's worth a line or two to let it take the same thing down.

The rules are for the left side only. Mira's decision from yesterday stands: the right-hand models in the Bold aren't fit to follow yet.

Now the thing Mira wanted this morning. She gives the Light `o` 2 more units on the left, with `set_sb.py` from chapter 62. If the rules work as they should, the `c`, the `d`, the `e`, the `g` and the `q` go with it, and nobody has to remember anything. She runs the script afterwards to see. `0 of 39 layers are off their rule.` is the line she'll look for from now on, and any other count names the layers to look at.

One warning to carry forward. A layer with a rule doesn't take orders about numbers. If you run `set_sb.py` on the Light `d` now and ask for 60 on the left, the number and the rule disagree, and I can't tell you which wins. The careful tools in `fly.ap` step around linked layers for that reason, and chapter 68 will meet them. Change the model, or change the rule.

## What you learned

A layer has three text fields, `metricsLeft`, `metricsRight` and `metricsWidth`: empty means no rule, and `=n` or `=n-4` is a rule FontLab works out from another glyph. Your script only builds the text, so `{extra:+}` keeps the sign, and a small function tried on a positive number, a negative one and zero catches `=n10` before it reaches the font. A dictionary with `.get(name, 0)` holds only the exceptions. When you can't see how another program does its sum, do the sum yourself and compare.

## Try it yourself

1. Before you run the script, guess what `rule("H", 0)`, `rule("H", 12)` and `rule("H", -12)` give. Then print them.
2. The `i` isn't in a family either. Compare its left side with the `n`'s in all three masters. After chapter 62 you should find 74 and 84, 60 and 70, 56 and 56. Can one rule of the form `=n-10` serve all three? What would it do to the Bold, and is that what Mira asked for on Tuesday?
3. Set `CLEAR = True`, run the script, and read the three fields of the Light `c` as in step 1. Then set it back to `False` and run again. How many Undo steps did the two runs make?

## Next

The publisher's price list is set in Plum, and its columns of figures look uneven, though all ten figures have the same width. Chapter 66 finds out why and centers each figure in its box.
