---
this_file: src_docs/md/part2-a-toolbox/021-a-dictionary-of-glyphs.md
---

# 21. Look it up

Monday, the fourth week. Ines is on the phone with the publisher's proofreader, and she's covering the receiver with her hand.

"Mira. How wide is the a-umlaut?"

Mira has `this_glyph.py`. She could have the answer in five seconds, if she knew what to type. Plum has no glyph called `a-umlaut`. She scrolls the Font window, finds the cell and reads the name under it: `adieresis`.

"471."

"And the sharp s?"

That one is `germandbls`. Then "the a-e, the stuck-together one", which is `ae`. Three questions, three trips to the Font window. The proofreader talks like a person and the font is named like a font, and Mira is the translator.

A translator needs a dictionary. Python has one.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open. Since chapter 8 it has 208 glyphs.
- Nothing else. This chapter starts a new script.

## Step 1: A list where you choose the labels

You know lists. A list keeps things in a row, and you get one back by its position: `names[0]`, `names[1]`. Position is the only handle a list gives you.

A **dictionary** keeps things in pairs. You choose a label for each thing, and you get the thing back by its label. Type this:

```python
nicknames = {
    "a-umlaut": "adieresis",
    "sharp s": "germandbls",
    "a-e": "ae",
}
print(nicknames["sharp s"])
```

Run it.

```text
germandbls
```

Look at how it's built. Curly braces go around the whole thing, where a list has square brackets. Inside are three pairs. Each pair is a label, a colon and a value, and commas keep the pairs apart. I've put one pair per line because that's how you'd write a word list on paper. Python doesn't mind the line breaks inside the braces.

The label is called a **key** and the thing it leads to is called a **value**. You ask with square brackets, the way you ask a list, but the key goes between them where the position would be.

You've done this already without the name. `font["A"]` in chapter 6 was a lookup by key. A font behaves like a dictionary of glyphs whose keys are the glyph names. Today you're making a dictionary of your own.

## Step 2: Two lookups in a row

Now use the translation. The nickname leads to the glyph name, and the glyph name leads to the glyph.

```python
from fly import fl

nicknames = {
    "a-umlaut": "adieresis",
    "sharp s": "germandbls",
    "a-e": "ae",
}

font = fl.CurrentFont()
glyph_name = nicknames["sharp s"]
glyph = font[glyph_name]
print(f"sharp s is {glyph.name}, width {int(glyph.width)}")
```

```text
sharp s is germandbls, width 569
```

Follow the boxes. `nicknames["sharp s"]` gives the text `germandbls`, and it goes in the box `glyph_name`. `font[glyph_name]` gives the glyph. There are no quotes around `glyph_name` in that line, because you want what's in the box and not the word on its label.

Change `"sharp s"` to `"a-e"` in both places and run again. 753. Mira could have answered Ines without leaving the keyboard.

Save this as `lookup.py`.

## Step 3: Ask for a word that isn't in the dictionary

Ines's next question is the e-acute. Put `"e-acute"` between the brackets and run.

```text
KeyError: 'e-acute'
```

A new letter of complaint, and a short one. `KeyError` means: you asked for a key, and this dictionary has no such key. The key you asked for is right there in the message.

Compare that with what the font did in chapter 6. When you asked a font for a glyph it didn't have, it handed back `None` and said nothing, and the trouble started one line later. A dictionary of your own is stricter. It stops on the spot and names the missing key. That's the better behavior. You find out where the problem is, not where it ended up.

A `KeyError` is also what you get from a capital in the wrong place. `"Sharp S"` and `"sharp s"` are two different keys.

## Step 4: Check first, and add a word

You can ask a dictionary whether it has a key before you use it. The word is `in`, the same `in` you used on text in chapter 9.

```python
nicknames = {
    "a-umlaut": "adieresis",
    "sharp s": "germandbls",
    "a-e": "ae",
}

ask = "e-acute"
if ask in nicknames:
    print(nicknames[ask])
else:
    print(f"I don't know '{ask}' yet")
```

```text
I don't know 'e-acute' yet
```

No error. The script took the `else` road and told you what's missing in words you chose.

To teach the dictionary a new word, put a value in under a new key. Add this line above `ask = "e-acute"`:

```python
nicknames["e-acute"] = "eacute"
```

Run it again and you get `eacute`. It's the same move as putting something in a box, except this box has many drawers and you say which one. If the key is new, the dictionary grows by one pair. If the key was there already, the old value is thrown out and the new one takes its place. That second case will catch you one day: two pairs with the same key don't give you two answers. The later one wins, and Python doesn't warn you.

`len` works here as it does on a list. `len(nicknames)` is now 4: four pairs.

The keys here are pieces of text. A key can be a number too, and tomorrow's will be.

### Go through the whole dictionary

A `for` loop works on a dictionary too. It hands you the keys, one at a time, in the order they went in.

```python
for nickname in nicknames:
    print(nickname)
```

```text
a-umlaut
sharp s
a-e
e-acute
```

