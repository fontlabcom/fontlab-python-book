---
this_file: src_docs/md/part1-first-words/019-when-it-goes-wrong.md
---

# 19. When it goes wrong

On Friday afternoon Ines tries the new command herself. She has FontLab open and no font in it, because she's between two jobs. She chooses **Scripts > Halfmoon > Friday Report** and gets a block of text she can't read. She copies the last line into a message to Mira:

*AttributeError: 'NoneType' object has no attribute 'info'. Is Plum broken?*

Plum is fine. The script met a situation Mira didn't plan for, and it answered in Python's words, not in hers. You saw this complaint at the end of chapter 18. Today you teach the script to notice trouble and to say something a person can act on.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `Friday Report.py` from chapter 18, in the `Halfmoon` folder inside FontLab's `Scripts` folder.

## Step 1: Find where the nothing came from

Read the complaint the way chapter 3 taught you: from the bottom. The last line names the kind of error and gives the detail. *'NoneType' object has no attribute 'info'* means: you asked for the drawer `info`, and the thing you asked wasn't a font. It was `None`.

The line that failed is this one:

```python
print("Friday report:", font.info.familyName)
```

That line isn't where the trouble began. It began further up, here:

```python
font = fl.CurrentFont()
```

With no font open, FontLab has nothing to hand back, so the box `font` holds `None`. Python doesn't mind. Putting nothing in a box is allowed. The complaint comes later, at the first line that tries to use the nothing as if it were a font. You met the same delay in chapter 5, when `len(font)` failed one line below the line that caused it.

So when a complaint mentions `'NoneType'`, don't stare at the line it points to. Look upward for the box that was filled with nothing.

## Step 2: Ask before you open the drawer

The fix is a question. Before the script touches the font, it asks whether there is one. Try it in the Scripting panel first, in a new script, with every font closed:

```python
from fly import fl

font = fl.CurrentFont()
if font is None:
    print("Open a font first.")
else:
    print("Glyphs:", len(font))
```

```text
Open a font first.
```

Open `Plum-practice` and run it again:

```text
Glyphs: 208
```

`is None` is the test you've used since chapter 16, for glyphs without a Unicode value. It asks: does this box hold the nothing? Its opposite is `is not None`. You could write `font == None` and get the same answer here, but Python people write `is` for this one question, and every script you read will too.

An `if` that stands at the door of a script and turns away the cases it can't handle is called a **guard**.

## Step 3: Leave early

The guard works, but look at what it did to the shape of the script. Everything that used to be the work now has to live under `else:`, pushed four spaces to the right. Add a second guard and the work moves right again.

There's a tidier way, and it uses what you learned in chapter 16. Put the work inside a function called `main`. Inside a function, `return` means "stop here and go back". It doesn't have to hand anything back. So the guard can say its piece and leave, and the rest of the function stays flat against the left edge:

```python
def main():
    font = fl.CurrentFont()
    if font is None:
        print("Friday Report: open a font first.")
        return

    no_unicode = names_without_unicode(font)
    widest = widest_glyph(font)

    print("Friday report:", font.info.familyName)
    print("Date:", date.today())
    print("Glyphs:", len(font))
    print("Without Unicode:", len(no_unicode), no_unicode)
    print(f"Widest: {widest.name} ({widest.width:.0f})")


main()
```

Change `Friday Report.py` so that its last part looks like this. The header, the imports and the two functions above it stay as they were. Don't forget the last line. `def` only teaches Python the step, and `main()` is what performs it. Leave that line out and the command does nothing at all, without any complaint, which is harder to diagnose than an error.

Save, close every font, and choose the command from the menu.

```text
Friday Report: open a font first.
```

The message starts with the name of the command. When you have ten commands in the menu and a line appears in the **Output** panel, you'll want to know who is talking.

The script template from chapter 17 gets a sixth habit: the work goes in `main()`, and `main()` starts with its guards. Open `template.py` and add that now.

## Step 4: The glyph that isn't there

A missing font is one kind of nothing. A missing glyph is the other, and you'll meet it more often. Ask Plum for a small cap that nobody has drawn yet:

```python
from fly import fl

font = fl.CurrentFont()
glyph = font["Q.sc"]
print(glyph)
print(glyph.width)
```

```text
None
AttributeError: 'NoneType' object has no attribute 'width'
```

Asking a font for a name it doesn't have is not an error. The font hands back `None`, and the error waits for the next line. It's the same delay as in step 1, and the same guard cures it. Here it is inside a loop, where it earns its keep:

```python
from fly import fl

font = fl.CurrentFont()
for name in ["a.sc", "b.sc", "Q.sc", "n"]:
    glyph = font[name]
    if glyph is None:
        print(name, "is not in this font")
    else:
        print(name, glyph.width)
```

The first two lines of output depend on the widths your `.sc` glyphs got in chapter 8. The last two are the same for everybody:

