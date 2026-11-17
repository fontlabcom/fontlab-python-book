---
this_file: src_docs/md/part1-first-words/008-only-the-ones-i-want.md
---

# 8. Only the ones I want

Tuesday. Ines forwards a one-line message from the publisher:

*Before we plan the proofs: which glyphs in Plum are still empty?*

Mira laughs, because she was about to make that answer longer. The small caps start today. Her plan is to add the glyph cells first, with nothing in them, and draw into them over the next weeks. So the honest answer to the publisher changes this morning, and it'll change again every time she finishes a letter.

It's also the second line on Oskar's sheet: *Find the glyphs that are still empty.*

Yesterday's loop treats every glyph the same way. It prints all 205 of them. Today the loop learns to ask a question about each glyph and to act only when the answer is yes.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open in a Font window.
- `list_names.py` from [chapter 7](007-do-it-to-all-of-them.md). You won't change it, but today's script starts the same way.

## Step 1: Ask a question that has two answers

Clear the Scripting panel, type this and run it:

```python
print(5 > 3)
print(5 > 8)
```

```text
True
False
```

You asked Python two questions. Is 5 greater than 3? Is 5 greater than 8? It answered each with one word.

Now ask about the font:

```python
from fly import fl

font = fl.CurrentFont()
print(font["A"].width)
print(font["A"].width > 600)
```

```text
596.0
False
```

The *A* is 596 units wide, so "is it wider than 600?" gets a no.

A line like `5 > 3` is called a comparison. The two answers, `True` and `False`, are values, like 205 or `"Plum"`. They aren't strings: there are no quotes around them, and the capital letter matters. Python knows `True`. It has never heard of `true`.

There are six comparison signs. You'll use all of them before the year is over:

| You type | It asks |
| --- | --- |
| `a > b` | is `a` greater than `b`? |
| `a < b` | is `a` less than `b`? |
| `a >= b` | is `a` greater than `b`, or equal to it? |
| `a <= b` | is `a` less than `b`, or equal to it? |
| `a == b` | are `a` and `b` equal? |
| `a != b` | are `a` and `b` different? |

Look twice at the fifth one. Two equals signs. Step 3 is about what happens when you type one.

## Step 2: Do it only if the answer is yes

A question by itself prints `True` or `False` and that's all. To make the answer decide something, put the word `if` in front of it:

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if glyph.width > 800:
        print(glyph.name, glyph.width)
```

```text
AE 852.0
M 840.0
OE 989.0
W 859.0
Wacute 859.0
Wcircumflex 859.0
Wdieresis 859.0
Wgrave 859.0
oe 824.0
emdash 1000.0
at 848.0
```

Eleven lines instead of 205. The loop still visits every glyph. For each one it asks "is your width greater than 800?", and it runs the `print` line only when the answer is `True`. The other 194 glyphs pass by in silence.

Read the shape of the `if` line. It's the shape of the `for` line from yesterday: a word, then something to work on, then a colon. And like `for`, it owns the indented lines below it. The `print` line is now indented twice, eight spaces. Four of them say "I belong to the loop". Four more say "and inside the loop, I belong to the `if`".

Press ++tab++ twice to get there, or let the Scripting panel do it: after you type the colon and press ++enter++, the next line may start at the right depth already. Count the spaces if you aren't sure.

Change 800 to 900 and run it again. Two glyphs are left, the *OE* and the em dash. Change `>` to `<` and 900 to 200. One glyph is left: `quotesingle`, the straight quote, 190 units wide. You're asking the font questions now, and it takes about a second each.

## Step 3: One equals sign too few

In Plum, the *O* is 708 units wide. Which other glyphs have that same width? Type this, with one equals sign, and run it:

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if glyph.width = 708:
        print(glyph.name)
```

```text
  File "<string>", line 5
    if glyph.width = 708:
       ^^^^^^^^^^^
SyntaxError: cannot assign to attribute here. Maybe you meant '==' instead of '='?
```

Read the letter of complaint from the bottom, the way you learned in [chapter 3](003-break-it-on-purpose.md). The last line says what went wrong and, this time, even offers the fix.

Here's the reason. In [chapter 5](005-a-font-is-a-list-of-glyphs.md) you learned to read `=` as "becomes". `glyph_count = 205` puts 205 into a box. So `glyph.width = 708` means "the width becomes 708". That's an order. After `if`, Python wants a question, and it got an order, so it stops before running anything. Nothing in your font changed.

The question is spelled with two signs. `==` reads "is equal to":

```python
from fly import fl

font = fl.CurrentFont()
count = 0
for glyph in font.glyphs:
    if glyph.width == 708:
        print(glyph.name)
        count = count + 1
print("Same width as O:", count)
```

```text
O
Oacute
Ocircumflex
Odieresis
Ograve
Oslash
Otilde
Q
Same width as O: 8
```

The *O*, six accented versions of it, and the *Q*. That's a type designer's decision made visible: in Plum the *Q* is an *O* with a tail, and it takes up the same room.

Two more things happened in that script. First, the counter from chapter 7 moved inside the `if`. It used to count every glyph. Now it counts only the ones that pass the test, because the line that adds 1 is indented under the `if`. Second, there's one `=` and one `==` three lines apart, and they do different jobs. `count = count + 1` gives an order. `glyph.width == 708` asks a question.

Everybody types `=` where `==` belongs. I still do it. Python catches it every time, so it costs you five seconds.

## Step 4: What does empty mean?

Back to the publisher's question. A glyph cell is empty when nothing is drawn in it: no outline of its own, and nothing borrowed from another glyph either. The *Aacute* in Plum has no outline of its own, but it isn't empty. It's built from the *A* and the acute accent, and it shows up in text like any other letter.

