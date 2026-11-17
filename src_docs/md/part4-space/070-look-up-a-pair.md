---
this_file: src_docs/md/part4-space/070-look-up-a-pair.md
---

# 70. Look up a pair

Friday of week thirteen. Ines is laying out the drinks page of the catalog and calls across the room: "What's `T o` at the moment?"

It's the kind of question a studio asks ten times a day, and it deserves an answer in ten seconds. Yesterday's report can't give one. It reports on a hundred pairs and leaves the looking to you. And Mira's own question from yesterday is still open: she looked for `A` and `V`, got a `KeyError`, and the pair was kerned all along, under another name.

Today's script takes two glyph names and says what the font does with them, in every master, and where the value comes from.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `ask_text` and `tell`.

Nothing is changed today. I couldn't run the code in FontLab 9. The values come from Plum's source file, with the classes worked out by hand, so today's outputs lean on one assumption: that FontLab looks a pair up the way step 2 describes: the two glyphs first, then their classes.

## Step 1: A quiet wrong answer

Yesterday's `KeyError` was at least honest. Chapter 22 showed a way around it: `get`, with a value to hand back when the key is missing.

```python
import fly.ap.core.scripting as scripting

package = scripting.current_package()
pairs = scripting.kerning_pairs(package, "Regular")
print(pairs.get(("T", "o"), 0))
print(pairs.get(("A", "V"), 0))
```

```text
-84.0
0
```

That's today's mistake, and there's no traceback to warn you. The first answer is right. The second is wrong: `AV` is kerned by 55 units, as you found yesterday. The dictionary holds that pair under `("@L_A", "V")`, so the lookup under `("A", "V")` misses, and `get` covers the miss with a polite 0.

A script built on that line would tell Ines that `AV` isn't kerned. She'd believe it, because 0 looks like an answer.

The default in `get` is a fine tool when a missing key truly means nothing, as in chapter 22's tally: a letter you haven't counted yet has a count of 0. Here a missing key means "not written under these two names", which is a different thing from "no kerning". When a miss and a zero mean different things, don't let `get` paint one over the other. Leave the default off:

```python
print(pairs.get(("A", "V")))
```

```text
None
```

`get` with no second value hands back `None` for a miss. Now the miss is visible, and it can't be mistaken for a number.

## Step 2: Ask the font what applies

The dictionary from `kerning_pairs` is a copy of what's written down. FontLab itself keeps the list in its own form, and that one knows about the classes. You reach it through the package:

```python
kerning = package.kerning("Regular")
print(scripting.kerning_pair_value(kerning, "A", "V"))
print(scripting.kerning_pair_value(kerning, "Aacute", "V"))
print(scripting.kerning_pair_value(kerning, "T", "O"))
```

```text
-55.0
-55.0
0
```

`package.kerning("Regular")` is the Regular's kerning as FontLab holds it. `kerning_pair_value` asks it one question: when this glyph is followed by that one, how far does the second move? FontLab looks for a pair written for the two glyphs themselves. If there's none, it tries the classes they belong to. If nothing fits, the answer is 0.

So `A` before `V` gives −55, through the class `@L_A`. `Aacute` before `V` gives the same, because `Á` is in that class too. Nobody ever wrote a pair for `Á` and `V`, and the font has one anyway. That's what classes are for.

And `T` before `O` gives 0. This time the zero can be trusted. It doesn't come from a missing key. It comes from FontLab, after it tried every way of reading the pair. Mira's hole between `T` and `O` was never kerned, and now she knows it for sure.

You now have two answers for every pair, and they're both worth having:

- **what's written**, from `pairs.get((first, second))`: a number, or `None`;
- **what applies**, from `kerning_pair_value`: always a number.

## Step 3: Put the two together

Three cases can come out, and each one tells you where to go if you want to change the value:

```python
def source(written, applies):
    if written is not None:
        return "its own pair"
    if applies != 0:
        return "through a class"
    return "not kerned"


for first, second in [("T", "o"), ("A", "V"), ("T", "O")]:
    written = pairs.get((first, second))
    applies = scripting.kerning_pair_value(kerning, first, second)
    print(first, second, applies, source(written, applies))
```

```text
T o -84.0 its own pair
A V -55.0 through a class
T O 0 not kerned
```

The order of the two tests matters. A pair that's written gets the first answer, even if its value is 0, because somebody can write a zero on purpose: "this pair gets nothing, whatever its class says". The test is `is not None`, and not `if written:`, for that very reason. An `if` treats the number 0 as false, the way it treats `None`. A written zero would slip through `if written:` and be reported as not written.

One honest gap: if a class pair itself has the value 0, `source` calls it "not kerned". On Plum there is no such pair, and the next chapter gives you the means to tell the two apart.

## Step 4: Names from a text field

The script should ask which glyphs you mean. `ask_text` gives back one piece of text, and you need two names, or more. Chapter 9 split a name at its dots with `split(".")`. With nothing in the parentheses, `split` cuts at every run of spaces:

```python
print("T o".split())
print("  T   oacute n i c a ".split())
```

```text
['T', 'o']
['T', 'oacute', 'n', 'i', 'c', 'a']
```

Extra spaces at the ends or in the middle do no harm. That's a kindness to whoever types.

These are glyph names, not letters. Mira types `T ó` the first time, and the script has to say something better than a traceback, because the font has no glyph called `ó`. Its name is `oacute`. So check every name before asking the font anything:

```python
from fly import fl

font = fl.CurrentFont()
names = "T ó".split()
unknown = [name for name in names if font[name] is None]
print(unknown)
```

```text
['ó']
```

With more than two names you get a chain: each glyph with the one after it. Chapter 61 did that with `zip(word, word[1:])`, and it works the same on a list of names.

