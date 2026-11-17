---
this_file: src_docs/md/part2-a-toolbox/030-rename-with-care.md
---

# 30. Rename with care

Thursday. The publisher's production notes have arrived, four pages of them, and item 11 is one line: *Alternates must be named `.ss01`, not `.alt`.*

Ines says sixty glyphs in the real Plum end in `.alt`. That Plum, the one Halfmoon ships, belongs to the story. Yours is the free one from chapter 4, and it has none, which is why you'll add four in a moment. Oskar named them that way years ago, when `.alt` was what everybody wrote. The publisher's layout software looks for stylistic set names, and `.ss01` is the name for set number one.

Sixty renames by hand is an afternoon: double-click, select four letters, type five, press Return, next. And somewhere around the fortieth she'd type `.ss10`.

A name is the handle that everything else in the font holds a glyph by. Changing sixty handles at once is the riskiest thing a script of Mira's has done yet. So this chapter goes slowly, and the script shows its plan before it touches anything.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open and saved.
- Four glyphs to rename. The practice font has no alternates, so make some, as you made the small caps in [chapter 8](../part1-first-words/008-only-the-ones-i-want.md): click the Font window, choose **Font > New Glyph…**, and type `a.alt`. Do it three more times for `g.alt`, `y.alt` and `ampersand.alt`.
- The Font window in front when you run the scripts.

Four glyphs will do. A script that renames four correctly renames sixty the same way.

## Step 1: Replace part of a string

Start with plain Python. Strings have a method for swapping one piece of text for another:

```python
old = "a.alt"
new = old.replace(".alt", ".ss01")
print(old)
print(new)
```

```text
a.alt
a.ss01
```

`replace` takes two things through the slot: what to look for, and what to put there. It hands back a new string. The first line of output shows that `old` still says `a.alt`. You saw the same with `upper` and `strip`: a string never changes in place. If you want the result, catch it in a box.

What if the thing you're looking for isn't there?

```python
print("A".replace(".alt", ".ss01"))
```

```text
A
```

No error, and no change. `replace` hands back the string as it was. That's convenient, and it's also a trap. A `replace` with a typo in it runs happily and does nothing, and nothing looks like success if you aren't checking.

## Step 2: Build the list of renames

Now the font. You want every glyph whose name ends in `.alt`, and for each one the old name and the new name, side by side. `endswith` is from chapter 9, and a list of lists is a list whose items are small lists:

```python
from fly import fl

font = fl.CurrentFont()

pairs = []
for glyph in font.glyphs:
    if glyph.name.endswith(".alt"):
        old = glyph.name
        new = old.replace(".alt", ".ss01")
        pairs.append([old, new])

print(len(pairs), "to rename")
for pair in pairs:
    print(pair)
```

```text
4 to rename
['a.alt', 'a.ss01']
['ampersand.alt', 'ampersand.ss01']
['g.alt', 'g.ss01']
['y.alt', 'y.ss01']
```

Your four may come in a different order, depending on how the Font window sorts them.

Each item in `pairs` is a little list of two strings, old then new. Call each one a pair. A list whose items are lists is a shape of its own, and chapter 35 looks at it properly. Nothing has been renamed. You've written down what you intend to do, the way you'd write a list before going to the shops. That list is the most useful thing in this chapter. You can read it, count it and check it, and the font is exactly as it was.

Do read it. Four lines you can check by eye. With sixty, read the first few, the last few, and the count. If the count says 61 when you expected 60, stop and find out why before going on.

## Step 3: Ask for a plan

Your list says what you want. It doesn't say whether the font can take it. What if there's already a glyph called `a.ss01`? What if a new name has a character in it that glyph names don't allow?

Fly has a helper that checks every pair against the font and tells you, line by line, whether the rename is safe. It changes nothing. Add this under your loop:

```python
import fly.ap.glyphs.names.model as names
from fly.ap.glyphs.identity_tools.glyph_identity.batch_rename import plan_renames

facts = names.scan()
plan = plan_renames(facts, pairs)

for old, new, status in plan:
    print(f"{old:<16}{new:<16}{status}")
```

