---
this_file: src_docs/md/part2-a-toolbox/023-unicode-is-a-number.md
---

# 23. Unicode is a number

Wednesday. The proofreader has stopped phoning and started writing, and what she writes looks like this:

*Please confirm Plum covers U+00E9, U+0153 and U+20AC.*

Mira looks at her own list, the one from chapter 7 with its Unicode numbers. It says things like 233 and 8364. Nothing in it starts with `U+`, and nothing in it has a letter in the middle of a number.

"Is she using a different Unicode?" Mira asks.

She isn't. There's one Unicode, and two ways of writing its numbers down. Today you learn to read both, and you teach your scripts to speak the proofreader's.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `this_glyph.py` from [chapter 6](../part1-first-words/006-ask-a-glyph-its-name.md). You'll improve it.

## Step 1: Every character has a number

Start with no font at all. Python knows Unicode by itself, and it has a function that tells you the number of any character.

```python
print(ord("A"))
print(ord("a"))
print(ord("é"))
print(ord("€"))
```

```text
65
97
233
8364
```

`ord` is short for "ordinal", which is a number that says where something stands in a row. Unicode is that row: one long numbered list of every character people write with, kept by a group called the Unicode Consortium. Capital A stands at place 65. The euro sign stands at place 8,364. The list has room for more than a million characters, and so far it holds about 150,000.

You saw 65 in chapter 6, when you asked the glyph `A` for its `unicode` drawer. It's the same 65. The font didn't make that number up. A font says "my glyph named `A` is the drawing for character number 65", and that's how a computer that receives the character 65 from a keyboard knows which drawing to show.

The trip works in the other direction too:

```python
print(chr(233))
print(chr(8364))
```

```text
é
€
```

`chr` is short for "character". Give it a number and it hands you the character at that place.

Capital and small letters are different characters with different numbers. `A` is 65 and `a` is 97. To Unicode they've no more to do with each other than `A` and `€`.

## Step 2: One character, please

`ord` has a slot for exactly one character. Give it two:

```python
print(ord("ab"))
```

```text
TypeError: ord() expected a character, but string of length 2 found
```

That's a clear letter of complaint. The reason I'm showing it is what it tells you about text. To you, `"ab"` and `"a"` are the same kind of thing, a bit of typing. To Python, a piece of text is a row of characters, and a row with one character in it is the only kind `ord` will take. When you want the numbers for a whole word, you loop:

```python
for letter in "Plum":
    print(letter, ord(letter))
```

```text
P 80
l 108
u 117
m 109
```

## Step 3: The other way to write the number

Now the proofreader's version. She wrote `U+00E9` for the é. Your script says 233. These are the same number, and here's the idea in a few lines.

The way you count has ten digits, 0 to 9. When you run out, you start a new column: after 9 comes 10. There's a second way of counting that has sixteen digits. It uses 0 to 9 and then, because we've no more digit shapes, the letters A to F. In that system A means ten, B eleven, and so on up to F for fifteen. Only after F do you start a new column. It's called **hexadecimal**, or **hex**.

Why would anyone do that? Because computers store numbers in a way that sixteen fits neatly and ten doesn't. Unicode charts were laid out by people who think in sixteens, with sixteen characters to a row. So the charts, FontLab and every proofreader in the business write Unicode values in hex, and put `U+` in front so you can tell.

Take the proofreader's `E9`. It has two columns. The right one counts ones, as you're used to, and holds 9. The left one doesn't count tens. It counts sixteens, and it holds E, which is fourteen. Fourteen sixteens are 224, and 9 more makes 233. Same number, written in a different system, the way 233 and CCXXXIII are.

One trap comes with this. A hex number that happens to use no letters looks like an everyday number and isn't. `U+0041` is the capital A, and you know that as 65, not 41. When a number arrives from a type person without a label, ask which kind it is.

You don't have to do the sums. Python translates. You met `hex` in chapter 6:

```python
print(hex(233))
```

```text
0xe9
```

That's `e9`, with Python's own "hex coming up" mark in front. It's the right number in the wrong clothes. The custom is capital letters, at least four digits, zeros in front if it's short, and `U+` at the start. An f-string can dress it properly:

```python
number = 233
print(f"U+{number:04X}")
```

```text
U+00E9
```

In chapter 12 you put things after a colon inside the curly braces to line up columns. This is the same slot with a different order in it. `X` means "write this in hex, with capitals". `04` means "at least four digits, and fill with zeros". The `U+` in front is plain text. Copy `:04X` as it stands. You'll type it the same way every time.

And back the other way, from the proofreader's digits to your number:

```python
print(int("00E9", 16))
```

```text
233
```

In chapter 11 `int` cut a float down to a whole number. It also reads text: `int("523")` gives 523. With a second thing in the slot, 16, it reads the text as hex. Leave the `U+` off. `int` doesn't know that part.

## Step 4: A better this_glyph.py

