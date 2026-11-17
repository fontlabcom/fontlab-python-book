---
this_file: src_docs/md/part1-first-words/001-the-list-oskar-left.md
---

# 1. The list Oskar left

Oskar's last day at Halfmoon Type is a Friday. He waters the plant, wipes his desk and puts one sheet of paper on Mira's keyboard.

"That's everything I do that nobody sees," he says.

Mira reads the first line. *Count the glyphs and tell Ines.* Then the second. *Find the glyphs that are still empty.* There are eleven lines. Next to most of them Oskar has written the same three words in pencil: *an afternoon by hand.*

"Forty afternoons," Mira says.

"Forty afternoons every time the client changes something," Oskar says. "I stopped doing them by hand years ago. There's a folder called `chores` on the shared drive. Start there." He picks up his bag. "You draw better than I ever did. You'll be fine."

Mira has never written a line of code.

That's where this book starts, and I suspect it's close to where you start. You draw type, or you want to. And somewhere in your week there's a job that takes an afternoon, needs no talent and comes back every time something changes.

This book is about handing those jobs to FontLab.

## What you need

- FontLab 9.
- An internet connection, to download one practice font.
- No Python and no programming. We start from nothing.

## What a script is

A script is a list of instructions in a text file. You write the instructions, FontLab follows them.

You already give FontLab instructions all day. You click a glyph, you pick a menu command, you type a number into a field. Each click is an instruction. The trouble with clicks is that FontLab forgets them. If you fix the spacing of 30 glyphs on Tuesday and the client changes the brief on Wednesday, you click 30 times again.

A script doesn't forget. You write down what you want once, in a language FontLab understands, and from then on the job costs you one click. If the brief changes, you change one line and run it again.

The language is called Python. FontLab 9 has Python built in, so there's nothing to install before you write your first line. People who have nothing to do with type use Python too: scientists, accountants, people who build websites. That's good news for you. What you learn here works elsewhere, and the world is full of free Python lessons if you ever want a second teacher.

Scripts in this book stay short. Most are under 20 lines. You'll run your first one before this chapter ends.

One thing before we go on. **Halfmoon Type is invented.** So are Mira, Oskar and Ines. I made them up because chores need a setting. Mira asks the questions a beginner asks, and I'm the one who answers. FontLab, Python and the fonts are real.

## Get the practice font

You're not going to practice on your own typeface. Not yet. You're going to practice on a font you can wreck.

In the story, Halfmoon's typeface for the publisher is called Plum. On your screen it's played by **GG Plum**, a real font from FontLab's GetGo Fonts collection. Its license is CC0, which means it's in the public domain. You may open it, change it and break it.

GG Plum has 205 glyphs and three weights: Light, Regular and Bold. That's small enough to see all at once and large enough to make hand work tedious, which is what we want.

To get it:

