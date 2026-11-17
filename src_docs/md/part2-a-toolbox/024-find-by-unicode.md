---
this_file: src_docs/md/part2-a-toolbox/024-find-by-unicode.md
---

# 24. Find the glyph for a letter

Thursday. Mira owes the proofreader an answer about the œ, and before she's had coffee there's a second question on top of it. The publisher is thinking about a Hungarian novel.

*Do we have ő? That's an o with two long accents, not an ö.*

Mira scrolls the Font window again. She's hunting through 208 cells for one small letter, and then for its capital. I stop her.

"You know its number," I say. "Yesterday you learned how to get the number of any character. Ask the font by number."

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- What you know about dictionaries from chapters 21 and 22, and about `def` from [chapter 16](../part1-first-words/016-name-your-steps.md).

## Step 1: The slow way first

Start with what you can already write. You have a number, 339, the œ. Every glyph has a `unicode` drawer. Go through all the glyphs and look in each drawer.

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if glyph.unicode == 339:
        print(glyph.name)
```

```text
oe
```

There it is. Plum has an œ, and its glyph is named `oe`. It sits a few cells after the `o`, behind the accented ones, and Mira went past it twice. That's no shame. After a hundred cells of small black shapes, an œ looks a lot like an `o` followed by an `e`. The loop doesn't get tired. It looked in all 208 drawers and compared numbers, and a number can't look like its neighbor.

Change 339 to 337, the ő, and run it again. Nothing prints. Is that a "no"?

It is, but it's a quiet one. A script that prints nothing when the answer is no looks the same as a script that's broken. Mira looks at the empty Output panel and isn't sure which she's got. You want a script that says no out loud.

## Step 2: Turn the font inside out

The loop also does more walking than it needs to. For every question, it visits every glyph. Ask about ten characters and it makes ten trips through the font.

You've seen the cure. In chapter 21 you built `widths`, a dictionary from glyph name to width, by going through the font once. After that, every lookup was instant. Build the same kind of table, but file each glyph under its Unicode value:

```python
from fly import fl

font = fl.CurrentFont()
by_number = {}
for glyph in font.glyphs:
    if glyph.unicode is not None:
        by_number[glyph.unicode] = glyph.name

print(len(by_number))
print(by_number[339])
```

```text
204
oe
```

The keys are numbers and the values are names. In chapter 21 I said numbers can be keys, and in chapter 22 you used them to count. Here they're doing the job a dictionary was made for: you hold a number, you want the thing filed under it.

The `if` keeps the four glyphs without a Unicode value out. If you left it off, all four would try to file themselves under the key `None`, each one replacing the last, and you'd have one useless pair in your table.

Now the question about ő:

```python
print(by_number[337])
```

```text
KeyError: 337
```

That's a loud no, at least. But it's a letter of complaint, and you don't want to forward one of those to a proofreader. You know two polite ways to ask. One is `in`. The other is `get`:

```python
print(by_number.get(339))
print(by_number.get(337))
```

```text
oe
None
```

In chapter 22 you gave `get` a second thing through the slot, the 0 to use when the key was new. Leave it off and `get` answers `None` for a key it doesn't have. You've met `None` before: it's what Python says when there's nothing there.

## Step 3: Give the question a name

You're going to ask this question often. Wrap it in a function, so that the question has a name.

```python
def glyph_for(character):
    number = ord(character)
    return by_number.get(number)
```

Three lines. It's a recipe with one slot, as in chapter 16, and the slot takes a character. The first line inside turns it into its number. The second looks the number up and hands back what it found.

`return` is the word that hands something back. You used it in chapter 16, and here's a closer look at it, because it's what makes this function useful. A function with `return` is a question that has an answer. When Python gets to `return`, the function is over, and the answer goes back to the place where the function was called. You can put that answer in a box, test it, or print it:

```python
print(glyph_for("œ"))
print(glyph_for("ő"))
print(glyph_for("é"))
```

```text
oe
None
eacute
```

Mira types the character she's been asked about, straight from the proofreader's message. No numbers, no hex, no scrolling.

Remember the three things from yesterday: the character, the Unicode value and the glyph name. This function is the whole chain in one go. A character goes in, `ord` makes it a number, the table makes the number a glyph name. It's the same trip a computer makes when someone presses a key and a letter of Plum appears on the screen, except that the computer goes on to fetch the drawing.

## Step 4: Print is not return

Here's a mistake that almost everybody makes once. Write the function with `print` where `return` should be:

```python
def glyph_for(character):
    number = ord(character)
    print(by_number.get(number))