```text
a.alt           a.ss01          ok
ampersand.alt   ampersand.ss01  ok
g.alt           g.ss01          ok
y.alt           y.ss01          ok
```

The two import lines are magic lines, and the second is the longest in the book so far. Copy them. They say where in Fly the two helpers live.

`names.scan()` reads the whole font once and remembers what it found: every glyph name, and which glyphs FontLab builds automatically from others. I've called the box `facts` because that's what's in it.

`plan_renames(facts, pairs)` goes through your pairs and hands back a list of rows. Each row has three things in it: the old name, the new name and a verdict. The `for old, new, status in plan:` line takes each row apart into three boxes at once, the way `for key, value in ...items()` took two in chapter 22.

`ok` means the helper found nothing against that rename. Now give it something to object to. Change the replacement so the new suffix has a space where the dot should be:

```python
        new = old.replace(".alt", " ss01")
```

```text
a.alt           a ss01          invalid name
ampersand.alt   ampersand ss01  invalid name
g.alt           g ss01          invalid name
y.alt           y ss01          invalid name
```

Still no error, and the font is still untouched. The plan tells you what would have gone wrong. A glyph name may hold letters without accents, digits, the dot, the underscore and the hyphen. It can't start with a digit, it can't be longer than 63 characters, and it can't hold a space. Put the dot back.

These are the other verdicts you may see, from the helper's source:

| Verdict | What it means |
|---|---|
| `exists in font` | There's already a glyph with the new name. |
| `duplicate target` | Two of your pairs want the same new name. |
| `reserved glyph` | You tried to rename `.notdef` or `space`. Don't. |
| `has auto layers` | FontLab builds this glyph automatically. |
| `base of auto ...` | Some other glyph is built automatically from this one. |

A row with any verdict but `ok` is skipped when you apply the plan. The rest go through.

## Step 4: Apply it

When every row says `ok`, and you've read the rows, add the lines that do the work:

```python
from fly import qt
from fly.ap.glyphs.identity_tools.glyph_identity.batch_rename import apply_renames

renamed = apply_renames(None, qt.QtCore, facts.package_id, pairs)

print(len(renamed), "renamed")
```

```text
4 renamed
```

Look at the Font window. The four cells carry their new names. Now open the **Edit** menu. There should be one Undo entry for the whole job, with the helper's own title, **Batch Rename**. Choose it and all four names go back. Choose **Edit > Redo** and they're `.ss01` again.

The same deal as yesterday's `commit`: all or nothing. In fact `apply_renames` calls a `commit` of its own inside. You don't write a function and hand it over this time, because the helper already knows what a rename is.

It takes four things. Two of them are parts I'm not opening yet. I'll say what they are and leave it there.

- `None` means "use the FontLab I'm running in". There's a slot there because the helper's own tests pass in something else.
- `qt.QtCore` hands the helper a clock. Every glyph it renames gets stamped with the time of the change.
- `facts.package_id` is a number that identifies the font you scanned. Suppose you scan Plum, wander off, click on a different font and come back to run the last line. The helper notices that the front font isn't the one the plan was made for and refuses with `The scanned font is no longer current; reload.`
- `pairs` is your list.

Notice what you didn't pass: the plan. `apply_renames` scans the font again and makes a fresh plan of its own the moment before it writes. The plan you printed was for you to read. The helper doesn't trust a plan that might be a minute old, and neither should you.

## Step 5: Run it twice

Run the whole script again, now that the glyphs are renamed.

```text
0 to rename
0 renamed
```

Nothing ends in `.alt` any more, so `pairs` is empty, the plan is empty, and the helper has nothing to do. No error and no damage.

A script that changes things should be safe to run twice. People do run scripts twice: by accident, or because they aren't sure the first run worked, or because a colleague ran it yesterday and didn't say. A script that finds its targets by looking at the font, and not by counting on what it did last time, behaves properly on the second run.