## The whole script

```python
#FLM: Pair Value
# Says what kerning applies between the glyphs you name, in every master.
import halfmoon
import fly.ap.core.scripting as scripting
from fly import fl

MASTERS = ["Light", "Regular", "Bold"]


def source(written, applies):
    if written is not None:
        return "its own pair"
    if applies != 0:
        return "through a class"
    return "not kerned"


def look(package, master, first, second):
    pairs = scripting.kerning_pairs(package, master)
    kerning = package.kerning(master)
    written = pairs.get((first, second))
    applies = scripting.kerning_pair_value(kerning, first, second)
    return applies, source(written, applies)


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    text = halfmoon.ask_text("Glyph names, with spaces between:", "T o")
    if text is None:
        return
    names = text.split()
    unknown = [name for name in names if font[name] is None]
    if unknown:
        halfmoon.tell(f"No glyph named {', '.join(unknown)}. Use glyph names, as in oacute.")
        return
    if len(names) < 2:
        halfmoon.tell("I need at least two glyph names.")
        return

    package = scripting.current_package()
    for first, second in zip(names, names[1:]):
        print(first, second)
        for master in MASTERS:
            applies, where = look(package, master, first, second)
            print(f"  {master:<9}{applies:>5.0f}   {where}")


main()
```

Save it as `pair_value.py`. Run it and click OK on the `T o` that's already in the field:

```text
T o
  Light      -55   its own pair
  Regular    -84   its own pair
  Bold      -108   its own pair
```

"Minus 84 in the Regular," Mira calls back. Ten seconds.

Two notes on the listing.

`look` returns two things, as `plan` did in chapter 62, and the loop unpacks them into `applies` and `where`. It reads the pairs afresh for every pair and master. For a handful of names that costs nothing you'd notice, and it keeps the function whole: give it a master and two names, and it needs nothing else.

`{applies:>5.0f}` prints the value without its `.0`. It also takes the plain 0 that comes back when nothing applies, so "not kerned" lines up with the rest.

## What Ines was really asking

Ines's headline isn't `To`. It's the name of a drink, `Tónica`. Mira runs the script again and types `T oacute`:

```text
T oacute
  Light      -56   through a class
  Regular    -45   through a class
  Bold       -43   through a class
```

Look at the Regular. Before a plain `o` the `T` pulls in by 84. Before `ó` it pulls in by 45, hardly more than half. Mira's first thought is that it's a slip. Then she looks at the shapes. The bar of the `T` hangs over the `o`, and that's why the pair can be so tight. An acute accent stands where the bar wants to be. Pull the `ó` in by 84 and the accent runs into the bar. Somebody saw that and wrote a looser value for the whole accented family: one class pair, `T` before `@R_oacute`, and every accented `o` is covered.

So `o` and `ó` kern differently after `T`, on purpose, and the names in yesterday's list say how. `("T", "o")` is a pair for the plain letter. `("T", "@R_oacute")` is a pair for the class. The plain `o` isn't in that class at all.

The Light tells another story: −55 for `o` and −56 for `ó`, as good as equal. Maybe the Light's thin accent clears the bar. Maybe nobody got round to it. The list can't say which, and neither can I. Mira adds a line to her notes: "Light: T before accents, same as plain. Meant?" It's a question for Oskar.

There's a second route to the same glyph, worth knowing if you'd rather type letters than names: chapter 24 found a glyph by its character. I've kept today's script to names, because half of what gets kerned, the small capitals and the alternates, has no character of its own.

Then she types the whole word, `T oacute n i c a`, and gets five pairs. Only the first is kerned. The other four say "not kerned" in all three masters, and they need nothing: `n`, `i`, `c` and `a` have stems and bowls, and the sidebearings of chapters 61 to 68 look after those.

## Why three masters disagree

One more thing shows in both outputs, and it'll matter for the rest of this part. Each master has its own list. The Regular's `T o` is −84 and the Bold's is −108, and no rule ties them together. When FontLab makes a weight between two masters, it blends their values for the pair, as it blends their outlines. As far as I know, a pair that's written in one master and absent from the next counts as 0 there, and the blend runs from the value to nothing. I haven't tested that in FontLab 9. That's why a kerning script always says which master it means, and why today's prints all three.

It also means yesterday's count of 106 was one master's truth. The Light has 100 pairs and the Bold 102. Six pairs are in the Regular and not in the Light, and four of them are missing from the Bold too.

## What you learned

`get` with a default hides a missing key, and `get` without one hands back `None`, which can't be mistaken for a value. A font has two answers for a pair: what's written under those two names, and what applies once the classes are counted. `scripting.kerning_pair_value(kerning, first, second)` asks `package.kerning(master)` what applies, with 0 for nothing. Test with `is not None` when 0 is a real value.

## Try it yourself

1. Run the script on `T a` and on `T aacute`. In which master is the difference between the plain and the accented letter biggest? Then try `V a` and `V aacute`. Why might the `V` need no such difference? Look at where its overhang is.
2. Add a fourth case to `source`. When a pair is written and a class pair would give a different value, the written one wins. You can't see the class value yet, so settle for less: when `written` is not `None` and differs from `applies`, return `"written, but something else applies"`. On a sound font that line never prints. Run `T o` and make sure it doesn't.
3. Make the script print one more line at the end: how many units the kerning takes out of the whole run in the Regular. Add up `applies` over all the pairs, with a total that starts at 0, as in chapter 11. For `T oacute n i c a` you should get −45, and for `A V O C A D O`, −55.

## Next

"Through a class" is as much as today's script can say. Which class? Who's in it? Why is `o` outside `@R_oacute` when `ó` is in? Chapter 71 opens the font's kerning classes and prints every one with its members.
