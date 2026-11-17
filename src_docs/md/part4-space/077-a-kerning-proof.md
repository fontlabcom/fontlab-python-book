---
this_file: src_docs/md/part4-space/077-a-kerning-proof.md
---

# 77. A kerning proof

Tuesday of week fifteen. The reviewer is called Tobias, he works two towns away, and he judges kerning the way everyone does: by looking at letters. A table of 104 pairs with numbers beside them tells him nothing until he has seen each pair set.

A pair on its own is hard to judge too. `AV` in the middle of a white page could be right or wrong by twenty units and you wouldn't know. Type designers set the pair between letters whose spacing is already trusted: `HHAVHH` for capitals, `nnaynn` for small letters. The eye compares the gap in the middle with the even gaps on either side.

Chapter 61 tested sidebearings with one such word, `minimum`, typed by hand. Today a script makes one for every pair in the kerning list and opens them in a Glyph window. The font doesn't change.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py` with `tell`.
- The kerning as chapter 75 left it. The Regular has 104 pairs.

I couldn't run the code in FontLab 9. The strings below were built in plain Python from Plum's source file. I haven't seen the tab that the last step opens.

## Step 1: Glue four strings together

Start with one pair and a plus sign. Between two strings, `+` joins them end to end:

```python
first = "A"
second = "V"
print("HH" + first + second + "HH")
```

```text
HHAVHH
```

That's a proof word. Now the frame has to suit the letters. A capital wants `H` beside it and a small letter wants `n`. Chapter 13 had the question to ask of a name:

```python
def frame(name):
    if name[0].isupper():
        return "HH"
    return "nn"


def word(first, second):
    return frame(first) + first + second + frame(second)


print(word("A", "V"), word("T", "o"), word("r", "y"))
```

```text
HHAVHH HHTonn nnrynn
```

`name[0]` is the first character of the name. Each side gets the frame that suits it, so `To` has capitals before it and small letters after, as it would in a word.

## Step 2: Names are not letters

Try it on two more pairs from the Regular's list:

```python
print(word("A", "wacute"), word("quoteright", "c"))
```

```text
HHAwacutenn nnquoterightcnn
```

Put those in a Glyph window and you'd see the words "wacute" and "quoteright" spelled out in Plum. The kerning list holds glyph names. A text field takes characters. For `A` and `V` the name and the character are the same thing, which is why the first try looked fine. A name was taken for the thing it names, and for the plain letters the two happen to look alike, so nothing warned you.

There are two ways out. One is to turn each name into its character through the glyph's Unicode value, and that fails for a glyph without one, as a small cap called `a.sc` would be. The other is FontLab's own way of writing a glyph by name in text: a slash, then the name. `/wacute` means the glyph called `wacute`. It works for every glyph, with or without a Unicode value, so the script uses it for all of them:

```python
def frame(name):
    if name[0].isupper():
        return "/H/H"
    return "/n/n"


def word(first, second):
    return frame(first) + "/" + first + "/" + second + frame(second)


print(word("A", "wacute"), word("quoteright", "c"))
```

```text
/H/H/A/wacute/n/n /n/n/quoteright/c/n/n
```

It's harder for you to read and FontLab reads it without guessing. Each slash ends the name before it, so there's never a doubt where `wacute` stops.

## Step 3: A class sends its first member

Most of the list names classes, and a class can't be set as text. Chapter 74 solved this: the first member stands for the class. Bring `stand_in` over as it is:

```python
def stand_in(side, classes):
    if side.startswith("@"):
        members, place = classes[side[1:]]
        return members[0]
    return side
```

So the pair `@L_A` before `@R_Y2` becomes `/H/H/A/Y/H/H`. Tobias sees `AY`, and what he decides holds for `ÁÝ`, `ÄŸ` and the rest of both families. If he doubts that, chapter 70's `pair_value.py` will tell him the value for any two glyphs he names.

## Step 4: Many words, one string

You have a word for each pair. A Glyph window wants one text. Chapter 25 gave you `join`: a separator, a dot, and a list of strings.

```python
words = [word("A", "V"), word("T", "o"), word("r", "y")]
print(" ".join(words))
```

```text
/H/H/A/V/H/H /H/H/T/o/n/n /n/n/r/y/n/n
```

A space between the words makes them words: FontLab can break the line there.

Could two pairs give the same word? If a class's first member also had a pair of its own, yes: `@L_A` before `V` and `A` before `V` would both come out as `/H/H/A/V/H/H`. The script keeps a word only the first time it appears. A set would do that, but a set forgets the order, and the order is how Tobias will find his way. So it's a list and a `not in`:

```python
words = []
for first, second in sorted(pairs):
    text = word(stand_in(first, classes), stand_in(second, classes))
    if text not in words:
        words.append(text)
```

## Step 5: Open the tab

Fly has a function that opens a Glyph window tab with a text in it:

```python
import fly.ap.proof.tabs.text as proof_tab

proof_tab.open_text_tab("/H/H/A/V/H/H", expected_id=package.id)
```