The `space` glyph is the opposite case. It has a width of 230 units and nothing at all in it. It's empty on purpose.

The glyph you get from `font.glyphs` doesn't have a drawer that says "empty". It's the plain kind of glyph: name, Unicode value, width. For this question you need a second tool from the bag you packed in [chapter 4](004-pack-the-toolbag.md). Type this and run it:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

font = fl.CurrentFont()
print(pGlyph(font, font["space"]).isEmpty())
print(pGlyph(font, font["A"]).isEmpty())
print(pGlyph(font, font["Aacute"]).isEmpty())
```

```text
True
False
False
```

There's the answer for three glyphs: the space is empty, the *A* isn't, and the *Aacute* isn't either.

I owe you an explanation for two lines, and I'm going to pay only part of it today.

The second line is long. Treat it as a magic line for now: copy it exactly, dots and all. It fetches a tool called `pGlyph` from deep inside the toolbag. The path is long because the bag has many pockets, and this tool lives four pockets down. In Part 2 you'll learn to read such a line piece by piece.

`pGlyph(font, glyph)` takes two things through the slot: the font and one plain glyph from it. It hands back a richer version of the same glyph, one that knows more about its own drawing. One of the things it knows is `isEmpty()`. The parentheses at the end are there because `isEmpty` isn't a drawer with a value lying in it. It's a question the glyph works out when you ask, the way `len()` works out a count. Nothing goes through the slot, but the slot has to be there.

And what comes back is `True` or `False`. That's the kind of answer `if` wants.

## Step 5: Mira adds three cells, and the script finds them

Before the script runs over the whole font, give it something to find. Mira starts her small caps with three placeholders, and you'll do the same.

1. Click the Font window of `Plum-practice`.
2. Choose **Font > New Glyph…**.
3. Type the name `a.sc` and confirm.
4. Do it twice more, for `b.sc` and `c.sc`.

You now have three new cells with nothing drawn in them. The name `a.sc` is a convention: the part before the dot says which letter it is, and the part after the dot says which version. `sc` is short for small cap. The next chapter takes such names apart.

Now the script. Start a new one:

```python
from fly import fl
from fly.tr.proxy.fl.objects.glyph import pGlyph

font = fl.CurrentFont()
count = 0
for glyph in font.glyphs:
    if pGlyph(font, glyph).isEmpty():
        print(glyph.name)
        count = count + 1
print("Empty:", count, "of", len(font))
```

```text
space
a.sc
b.sc
c.sc
Empty: 4 of 208
```

Save it as `empty_glyphs.py` in your `scripting-book` folder.

Look at the `if` line. There's no `>` and no `==` in it. There doesn't have to be. `if` needs something that is `True` or `False`, and `isEmpty()` already hands back one of the two. You could write `if pGlyph(font, glyph).isEmpty() == True:` and it would work, but it says the same thing twice, like "if it is true that the glyph is empty".

The font has 208 glyphs now, not 205, and `len(font)` knows it without being told. That's the reason the script asks the font for the count instead of having the number typed into it.

Mira writes back to the publisher: *Four. One is the space, which stays empty. Three are small caps I started this morning. There will be more of those before there are fewer.* Then she takes Oskar's sheet and crosses out line 2.

When she adds twenty more cells next week, she won't count them. She'll run `empty_glyphs.py` again.

## Step 6: Test for nothing

One more question, because it uses a value you met in chapter 5. In [chapter 6](006-ask-a-glyph-its-name.md) you saw that the `unicode` drawer holds a number for most glyphs. For a glyph without a Unicode value, the drawer holds `None`, Python's word for "nothing here". You can compare with it:

```python
from fly import fl

font = fl.CurrentFont()
for glyph in font.glyphs:
    if glyph.unicode == None:
        print(glyph.name)
```

```text
.notdef
a.sc
b.sc
c.sc
```

Four glyphs that no key on a keyboard reaches directly. The `.notdef` is the box a font shows when it has no glyph for a character. The three small caps have no Unicode value because Unicode has no separate numbers for small caps: an *a* is an *a*, however you dress it. Fonts reach such glyphs through OpenType features, which is a story for Part 5.

Notice that the two lists overlap but aren't the same. `space` is empty and has a Unicode value. `.notdef` has a drawing and no Unicode value. "Empty" and "has no Unicode value" are different questions, and now you can ask either.

??? info "Going deeper: `is None`"
    When you read other people's scripts, you'll see `if glyph.unicode is None:` more often than `== None`. Both work here. `is` asks "is this the very same thing?", and since Python keeps exactly one `None`, that's the stricter and more usual way to ask. Use whichever you can read aloud more comfortably. I'll write `is None` from now on.

## What you learned

A comparison such as `glyph.width > 800` is a question, and Python answers it with `True` or `False`. Put `if` in front of the question and a colon behind it, and the indented lines below run only when the answer is `True`. Inside a loop, that turns "do it to all of them" into "do it to the ones I want". One `=` gives an order and two ask a question, and when you mix them up, Python tells you before anything runs.

## Try it yourself

1. Change the script from step 2 so it prints the glyphs that are 859 units wide or wider. Use `>=`. You should get seven names: `OE`, five W's and `emdash`.
2. Change the script from step 6 so it counts the glyphs that do have a Unicode value, and prints only the count after the loop. Use `!=`. Add your number to the four glyphs from step 6. Do you get 208?
3. In `empty_glyphs.py`, the `if` line picks the empty glyphs. Change it so the script counts the glyphs that are not empty, by comparing the answer with `False`. Don't save over the original.

## Next

Chapter 9 looks inside glyph names. A name is a string, a string is made of letters, and Python can check how a name starts, how it ends and what's in the middle. That's how you find every `.sc` without typing the list.