The keys come out and the values stay behind. Mira expected pairs, a nickname and a name on each line. But a key is all you need, because with the key in your hand you can look the value up inside the loop. And `sorted`, which you used on a list in chapter 10, puts the keys in alphabetical order first:

```python
for nickname in sorted(nicknames):
    print(nickname, "means", nicknames[nickname])
```

```text
a-e means ae
a-umlaut means adieresis
e-acute means eacute
sharp s means germandbls
```

That's the word list printed the way a paper dictionary would have it. Mira pins a copy next to the phone, so Ines can see which nicknames the script knows. Notice that a dictionary has no positions. `nicknames[0]` doesn't mean "the first pair". It means "the value under the key 0", there's no such key, and you get `KeyError: 0`.

## Step 5: Let the font fill a dictionary

Typing pairs by hand is fine for a dozen nicknames. For anything about every glyph, let a loop do the typing.

Start with an empty dictionary, which is a pair of curly braces with nothing between them. Then go through the font and put one pair in for each glyph: the name as the key, the width as the value.

```python
from fly import fl

font = fl.CurrentFont()
widths = {}
for glyph in font.glyphs:
    widths[glyph.name] = int(glyph.width)

print(len(widths))
print(widths["adieresis"])
print(widths["germandbls"])
```

```text
208
471
569
```

The loop ran 208 times and each time around it added one pair. After the loop, `widths` is a little table you made: every glyph name in Plum, each with its width next to it.

Why bother, when `font["adieresis"].width` gives the same 471? Two reasons.

The first is that the table is yours. You decided what goes in it. Today it's the width. It could be the width with the left side taken off, or the width compared with another weight, or a yes-or-no for "has Ines approved this glyph". The font only stores what a font stores. A dictionary stores whatever you work out.

The second is that the table keeps still. Suppose a script changes widths, and afterwards you want to say which glyphs changed and by how much. If you filled `widths` before the change, the old numbers are still in it.

## Step 6: Put the two dictionaries together

Now Ines can ask in her own words, about several glyphs at once.

```python
from fly import fl

nicknames = {
    "a-umlaut": "adieresis",
    "sharp s": "germandbls",
    "a-e": "ae",
    "e-acute": "eacute",
}

font = fl.CurrentFont()
widths = {}
for glyph in font.glyphs:
    widths[glyph.name] = int(glyph.width)

for ask in ["a-umlaut", "sharp s", "o-slash", "a-e"]:
    if ask in nicknames:
        glyph_name = nicknames[ask]
        print(f"{ask}: {glyph_name}, {widths[glyph_name]}")
    else:
        print(f"{ask}: not in my list yet")
```

```text
a-umlaut: adieresis, 471
sharp s: germandbls, 569
o-slash: not in my list yet
a-e: ae, 753
```

Three answers and one honest "not yet". The script didn't stop at `o-slash`, because the `if` checked before the lookup.

Mira's first run looked different in one line. She had typed the dictionary a second time for this script, and in her hurry she wrote `"a-e": "a-e"`. Her last line read:

```text
KeyError: 'a-e'
```

The complaint came from `widths[glyph_name]`, and it's a fair one: Plum has no glyph called `a-e`. She found the typo in a minute. She was lucky that the wrong value led nowhere. If she had typed `"a-e": "a"`, the script would have printed `a-e: a, 471` and nobody would have complained at all.

That's the limit of a dictionary. It tells you when a key is missing. It can't tell you that a value is wrong, and a wrong value that leads somewhere gives a wrong answer with a straight face. When you type a table by hand, read it back once, the way you'd read back a phone number.

Save the script over `lookup.py`. The list on the `for ask in` line is the part you change when the phone rings.

??? info "Going deeper: what can be a key"
    Keys are usually pieces of text, and in this book they nearly always are. Numbers work as keys too, which is how chapter 24 looks a glyph up by its Unicode value. A list can't be a key, because a key must not be able to change after it goes in. Values can be anything at all: text, numbers, lists, glyphs, other dictionaries.

## What you learned

A dictionary holds pairs of key and value in curly braces, and `d[key]` gives you the value back. A missing key stops the script with `KeyError`, so check with `in` first when you aren't sure. You can add a pair with `d[key] = value`, and a loop that does this for every glyph turns the font into a lookup table that holds whatever you decide to put in it.

## Try it yourself

1. Add three nicknames of your own to `lookup.py` for glyphs in Plum. Look their real names up in the Font window, then ask for all three in the last loop.
2. Build a second dictionary in the loop from step 5, called `codes`, with the glyph name as key and `glyph.unicode` as value. Print `codes["germandbls"]` and `codes[".notdef"]`. One of them prints something you met in chapter 6.
3. Make a dictionary with the same key twice and different values, for example `{"a": 1, "a": 2}`. Print it, and print its `len`. Say in one sentence what happened to the first pair.

## Next

Chapter 22 uses a dictionary to count: how many glyphs of each kind does the font have?