1. Go to [GetGo Fonts](https://fontlabcom.github.io/getgo-fonts/) and download the collection for FontLab. It arrives as one ZIP file.
2. Unpack the ZIP. Inside, open the `cc0` folder, then the `plum` folder.
3. You'll find a file called `plum-var.vfj`. That's the one we want. A `.vfj` file is a font in one of FontLab's own formats, with everything still editable.

## Open it and look around

Start FontLab 9. Choose **File > Open Fonts…** (++cmd+o++ on a Mac, ++ctrl+o++ on Windows), find `plum-var.vfj` and open it.

You may know most of what follows. I go through it because I use these words in every chapter.

FontLab shows you the **Font window**: a grid of small boxes. Each box shows one drawing and a name. Capitals, lowercase, figures, punctuation and accented letters are all there.

What you're looking at is a **font**: a file that carries a typeface design to a computer. And each box holds a **glyph**: one drawn shape with a name. The capital A is a glyph. So is the comma. So is `space`, a glyph with nothing drawn in it. Find it in the grid. Its box looks empty because it is.

Read a few of the names. `A`, `a`, `comma`, `Aacute`, `germandbls`. Every glyph in a font has a name, and no two glyphs in one font share one. When a script wants a glyph, it asks for it by name, so you'll be reading and typing these names a lot.

Now find `a` and `aacute`, the *a* with an acute accent. Double-click `aacute`. FontLab opens the **Glyph window**, which is where you draw. You see the outline of the letter with the accent above it.

Here's one distinction to carry with you. A glyph isn't the same thing as a **character**. A character is what you type: the idea "lowercase a". A glyph is what you see: one particular drawing. One character can have several glyphs. A font may hold a normal *a* and a second, fancier *a* for the ends of words. And one glyph can stand for two characters, the way a joined *fi* does. FontLab keeps the two apart, so we will too.

That's all the vocabulary this chapter needs: font, glyph, name, and the difference between a glyph and a character. Widths, outlines, kerning and the rest each arrive when a chore needs them.

Every one of the things you looked at is something a script can ask about. How many glyphs? What's this one called? Is anything drawn in it? And nearly every one is something a script can change, many glyphs at a time.

## Save a copy you can break

**Never practice on the original.**

With the font open, choose **File > Save Font As**. Name the copy `Plum-practice.vfj` and put it in a folder you'll find again. I keep a folder called `scripting-book` on my desktop for this.

From now on you work in `Plum-practice`. The file you downloaded stays untouched in its folder. If a script in chapter 30 turns every glyph inside out, you open the original and save a fresh copy.

There are two more nets under you. FontLab's Undo can take back what a script did, but not always in one step. Part 2 shows you how to make a script undo cleanly. And **File > Revert Font** throws away everything since the last save.

Until Part 2, the copy is your net. As long as the font you're working in is `Plum-practice`, you can try anything.

## Run one line

Before Mira goes home, Oskar leans over her keyboard one last time. "You should see it work once," he says. "Then the weekend is easier."

So let's see it work once.

Choose **Window > Panels > Scripting**. A panel opens with a blank area, like an empty page. Then choose **Window > Panels > Output**. A second panel opens. Arrange them so you can see both.

Click in the blank area of the Scripting panel and type this line:

```python
print("Hello, Mira")
```

Lowercase `print`, an opening parenthesis, a double quote mark from the plain quote key, the words, the same quote mark again, a closing parenthesis.

In the toolbar at the top of the Scripting panel there's a triangle, ▶. FontLab calls it **Run script**. Click it.

Look at the Output panel.

```text
Hello, Mira
```

You wrote an instruction and FontLab carried it out. That was a script.

Now do what Mira does next. She changes `Mira` to `Oskar`, forgets the last quote mark, and clicks the triangle.

```python
print("Hello, Oskar)
```

No greeting this time. The Output panel shows a few lines she didn't ask for, and the last one reads:

```text
SyntaxError: unterminated string literal (detected at line 1)
```

"That's an error," Oskar says. "It means the line was wrong. The font's fine. Put the quote mark back."

She does, and runs it again.

```text
Hello, Oskar
```

That's the whole cycle of scripting, and you've now been around it once: type, run, read, fix, run again. Chapter 2 takes the line apart. Chapter 3 is all about errors.

## Read the list

Mira takes Oskar's sheet home for the weekend. Here are the lines.

- Count the glyphs and tell Ines.
- Find the glyphs that are still empty.
- Make a table of every glyph and its width.
- List the glyphs that are built from other glyphs.
- Mark every glyph that mixes its own outlines with borrowed ones.
- Make the left sidebearing of the *d*, *q* and *g* match the *o*.
- Rebuild the accented letters from the base letters and the accents.
- Find kerning pairs that are larger than they should be.
- When the small caps come: list every glyph whose name ends in `.sc`.
- Put the right family name and version number into every weight.
- Export the whole family to a dated folder every Friday.

Some of these words may be new. Each gets explained when its chore comes up.

Read the list again and notice how the lines are written. None of them needs an eye for type. Each one is a rule applied to many glyphs: *every* glyph, *all* the weights, *each* pair. A person gets bored and makes mistakes on glyph 140. A script does glyph 140 the way it did glyph 1.

That's the test for whether a job belongs in a script. If you can say it as "for every one of these, check this, then do that," it does. If it needs you to squint and decide whether a curve looks right, it stays yours.

By the end of Part 1 you'll have done the first few chores on that list. By the end of the book you'll have worked through the rest, and built a few tools of your own that Oskar never thought of.

On Monday, Mira opens FontLab again.

## What you learned

You can now say what a script is, open a font in FontLab and name what you see: a font, its glyphs, their names. You have a copy of GG Plum that you're free to break. And you've run one line of Python, broken it and mended it.

## Try it yourself

1. In the Font window of `Plum-practice`, open `o` in the Glyph window, then `d`. Compare the gap between the drawing and the vertical line on the left side. Does it look the same in both? Now compare the gaps on the right. Should those match? Hold on to your answers. In Part 4 a script will give you the numbers.
2. Count the glyphs in the font by hand, or try to. Stop when you get bored and write down how far you got. Chapter 4 does it in a few lines.
3. Write your own list. Think of three jobs from your own work that fit the sentence "for every one of these, check this, then do that." Keep the list near your desk. By the end of Part 2 you'll be able to script at least one of them.

## Next

In [chapter 2](002-say-hello.md) you take the line you ran today apart, piece by piece.