## Step 6: What a rename doesn't reach

The glyphs have new names. The rest of the font may not have heard.

A glyph's name gets written down in other places. OpenType features refer to glyphs by name: the real Plum has a line that says, more or less, "when the reader turns on the stylistic set, swap `a` for `a.alt`". Kerning classes list their members by name. The notes at the top of Fly's rename helper say plainly that kerning and features keep the old names after a rename. So the feature line would still ask for `a.alt`, and there'd no longer be such a glyph.

There's no error for that today. It shows up later, when the font is exported, or worse, when the alternates quietly stop working in the publisher's layout.

So a rename has three parts, and the script does only the first:

1. Rename the glyphs.
2. Open the **Features** panel, search for the old suffix and fix what you find. Mira finds one line and fixes it by hand.
3. Look at your kerning classes for the old names.

Part 5 of this book deals with features and Part 4 with kerning, and by then you'll have scripts that check both. Until then, check by hand, and write the three parts in a comment at the top of the script so that the next person does too.

The other thing a rename can disturb is glyphs built from other glyphs. That's what the `has auto layers` and `base of auto` verdicts are about. When FontLab builds `aacute` automatically from `a` and `acute`, it finds the pieces by name. Rename `a` and the recipe breaks. The helper refuses those rows and leaves you to sort them out with your eyes open. I think that's the right call.

## The whole script

Save this as `rename_suffix.py`. The two suffixes sit in boxes at the top:

```python
# Renames every glyph that ends in OLD_SUFFIX so that it ends in NEW_SUFFIX.
# One step in Edit > Undo. Run it with the Font window in front.
# Afterward, by hand: fix the old names in Features and in kerning classes.
from fly import fl, qt
import fly.ap.glyphs.names.model as names
from fly.ap.glyphs.identity_tools.glyph_identity.batch_rename import (
    apply_renames,
    plan_renames,
)

OLD_SUFFIX = ".alt"
NEW_SUFFIX = ".ss01"

font = fl.CurrentFont()

pairs = []
for glyph in font.glyphs:
    if glyph.name.endswith(OLD_SUFFIX):
        old = glyph.name
        new = old.replace(OLD_SUFFIX, NEW_SUFFIX)
        pairs.append([old, new])

facts = names.scan()
for old, new, status in plan_renames(facts, pairs):
    print(f"{old:<16}{new:<16}{status}")

renamed = apply_renames(None, qt.QtCore, facts.package_id, pairs)
print(len(renamed), "renamed")
```

The import with parentheses around two names is one line folded in two so that it fits the page. Python reads it as one.

Mira reads the script through and is nearly ready to run it on the real Plum. Then she notices that it prints the plan and applies it in the same breath. On four glyphs she can read the plan afterward and press Undo. On sixty, in the font she ships, she'd like the script to stop after the plan and wait until she says go.

## What you learned

`replace` hands back a string with one piece of text swapped for another, and hands back the string unchanged when there's nothing to swap. To rename glyphs, build a list of old and new names first, read it, ask `plan_renames` what the font thinks of it, and only then call `apply_renames`, which does the whole job as one Undo step. A rename changes glyph names and nothing else: features and kerning classes still hold the old names until you fix them.

## Try it yourself

1. Undo the rename so that you have `.alt` glyphs again. Add a glyph named `g.ss01` by hand, then run the script. What does the plan say for `g.alt`, and how many glyphs get renamed? Delete `g.ss01` afterward.
2. Change the two suffixes so that the script turns `.ss01` back into `.alt`, and run it. You've written your own Undo. When would that be useful, given what you know from chapter 29 about how long **Edit > Undo** lasts?
3. Before you run anything, work out on paper what `"a.alt.sc".replace(".alt", ".ss01")` gives, and what `"salt".replace("alt", "ss01")` gives. Then try both. One of them is fine. The other is a bug in waiting, and it's the subject of the next chapter.

## Next

Mira nearly renames the wrong sixty. Chapter 31 adds a switch to the script: plan only, or plan and apply.
