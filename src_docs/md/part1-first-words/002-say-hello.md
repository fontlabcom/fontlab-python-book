---
this_file: src_docs/md/part1-first-words/002-say-hello.md
---

# 2. Say hello to FontLab

Monday morning. Mira has `Plum-practice` open and Oskar's sheet propped against her monitor. On Friday she ran one line with Oskar leaning over her shoulder. Today the chair next to hers is empty, and she can't remember which menu he used.

"Where did he type it?" she asks the empty chair.

Her phone buzzes. Oskar, from a train: *Window menu. Panels. Scripting. Type something, press the triangle. Don't think too hard yet.*

It's good advice, and it's the plan for this chapter. You ran one line yesterday. Today we take it apart: where it goes, what each piece of it does, and what happens when you change the pieces. No font work yet.

## What you need

- FontLab 9, running.
- `Plum-practice` open, from [chapter 1](001-the-list-oskar-left.md). We won't touch it today, but it's a good habit.

## The two panels, properly this time

Choose **Window > Panels > Scripting**, if the panel isn't open already.

Most of the panel is a blank area, like an empty page. It's a text editor that lives inside FontLab, and it's where you type Python. Along the top is a small toolbar. At its left end is a button with three lines, ≡, which opens the panel's own menu. Next to it is the triangle, ▶, which FontLab calls **Run script**.

Now choose **Window > Panels > Output**.

You don't type in this one. The **Output** panel is where FontLab talks back. When a script has something to say, it says it here. When a script goes wrong, the complaint lands here too.

Drag the two panels so you can see both, and keep both visible for the rest of this book. You write on one side. FontLab answers on the other.

Type Friday's line again and run it.

```python
print("Hello, Mira")
```

```text
Hello, Mira
```

Your panel may show the time in front of each line. I leave it out.

Now click **Run script** a second time and watch the Output panel. One of two things happens. Either a second `Hello, Mira` appears under the first, or the panel empties and shows one fresh greeting. Which one you get depends on a setting, and I'd like you to choose it yourself. Open the ≡ menu of the Scripting panel and find **Clear Output Panel**. When it's on, every run starts with a clean Output panel. Turn it on. From now on, what you see in the Output panel is what the last run did, with no leftovers from earlier.

If you got an error and no greeting, compare your line with mine, one character at a time. Lowercase `print`. An opening parenthesis straight after it. Double quote marks from the plain quote key. A closing parenthesis.

## Take the line apart

One line, three pieces.

**`print`** is a **function**. A function is a named job that Python knows how to do. This one's job is to write something to the Output panel. Python comes with dozens of functions, FontLab adds many more, and from chapter 16 on you'll write your own.

**The parentheses** are how you tell a function to go. Whatever sits between them is what you hand to the function to work on. Think of a letterbox: `print` is the box and the parentheses are the slot. You push something through the slot and the function deals with it.

**`"Hello, Mira"`** is a **string**. String is the programmer's word for a piece of text. The quote marks aren't part of the text. They're the fence around it, and they tell Python: everything between these two marks is text, so don't try to understand it, only carry it.

Python reads everything you type and tries to make sense of it as instructions. The quote marks are how you say "this part isn't an instruction, this is words." Inside the fence you can put anything:

```python
print("Find kerning pairs that are larger than they should be.")
```

```text
Find kerning pairs that are larger than they should be.
```

Python doesn't know what kerning is. The text was inside the fence, so Python carried it to the Output panel and left it there.

The fence can be built from double quote marks or single ones. Python accepts both, as long as the mark that opens the string is the mark that closes it.

```python
print("Halfmoon Type")
print('Halfmoon Type')
```

```text
Halfmoon Type
Halfmoon Type
```

Why have two kinds? Because sometimes the text has a quote mark in it.

```python
print("Oskar's list")
print('Ines says "Friday"')
```

```text
Oskar's list
Ines says "Friday"
```

The first string has an apostrophe inside, so it gets double quotes outside. The second has double quotes inside, so it gets single quotes outside. Python sees the opening mark and treats everything as text until it meets the same mark again. In this book I use double quotes unless the text forces me to do otherwise.

## More than one line

A script can have as many lines as you want. Python reads them from the top down, one after another, the way you read a recipe.

Replace what's in the Scripting panel with this:

```python
print("Count the glyphs and tell Ines.")
print("Find the glyphs that are still empty.")
print("Make a table of every glyph and its width.")
```

Run it.

```text
Count the glyphs and tell Ines.
Find the glyphs that are still empty.
Make a table of every glyph and its width.
```

Three instructions, three lines of output, in the same order. Each `print` starts a fresh line in the Output panel.

Swap the first and last lines of the script and run it again. The output swaps too. The order of your lines is the order of events. The computer does what you wrote, in the order you wrote it, and nothing else.

