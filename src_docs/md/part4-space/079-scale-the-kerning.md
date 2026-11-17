---
this_file: src_docs/md/part4-space/079-scale-the-kerning.md
---

# 79. Scale the kerning

Thursday of week fifteen. Tobias's pencil note says the Bold's kerning is "a notch too strong. Not pair by pair." Mira agrees, and she knows why. Most of the Bold's values were carried over from the Light, as chapter 74 found, and they were too strong from the start. Chapter 68 then opened up every right side, and a pair that pulled two letters together by 90 units is now pulling across a wider gap than it was drawn for.

Nobody wants to retype 102 values. The relations between the pairs are sound: `AV` should stay deeper than `AO`. What's wrong is the strength of all of them together. So every value gets multiplied by the same number, a little less than one. The arithmetic is one line. Most of the chapter is about what happens to the fractions.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `ask` and `tell`.
- The kerning as chapter 78 left it: 102 pairs in each master.

I couldn't run the code in FontLab 9. The numbers below were computed in plain Python from Plum's source file with the changes of chapters 72 to 78 applied.

## Step 1: How strong is a master's kerning?

"Too strong" needs a number before you change it. A fair one is the sum of all the values, each taken without its sign, so that a pair which pushes apart counts as much as one which pulls together. Chapter 36 had `abs` for that:

```python
import fly.ap.core.scripting as scripting

package = scripting.current_package()
for master in ["Light", "Regular", "Bold"]:
    pairs = scripting.kerning_pairs(package, master)
    print(master, sum([abs(value) for value in pairs.values()]))
```

```text
Light 5232.0
Regular 4924.0
Bold 5988.0
```

The same 102 pairs in each, and the Bold spends a fifth more than the Regular on them. That agrees with what two people saw on paper.

Mira's first thought is 80 per cent. That would bring the Bold to about 4,790, under the Regular, and a bold face usually wants a little more kerning than its regular, since its letters are heavier and its gaps show more. She settles on 85 per cent, which gives about 5,090.

## Step 2: Multiply one value

```python
value = -90.0
print(value * 85 / 100)
```

```text
-76.5
```

Kerning values are whole units, so that has to become −76 or −77. You know `round` from chapter 11:

```python
print(round(-76.5), round(-59.5), round(-8.5))
```

```text
-76 -60 -8
```

Look at those three. −76.5 went toward zero. −59.5 went away from zero. −8.5 went toward zero again. Python's `round` sends a half to the nearest even number. That's a sound rule for statistics, because the halves don't all lean the same way. For kerning it means that two pairs which were equal steps apart can end up at uneven steps, and which way a half goes depends on whether its neighbor is odd or even.

Fly's kerning tools use the rule from school: a half goes away from zero, always.

```python
import fly.ap.kerning.edit.model as kerning_edit

print(kerning_edit.scaled(-90, 85), kerning_edit.scaled(-70, 85), kerning_edit.scaled(-10, 85))
```

```text
-77 -60 -9
```

`scaled(value, percent)` multiplies, divides by a hundred and rounds that way. In the Bold, 6 of the 102 products land on a half at 85 per cent, and for 4 of them the two rules disagree. One unit, in four pairs: nobody will see it. The reason to use `scaled` is that Fly's kerning tools round the same way, so your script's result will match what a colleague gets from them.

## Step 3: The plan

A plan is a dictionary from pair to new value, holding only the pairs that change. A value that would become 0 gets `None`, the removal order of chapter 73, because a pair of 0 does nothing and still takes up room:

```python
def scale_plan(pairs, percent):
    plan = {}
    for pair, value in pairs.items():
        new = kerning_edit.scaled(value, percent)
        if new == value:
            continue
        if new == 0:
            new = None
        plan[pair] = new
    return plan
```

It takes a dictionary and a number and never touches FontLab, so try it on a made-up table first:

```python
print(scale_plan({("A", "V"): -90.0, ("r", "y"): 2.0, ("o", "o"): 0.4}, 85))
```

```text
{('A', 'V'): -77, ('o', 'o'): None}
```

Three pairs in, two orders out. `r y` at 2 would be 1.7, which rounds back to 2, so it's left alone. The 0.4 becomes nothing and is removed.

## Step 4: Eighty-five of what?

Now the real table. Chapter 68 scaled the sidebearings with a factor, 0.8, and the hand remembers:

```python
PERCENT = 0.85

pairs = scripting.kerning_pairs(package, "Bold")
plan = scale_plan(pairs, PERCENT)
gone = [pair for pair in plan if plan[pair] is None]
print(len(plan), "pairs change,", len(gone), "would be removed.")
```

```text
102 pairs change, 58 would be removed.
```

The function wanted a percentage and got a factor. It did what it was told: it scaled every value to 0.85 per cent of itself. `−90` became `−0.765`, which rounds to −1. Anything under 59 became less than a half and was marked for removal. One click on Yes and the Bold would have had 44 pairs left, each of them −1.

Two things stood between that and the font. The function is called with a number whose unit is in the parameter's name, `percent`, and the constant is named `PERCENT`, so the mistake is visible in the script to anyone who reads it. And the plan was counted before it was written. "58 would be removed" is not what turning something down by a notch looks like.

The script gets a guard as well. A percentage under 10 or over 300 is almost certainly a slip, so it refuses and says why. Set `PERCENT = 85`:

```text
102 pairs change, 0 would be removed.
```

## The whole script