answer = glyph_for("œ")
print("The answer is", answer)
```

```text
oe
The answer is None
```

Look at the two lines. The function did show `oe`, in the Output panel, for a person to read. But it handed nothing back. So the box `answer` got `None`, which is what every function hands back when it has no `return`.

This is the difference between a colleague who says the number out loud as they walk past your desk and one who writes it on a slip and puts it in your hand. If all you wanted was to hear it, both will do. If you need to do something with it next, you need the slip. `print` is for people. `return` is for the rest of your script.

Put the `return` back.

## Step 5: Say yes or no in words

Now use the answer. The function hands back a name or `None`, and an `if` turns that into a sentence:

```python
character = "ő"
name = glyph_for(character)
if name is None:
    print(f"No. There is no glyph for {character} (U+{ord(character):04X}).")
else:
    print(f"Yes. {character} (U+{ord(character):04X}) is the glyph {name}.")
```

```text
No. There is no glyph for ő (U+0151).
```

Change the first line to `"œ"`:

```text
Yes. œ (U+0153) is the glyph oe.
```

Both answers are out loud now, and both come with the `U+` form the proofreader likes, thanks to yesterday's `:04X`.

Notice what the function doesn't do. It doesn't print, and it doesn't decide how the answer is worded. It finds a glyph name and that's all. The wording lives outside. That split is worth keeping. Next week you may want the same answer in a file, or in a count, and a function that only finds things can serve all of those. One that also talks can only talk.

## Step 6: A whole word at a time

The proofreader won't stop at one letter. A piece of text is a row of characters, so loop over it. Here's the Hungarian sentence that typesetters use to test accents, the way English speakers use the quick brown fox:

```python
text = "Árvíztűrő tükörfúrógép"
for character in text:
    if glyph_for(character) is None:
        print(f"Missing: {character} (U+{ord(character):04X})")
```

```text
Missing: ű (U+0171)
Missing: ő (U+0151)
```

Twenty-two characters, two gaps. Plum has the Á, the í, the ö, the ú and the rest. It lacks exactly the two letters that Hungarian has and its neighbors don't: the o and the u with the double acute accent.

That's a much better answer than "no". Mira writes: *œ yes, it was hiding under the name `oe`. For Hungarian we're two letters short, ő and ű, plus their capitals I expect. Everything else is there.* Ines reads it and says the two letters are a morning's drawing, not a reason to turn a book down.

Here's the whole script. Save it as `have_we_got.py`.

```python
from fly import fl


def glyph_for(character):
    number = ord(character)
    return by_number.get(number)


font = fl.CurrentFont()
by_number = {}
for glyph in font.glyphs:
    if glyph.unicode is not None:
        by_number[glyph.unicode] = glyph.name

text = "Árvíztűrő tükörfúrógép"
for character in text:
    if glyph_for(character) is None:
        print(f"Missing: {character} (U+{ord(character):04X})")
print("Checked", len(text), "characters.")
```

The last line is there for the reason from step 1. When nothing is missing, the script still says something, so you can tell a clean result from a script that didn't run.

The function sits at the top and uses `by_number`, which is filled further down. That works because Python only reads a function when it's defined. It looks for `by_number` later, at the moment the function is called, and by then the table exists.

??? info "Going deeper: FontLab can look up a Unicode value itself"
    The font object has its own way to find a glyph by Unicode value, and chapter 81 uses it when the book gets to encoding in earnest. I've built the table by hand here for two reasons. It's four lines you fully understand, and a table you built is one you can also loop over, count and compare, which is what chapter 25 does with it.

## What you learned

To find things fast, go through the font once and file each glyph under the thing you'll search by, here its Unicode value. `d.get(key)` hands back `None` when the key isn't there. A function with `return` hands its answer to the rest of the script, which `print` can't do, and a function that only finds something is easier to reuse than one that also reports. A script should say something when the answer is no.

## Try it yourself

1. Check your own name with `have_we_got.py`, then the sentence *Zażółć gęślą jaźń*, which is the Polish test sentence. Which characters does Plum lack for Polish?
2. The loop in step 6 reports a missing character once for every time it appears. Try the text `"őőő"`. Then fix it: keep a list of the characters you've already reported, and report a character only if `character in reported` is false. You need `append`, and an `if` with an `else`: do nothing much in the first branch, and report in the second.
3. Write a second function, `number_for(name)`, that goes the other way: give it a glyph name, get its Unicode value, or `None`. You'll need a second dictionary, filed by name. What does it hand back for `"a.sc"`, and for `"nosuchglyph"`? The two answers look the same. Do they mean the same?

## Next

Chapter 25 takes a whole language's worth of characters and subtracts the font from it, with a new kind of container made for that sum.