## Numbers, alone and in company

Text goes in quotes. Numbers don't.

```python
print(205)
```

```text
205
```

That's the number of glyphs in GG Plum. Without quotes, Python understands 205 as a quantity, something it can do arithmetic with:

```python
print(205 * 3)
```

```text
615
```

The star means "times". GG Plum has 205 glyphs and three weights, so there are 615 drawings in that file. Python worked it out before printing.

Now put the same thing inside quotes and see what changes.

```python
print("205 * 3")
```

```text
205 * 3
```

No arithmetic. Inside the fence it's text, and Python carries text without reading it. So `205` and `"205"` are different things. The first is a number. The second is a picture of a number. You'll mix them up one day, and chapter 3 shows you what Python says when you do.

The other arithmetic signs are what you'd guess: `+` to add, `-` to subtract, `/` to divide.

```python
print(1000 - 742)
print(600 / 2)
```

```text
258
300.0
```

Look at the `300.0`. Division gives an answer with a decimal point, even when it comes out even. Python keeps two kinds of numbers, whole ones and ones with a decimal point, and chapter 11 explains why a type designer should care. For today, `300.0` is 300.

You can also push more than one thing through the slot. Put a comma between them.

```python
print("Plum has", 205, "glyphs")
```

```text
Plum has 205 glyphs
```

Three things went in: a string, a number, a string. `print` wrote them on one line and put a space between each. You didn't have to type the spaces.

Most reports in this book have this shape. Some words to say what the number is, then the number. At the moment you're typing the 205 yourself. In chapter 4 FontLab supplies it, and the line looks much the same.

You can do the sum inside the print, too:

```python
print("That makes", 205 * 3, "drawings in three weights")
```

```text
That makes 615 drawings in three weights
```

## An old habit that no longer works

Sooner or later you'll find a FontLab script on the internet, or in a forum post from years ago, that prints like this:

```python
print "Hello, Mira"
```

No parentheses. Type that into the Scripting panel and run it. Go on, do it on purpose.

No greeting. The Output panel shows an error, and its last line reads:

```text
SyntaxError: Missing parentheses in call to 'print'. Did you mean print(...)?
```

Nothing is damaged. Python read the line, couldn't follow it, and told you why. It even suggests the fix.

The reason is history. Python has had two major versions. In the old one, Python 2, `print` was written without parentheses. FontLab Studio 5 used Python 2, and many scripts from those years are still around. FontLab 9 uses Python 3, where `print` is a function like any other and needs its parentheses.

So when an old script fails on its first `print`, you know what happened and how to mend it. Put the parentheses back and run it again.

## Keep your script

What you type into the Scripting panel isn't saved anywhere until you save it. Let's keep today's work.

Put this in the panel:

```python
print("Hello, Mira")
print("Plum has", 205, "glyphs")
print("That makes", 205 * 3, "drawings in three weights")
```

Run it once to be sure it works.

```text
Hello, Mira
Plum has 205 glyphs
That makes 615 drawings in three weights
```

Then open the ≡ menu and choose **Save Script As…**. Go to the `scripting-book` folder you made in chapter 1, name the file `hello.py` and save.

Open the folder in Finder, or in File Explorer on Windows, and look at the file. A Python script is a plain text file whose name ends in `.py`. There's nothing else to it. You could open `hello.py` in any text editor and read it. You could email it to a friend, who would run it in their FontLab and get the same three lines.

To get it back later, use the same menu and choose **Open Script**. To start with a clean page, choose **New Script**.

In chapter 18 we move your scripts to a place where FontLab lists them in its **Scripts** menu, so you can run them without opening the panel at all. A folder on your desktop is fine until then.

??? info "Going deeper: the Console"
    The Scripting panel's toolbar has a toggle called **Console panel**. Turn it on and you get a prompt that looks like `py>`. Type a line of Python there, press ++return++ (++enter++ on Windows), and it runs at once. The Console is handy for one-line questions. This book uses the main editor, because a script you can save is a script you can run again.

## What you learned

You know where Python goes in FontLab and where the answers come out. You can print text and numbers, on one line or several, and let Python do the arithmetic on the way. And you have a first script, `hello.py`, saved as a file you can open and run again.

## Try it yourself

1. Write a script that prints your name, the name of a typeface you're working on and how many weights it has, each on its own line.
2. A font has 420 glyphs and four weights. Make Python print the sentence `That is 1680 drawings`, with Python doing the multiplication.
3. Print this line, quote marks and apostrophe included: `"Oskar's" list`. Try double quotes on the outside, then single ones. If neither works, good. Bring the error text with you to chapter 3.

## Next

In [chapter 3](003-break-it-on-purpose.md) you make mistakes on purpose and learn to read what Python says about each one.