`expected_id` is a safety catch. `package.id` is the number that identifies the font you read the kerning from, the one chapter 30 passed along as `facts.package_id`. If somebody has switched to another font between the reading and the opening, the function refuses with `The source font changed or closed; run the proof again.` A proof of one font's pairs set in another font's letters would be worse than no proof.

The tab shows whichever master is current in FontLab. The pairs differ a little from master to master, so the script builds its text from the master you name in `MASTER`, and you should have that master showing when you run it.

## The whole script

```python
#FLM: Kerning Proof Text
# Builds one proof word for each kerning pair of MASTER, with HH or nn
# on either side, and opens them in a Glyph window tab.
import halfmoon
import fly.ap.core.scripting as scripting
import fly.ap.proof.tabs.text as proof_tab
from fly import fl

MASTER = "Regular"


def frame(name):
    if name[0].isupper():
        return "/H/H"
    return "/n/n"


def word(first, second):
    return frame(first) + "/" + first + "/" + second + frame(second)


def stand_in(side, classes):
    if side.startswith("@"):
        members, place = classes[side[1:]]
        return members[0]
    return side


def proof_words(pairs, classes):
    words = []
    for first, second in sorted(pairs):
        text = word(stand_in(first, classes), stand_in(second, classes))
        if text not in words:
            words.append(text)
    return words


def main():
    if fl.CurrentFont() is None:
        halfmoon.tell("Open a font first.")
        return
    package = scripting.current_package()
    pairs = scripting.kerning_pairs(package, MASTER)
    classes = scripting.kerning_classes(package, MASTER)
    words = proof_words(pairs, classes)
    print(f"{MASTER}: {len(pairs)} pairs, {len(words)} proof words.")
    for text in words[:3]:
        print(" ", text)
    proof_tab.open_text_tab(" ".join(words), expected_id=package.id)


main()
```

Save it as `kern_proof_text.py`. It should print:

```text
Regular: 104 pairs, 104 proof words.
  /H/H/A/C/H/H
  /H/H/A/O/H/H
  /H/H/A/U/H/H
```

and open a tab with 104 words in it, beginning `HHACHH HHAOHH HHAUHH`. That's the design. I haven't seen the tab, and three things about it are open: whether a text of some 1,800 characters is accepted in one go, whether FontLab wraps it into lines, and whether the tab opens with kerning switched on. If the pairs look unkerned, look for the kerning switch in the tab's own controls.

Notes on the listing.

`proof_words` takes two dictionaries and returns a list. It never touches FontLab, so, as with yesterday's checks, you can try it on a made-up table.

The pairs are sorted by name, so the class pairs come first and the proof walks through `A`, then `O`, then `T`. That suits a first reading, because pairs that share a first letter sit side by side and can be compared with each other as well as with their frames. A reviewer who has an hour might prefer the deepest pairs first, and exercise 2 gives him that.

The script prints the first three words before it opens the tab. When a script hands a long text to a window, print the start of it. If the window shows something odd, you can tell whether the text was wrong or the window. I haven't seen the tab in FontLab 9, so that print is also the only part of the result this chapter can vouch for.

In Plum's Regular no word repeats: 104 pairs, 104 words. The `not in` is there for the font where one does.

## What Tobias does with it

Mira runs the script, looks at the tab for a minute, and marks two words herself before anything leaves the studio. `HHLTHH` is the pair chapter 74 flagged, and set between capitals it is as bad as the number said: the `T` sits on the foot of the `L`. And `HHAOHH`, one of the four pairs from Friday's note, shows almost no kerning at all next to its neighbors.

Then she prints the tab to a PDF and sends it. Tobias will write on a printout. What comes back are corrections by pair, and the script for taking those in is tomorrow's.

Fly also ships ready-made kerning proofs, long texts that type designers have used for years. `fly.ap.kerning.proofs.run("kernking")` opens one. They test a font against the pairs that matter in general. Today's proof tests the pairs this font has, which is a different question: the first finds what's missing, the second checks what's there.

## What you learned

A proof word puts a pair between letters whose spacing is trusted: `HH` beside capitals, `nn` beside small letters, chosen with `name[0].isupper()`. A glyph name is not a character, and in FontLab text you write a glyph by name as a slash and the name. `" ".join(words)` makes one text of many words, and a list with `not in` drops repeats and keeps the order. `open_text_tab(text, expected_id=package.id)` opens the text in a Glyph window, and refuses if the font has changed meanwhile.

## Try it yourself

1. Change `frame` so that figures get `/zero/zero` around them. A glyph is a figure if its name is one of `zero`, `one`, and so on up to `nine`: write the ten names in a list and use `in`. Plum has no figure pairs yet, so test `word("seven", "one")` by hand.
2. Sort the pairs by value before making words, deepest first. You'll need `sorted(pairs.items(), key=...)` with a tuple key, as in chapter 74, and a loop that unpacks `(first, second), value`. Which word leads now?
3. Make a second list of words with the pair turned round: for `A` before `V`, the word for `V` before `A`. Print only those whose turned pair is not in the kerning. It's a quick way to find pairs kerned in one direction only.

## Next

Tobias's corrections will come as a table: pair, master, new value. Chapter 78 writes the kerning out to a file a spreadsheet can open, and reads his edited copy back in.