```python
#FLM: Scale Kerning
# Multiplies every kerning value of MASTER by PERCENT / 100.
# Halves round away from zero. A pair that becomes 0 is removed.
import halfmoon
import fly.ap.core.scripting as scripting
import fly.ap.kerning.batch as kerning_batch
import fly.ap.kerning.edit.model as kerning_edit
from fly import fl

MASTER = "Bold"
PERCENT = 85
SHOW = 7


def strength(pairs):
    return sum([abs(value) for value in pairs.values()])


def scale_plan(pairs, percent):
    plan = {}
    for pair, value in pairs.items():
        new = kerning_edit.scaled(value, percent)
        if new == value:
            continue
        if new == 0:
            new = None
        plan[pair] = new
    return plan


def size_then_name(item):
    pair, value = item
    return (abs(value), pair)


def main():
    if fl.CurrentFont() is None:
        halfmoon.tell("Open a font first.")
        return
    if PERCENT < 10 or PERCENT > 300:
        halfmoon.tell(f"PERCENT is {PERCENT}. Write 85 for 85 per cent.")
        return
    package = scripting.current_package()
    pairs = scripting.kerning_pairs(package, MASTER)
    plan = scale_plan(pairs, PERCENT)
    gone = [pair for pair in plan if plan[pair] is None]

    print(f"{MASTER} at {PERCENT} per cent. The {SHOW} smallest pairs:")
    for (first, second), value in sorted(pairs.items(), key=size_then_name)[:SHOW]:
        new = plan.get((first, second), value)
        print(f"  {first:<12}{second:<12}{value:>5.0f} -> {new}")
    print(f"{len(plan)} pairs change, {len(gone)} would be removed.")
    if not plan:
        return
    if not halfmoon.ask(f"Scale {len(plan)} pairs of the {MASTER} to {PERCENT} per cent?"):
        return

    before = strength(pairs)
    kerning_batch.write_kerning(package, {MASTER: plan}, "Scale kerning")
    pairs = scripting.kerning_pairs(package, MASTER)
    print(f"Done. Strength {before:.0f} -> {strength(pairs):.0f}, {len(pairs)} pairs.")


main()
```

Save it as `scale_kerning.py`. It should print:

```text
Bold at 85 per cent. The 7 smallest pairs:
  @L_W        @R_aacute     -10 -> -9
  @L_W        @R_oacute     -12 -> -10
  V           @R_uacute     -14 -> -12
  V           u             -14 -> -12
  r           @R_yacute      14 -> 12
  r           y              14 -> 12
  t           quoteright     15 -> 13
102 pairs change, 0 would be removed.
```

and, after Yes:

```text
Done. Strength 5988 -> 5090, 102 pairs.
```

One Undo step should take it back. I haven't seen it in FontLab 9.

Notes on the listing.

The script shows the smallest pairs because that's where scaling does its damage. A big pair loses 15 per cent of itself, give or take a hair. A small one can't. `−10` should become −8.5 and becomes −9, which is 90 per cent. `−12` becomes −10, which is 83. Had there been a pair of 3, it would have become 2.55 and rounded back to 3: not scaled at all. The smaller the value, the coarser the steps it can take. That's worth seeing before you agree, and it's why chapter 75 removed the tiny pairs first.

`size_then_name` returns a tuple, as the sort keys of chapter 74 did: smallest size first, and the pair's names to settle ties, so the list comes out in the same order every time.

`plan.get((first, second), value)` uses the second argument of `get` from chapter 22's tally: if the pair isn't in the plan, it stays as it is, and the line shows its present value.

`{MASTER: plan}` is the whole of the edit that `write_kerning` wants: a dictionary from master name to that master's orders.

The last line reads the font again and measures again, as every writing script in this part has done.

## Don't run it twice

Run the script a second time and it will scale the scaled values: 85 per cent of 85 per cent is about 72. Nothing in the font says "this has been scaled", so the script can't know. The Undo step is your way back, and the strength it prints is your way of knowing where you are: the Bold should read 5,090 after one run. If it reads about 4,320, it has been run twice.

Scaling isn't its own undo either. You might think 118 per cent would take the 85 back. Try the smallest pair: −10 became −9, and −9 at 118 per cent is −10.62, which rounds to −11. Every rounding loses what was after the decimal point, and no later multiplication can find it again. To go back, use Undo, or keep the CSV from yesterday, which holds every value as it was.

## What Mira sees

She runs Tuesday's proof script again. The Bold's `HHAYHH` has let go a little, from −90 to −77, and the `quoteright` pairs no longer look as if the apostrophe were falling into the letter after it. `L T` is at −72, in step with its neighbors.

She writes "Bold kerning: 85%" in the project notebook, with the date. A number like that is soon forgotten and can't be recovered from the font.

## What you learned

To change how strong a whole master's kerning is, multiply every value by one percentage, and measure the strength before and after with the sum of `abs(value)`. Python's `round` sends a half to the even neighbor, and `kerning_edit.scaled(value, percent)` sends it away from zero, as Fly's kerning tools do. Name a quantity by its unit, and refuse values that can only be slips: 0.85 is not 85. Scaling twice compounds, and scaling back doesn't restore what rounding dropped, so write down the percentage you used.

## Try it yourself

1. Without writing anything, find out how many pairs of the Bold would be removed at 3 per cent. Change `PERCENT`, and change the guard for the moment so that it lets you. Put both back afterwards.
2. Add a constant `ONLY_NEGATIVE = True`. When it's on, `scale_plan` should leave the positive pairs alone. You'll need one more `if` with `continue`. How many pairs change now?
3. `kerning_edit.round_to(value, step)` snaps a value to a multiple of `step`, with the same rule for halves. Write a plan that rounds every Bold pair to a multiple of 5 and print how many would change. Don't write it. Some designers keep all kerning on a grid like that, and some think it throws away good work.

## Next

The spacing is set and the kerning is reviewed. Chapter 80 gathers the checks of this part into one audit that Mira can run on a Friday, and holds it against the proof that started it all.