Open `this_glyph.py`. It prints the Unicode value in the plain form. Make it print both forms and the character too.

```python
from fly import fl

glyph = fl.CurrentGlyph()
number = glyph.unicode
print("Name:", glyph.name)
print("Unicode:", f"U+{number:04X}", "which is", number)
print("Character:", chr(number))
print("Width:", int(glyph.width))
```

Go to the `eacute` glyph and run it.

```text
Name: eacute
Unicode: U+00E9 which is 233
Character: é
Width: 470
```

Now try it on `Euro`. You get `U+20AC`, 8364 and €. Try `fi`, the ligature: `U+FB01`, 64257. That's one of the two highest numbers in the whole font.

Then go to `.notdef` and run it.

```text
TypeError: unsupported format string passed to NoneType.__format__
```

The script got as far as the name and stopped on the next line. Read the complaint from its end. `NoneType` is the name you learned to look for in chapter 19: somewhere a box holds the nothing. `__format__` is the part of a value that an f-string asks to do the dressing. So the complaint says: I was handed a format, `04X`, and the thing I was to dress in it was `None`.

Which box? `.notdef` has no Unicode value, so `number` is `None`, and the f-string was asked to write nothing as four hex digits. It couldn't. Notice that the plain version of the script never had this trouble. `print("Unicode:", None)` prints the word `None` and goes on. The complaint arrived on the day you asked for more than plain printing. That's how a script that ran for weeks fails on a glyph it has seen before.

The fix is the guard from chapter 19:

```python
from fly import fl

glyph = fl.CurrentGlyph()
number = glyph.unicode
print("Name:", glyph.name)
if number is None:
    print("Unicode: none")
else:
    print("Unicode:", f"U+{number:04X}", "which is", number)
    print("Character:", chr(number))
print("Width:", int(glyph.width))
```

Save it as `what_unicode.py`. Leave `this_glyph.py` as it was. You'll want to remember where you started.

## Step 5: The glyph name is not the character

There are now three things on Mira's screen for one letter, and it's worth keeping them apart.

`eacute` is the **glyph name**. It's a label inside the font, made of plain letters so that every program can handle it. People chose it. It could have been `e_with_stroke_on_top` and the font would work the same.

233, or `U+00E9`, is the **Unicode value**. It's the link from the font to the outside world. Change it and the keyboard's é shows a different drawing, or none.

`é` is the character, the thing the reader types and sees.

Scripts get these mixed up all the time, and so do people. Here's a way to see that they're separate:

```python
print(len("eacute"))
print(len("é"))
```

```text
6
1
```

Six letters in the name. One character. When a script asks the font for `font["é"]`, it's using a character where a glyph name belongs, and it gets `None`. You found that in an exercise in chapter 6. Now you know why.

## Step 6: Answer the proofreader

She asked about three values. You can now read them: `00E9` is 233, the é. What's `0153`, and what's `20AC`?

```python
for code in ["00E9", "0153", "20AC"]:
    number = int(code, 16)
    print(f"U+{code} is {number}, the character {chr(number)}")
```

```text
U+00E9 is 233, the character é
U+0153 is 339, the character œ
U+20AC is 8364, the character €
```

So she wants the é, the œ and the euro sign. Notice the script hasn't touched the font yet. It only translated. Whether Plum has a glyph for each of those numbers is a different question, and you can't answer it with `font[...]`, because that looks up names, not numbers.

Mira scrolls the Font window. The é is there. The euro is there. She can't see an œ anywhere near the `o`, but with 208 cells she isn't sure she hasn't missed it.

She writes: *é and € yes. œ I can't find. I'll confirm tomorrow.*

??? info "Going deeper: glyphs with no number, and numbers above FFFF"
    Not every glyph needs a Unicode value. Small caps, alternates and the parts of ligatures are reached through OpenType features, which Part 5 covers, and they usually have none. Going the other way, Unicode values can be longer than four hex digits. Emoji and many historic scripts sit above `U+FFFF` and are written with five or six digits. `:04X` handles them: four is the least it writes, not the most.

## What you learned

Every character has a place in Unicode's list: `ord("é")` gives the number 233 and `chr(233)` gives the character back. Type people write that number in hex with `U+` in front, and you translate with `f"U+{number:04X}"` in one direction and `int("00E9", 16)` in the other. A glyph name, a Unicode value and a character are three different things, and a font is what ties them together.

## Try it yourself

1. Find the number and the `U+` form for these characters without opening FontLab: `ß`, `?`, a space, and the first letter of your own name.
2. `ord("a") - ord("A")` gives a number. Work it out, then check whether `ord("z") - ord("Z")` gives the same. Use what you find to print the small letter for `"Q"` with `chr` and `ord` and a sum.
3. Run `what_unicode.py` on the `space` glyph. The line that starts with `Character:` looks unfinished. Why isn't it? Change that line so that the character is printed between two quote marks.

## Next

Chapter 24 answers the question Mira couldn't: given a number, does the font have a glyph for it?