```text
Q.sc is not in this font
n 523.0
```

Without the guard, the loop would stop at `Q.sc` and never reach `n`. With it, one missing glyph costs one line of output and the loop goes on. Any time a script works from a list of names that a person typed, some name in the list will be wrong sooner or later. Guard the lookup.

## Step 5: Try it, and catch what falls

A guard works when you can ask beforehand. Sometimes you can't. Then you let Python try, and you catch the complaint yourself.

Tomas sends Mira a column of numbers copied out of his spreadsheet, and she wants the total. Text copied from a spreadsheet arrives as strings, so each cell has to go through `int()`. In chapter 11 it cut floats down. It also reads a number out of a string. Two of his cells aren't numbers:

```python
cells = ["596", "672", "n/a", "708", "", "520"]

total = 0
for cell in cells:
    total = total + int(cell)
print(total)
```

```text
ValueError: invalid literal for int() with base 10: 'n/a'
```

A `ValueError` means the tool got the right kind of thing, a string, with the wrong contents. Could you guard against it? You'd have to describe every string that isn't a number: letters, empty cells, a stray comma, two minus signs. It's less work to let `int()` decide, since it already knows.

```python
cells = ["596", "672", "n/a", "708", "", "520"]

total = 0
skipped = 0
for cell in cells:
    try:
        total = total + int(cell)
    except ValueError:
        skipped = skipped + 1
        print("Not a number:", repr(cell))
print("Total:", total)
print("Skipped:", skipped)
```

```text
Not a number: 'n/a'
Not a number: ''
Total: 2496
Skipped: 2
```

Read it as two instructions. `try:` says: do the indented lines, and watch. `except ValueError:` says: if one of them raises a `ValueError`, don't stop the script. Do these lines, then carry on after the whole block. If nothing goes wrong, the `except` part is skipped.

Two details. `repr(cell)` prints a string with its quotes on, so an empty cell shows up as `''` and not as a blank you could miss. And the script counts what it skipped and says so. A script that drops things without a word is worse than one that stops, because you'll believe its total.

## Step 6: Don't catch everything

Now the mistake, and it's one that experienced people make. You can leave the error's name out and write a bare `except:`. It catches every complaint there is. Watch what that does when the script has a typo in it:

```python
cells = ["596", "672", "n/a", "708", "", "520"]

total = 0
skipped = 0
for cell in cells:
    try:
        total = totl + int(cell)
    except:
        skipped = skipped + 1
print("Total:", total)
print("Skipped:", skipped)
```

```text
Total: 0
Skipped: 6
```

No complaint. The script ran to the end and reported that all six cells were bad. They weren't. Look at the line under `try:`. The box is spelled `totl`. Every turn of the loop raised a `NameError`, the bare `except:` swallowed it, and the script told a confident lie.

Put the name back, `except ValueError:`, and run it again.

```text
NameError: name 'totl' is not defined. Did you mean: 'total'?
```

That's the letter of complaint you needed. It names the typo and even suggests the spelling. An error message is the most useful thing Python gives you, so catch only the one error you expect and can do something about. Let every other error through.

??? info "Going deeper: guard or try?"
    The two tools overlap, and you'll see both styles in other people's scripts. In this book the habit is: guard when a cheap question answers it (`is None`, `len(font) == 0`, `name in names`), and use `try` when the only way to find out is to attempt the thing: turning text into a number, opening a file, asking a server. Keep the `try` block short, one or two lines. The more lines it holds, the more unrelated mistakes it can hide.

    One more guard belongs in `Friday Report.py`. A new font with no glyphs in it isn't `None`, and I haven't tried what `font[0]` in `widest_glyph` does there. A second guard after the first, `if len(font) == 0:`, with its own message and its own `return`, covers that.

## What you learned

`None` travels quietly from the line that produced it to the first line that uses it, so when a complaint mentions `'NoneType'`, look upward for the box that was filled with nothing. A guard, `if font is None:` followed by a message and `return`, stops a script at the door with words a colleague can act on, and the same test keeps a loop alive when one glyph name is missing. When you can't ask beforehand, `try:` and `except ValueError:` let the script attempt something and handle the one failure you expect, and a bare `except:` hides the failures you didn't.

## Try it yourself

1. Give `wide_glyphs.py` in the `Halfmoon` folder the same treatment: a `main()` with a guard that prints "Wide Glyphs: open a font first." Close every font and choose it from the menu.
2. Add the cell `"12.5"` to Tomas's list and run the script from step 5. `int()` refuses it, because it isn't a whole number. Check that the report says so and that the total hasn't changed.
3. Write a function `glyph_width(font, name)` that returns the glyph's width, or `None` when the font has no glyph of that name. Try it with `"A"` and with `"Q.sc"`.

## Next

Chapter 20 puts three weeks of small scripts together into one inventory of the font, and closes the first part of the book.
