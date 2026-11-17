---
this_file: src_docs/md/part1-first-words/003-break-it-on-purpose.md
---

# 3. Break it on purpose

Tuesday. Mira types a line from memory, clicks the triangle, and the Output panel fills with text she didn't write.

She pulls her hands off the keyboard as if it were hot.

"I broke it," she tells Ines, who's passing with coffee.

Ines looks at the screen. "Is the font still there?"

It is. `Plum-practice` sits in its window, every glyph in place.

"Then you didn't break it," Ines says. "You got a letter of complaint. Read it."

That text is called an **error**, and an error is Python telling you what kind of problem it found, where, and often how to fix it. People who script for a living get these letters many times a day. They don't make fewer mistakes than a beginner. They've stopped being afraid of the letter, and they read it. So today you make mistakes on purpose, one at a time, with me standing next to you.

## What you need

- FontLab 9 with the **Scripting** and **Output** panels open, as in [chapter 2](002-say-hello.md).
- **Clear Output Panel** turned on in the Scripting panel's ≡ menu, so each run starts clean.

## Names Python doesn't know

Start with a line that works.

```python
print("Oskar")
```

```text
Oskar
```

Now take the quote marks away and run it again.

```python
print(Oskar)
```

No `Oskar` this time. Read what you got from the bottom, because the last line is the one that counts:

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
NameError: name 'Oskar' is not defined
```

The lines above the last one may look a little different in your Output panel. Here's how to read the whole thing.

The top line, `Traceback`, means "here's the path I was on when I fell over." You can skip it.

The middle line says **where**. The part to look for is `line 1`. Python counts the lines of your script from the top, starting at 1, and tells you which one it was reading when things went wrong.

The last line says **what**. It has two halves with a colon between them. `NameError` is the kind of problem. `name 'Oskar' is not defined` is the explanation, in something close to English.

So what happened? Remember the fence from chapter 2. Inside quote marks, text is only text. Without the fence, Python tries to understand the word. It reads `Oskar` and assumes this must be the name of something it has been told about. It looks through everything it knows, finds no Oskar and gives up. *Name not defined* means "you're talking about something as if I should know it, and I don't."

Put the quotes back. The error goes away.

`NameError` nearly always means one of two things: you forgot the quotes around some text, or you mistyped a name.

Here's the mistyped kind. Run this.

```python
Print("Oskar")
```

```text
NameError: name 'Print' is not defined
```

From here on I show only the last line of each error, since that's where the news is.

Same kind of error, different cause. Python is **case-sensitive**. To Python, `print`, `Print` and `PRINT` are three different words, the way `a` and `A` are two different glyphs to you. Python knows `print`. It has never heard of `Print`.

Your message may be a little longer than mine. Some versions of Python add a guess at the end, such as *Did you mean: 'print'?* When Python offers a guess, try it. So read every message to its end before you start hunting.

Glyph names are case-sensitive too. `A` and `a` are different glyphs, `Aacute` and `aacute` are different glyphs, and a script that asks for `germandbls` won't find `Germandbls`. A lot of scripting is spelling.

## A string with no end

Now take away only the closing quote mark. You met this one on Friday.

```python
print("Oskar)
```

```text
SyntaxError: unterminated string literal (detected at line 1)
```

A new kind: `SyntaxError`. **Syntax** is grammar. A `NameError` means Python understood your sentence but didn't know one of the words. A `SyntaxError` means Python couldn't make out the sentence at all.

In plain words, "unterminated string literal" says: a piece of text was opened and never closed. Python saw the opening quote, started treating everything after it as text, and ran off the end of the line still waiting for the closing mark. The fence has no second post.

These two kinds of error behave differently, and you can test it. Run this three-line script, where the mistake is on the last line:

```python
print("one")
print("two")
print(Oskar)
```

```text
one
two
NameError: name 'Oskar' is not defined
```

Python ran the first two lines, printed their output and stopped at the third. Now change the last line to the broken string:

```python
print("one")
print("two")
print("Oskar)
```

```text
SyntaxError: unterminated string literal (detected at line 3)
```

No `one`, no `two`. Nothing ran. Before Python runs a script, it reads the whole thing to check the grammar. If the grammar is wrong anywhere, it refuses to start.

Keep that in mind when you begin changing fonts. A `SyntaxError` means nothing happened. Any other error means the script got some of the way and stopped, so some of your glyphs may be changed and others not. Part 2 shows you how to make that safe.

!!! tip "A quote mark inside the quotes"
    At the end of chapter 2 I asked you to print `"Oskar's" list`. Whichever mark you put on the outside, the same mark inside ended the string too early. The way out is the backslash. `\'` means "this apostrophe is part of the text", so `print('"Oskar\'s" list')` works. The backslash itself isn't printed.

## The quotes a type designer loves

Copy this line from the page and paste it into the Scripting panel. Don't retype it.

```python
print(“Oskar”)
```

```text
SyntaxError: invalid character '“' (U+201C)
```

To your eye, those are the correct quote marks. They're the ones you draw with care and kern against the *A* and the *T*. Python can't use them.

This message speaks your language. It shows you the character it stopped at, and then its Unicode value, `U+201C`. That's the left double quotation mark. Python wants `U+0022`, the plain straight one, or `U+0027`, the plain apostrophe.

You get curly quotes when code passes through a program that tries to help with typography: a word processor, an email, some chat apps, a note-taking tool. They see straight quotes and curl them. The fix is to retype the quote marks yourself, from the plain quote key.

The same thing happens with dashes. A minus sign that has been turned into an en dash gives you the same error with a different number. When you see `invalid character`, look at the number and you'll know what crept in.

## The parenthesis that never closed

Leave off the last parenthesis.

```python
print("Oskar"
```

```text
SyntaxError: '(' was never closed
```

Every opening parenthesis needs a closing one. The same holds for the square brackets and curly braces you'll meet later.

A close cousin turns up when you leave out a comma between two things:

```python
print("Plum has" 205)
```

```text
SyntaxError: invalid syntax. Perhaps you forgot a comma?
```

"Invalid syntax" is the vaguest thing Python says. It means "this isn't a sentence, and I can't tell you more." Here it adds a guess, and the guess is right. When it adds nothing, look for what's missing: a comma, a parenthesis, a quote mark.

## Text plus a number

One more, and this one is a different sort of trouble. The grammar is fine, and every name is known.

In chapter 2 you joined things with commas inside `print`. A plus sign can join two strings as well:

```python
print("Half" + "moon")
```

```text
Halfmoon
```

The plus glues the two strings end to end. Now try gluing a string to a number.

```python
print("Plum has " + 205)
```

```text
TypeError: can only concatenate str (not "int") to str
```

A `TypeError` means you asked for something that doesn't make sense for the kind of thing you have. "Concatenate" is a long word for "glue end to end." `str` is short for string. `int` is short for integer, a whole number. So the message says: I can glue a string only to another string, and you handed me a whole number.

Python won't guess. Should `"Plum has " + 205` glue, or add? It refuses to pick, and tells you so.

There are two ways out. The first you already know: use a comma, and let `print` handle it.

```python
print("Plum has", 205)
```

The second is to turn the number into a string yourself, with a function called `str`:

```python
print("Plum has " + str(205))
```

Both print `Plum has 205`. In this book I use the comma for quick reports. Chapter 12 shows a third way, the one I use for tables.

## How to read any error

Every error in this chapter gave way to the same routine, so here it is in one place. When the Output panel shows an error:

1. **Go to the last line.** That's the message.
2. **Read the word before the colon.** It tells you the kind of problem. `SyntaxError`: the grammar is wrong, and nothing ran. `NameError`: Python met a word it doesn't know. `TypeError`: wrong kind of thing for the job.
3. **Read the rest of that line, to the end.** If Python offers a guess, try it.
4. **Find the line number**, in the message or in the lines above it, and look at that line in your script, one character at a time.
5. **Change one thing, and run again.** One thing. If you change three things and the error goes away, you won't know which one mattered.

Here's the list Mira pins to the wall next to Oskar's sheet.

| The last line starts with | In plain words | Look for |
|---|---|---|
| `NameError: name '…' is not defined` | Python doesn't know this word | missing quotes, a typo, a wrong capital letter |
| `SyntaxError: unterminated string literal` | a string was opened and not closed | a missing or mismatched quote mark |
| `SyntaxError: invalid character` | a character Python can't use | curly quotes or a dash pasted from elsewhere |
| `SyntaxError: '(' was never closed` | a parenthesis is missing | count the opening and closing ones |
| `SyntaxError: invalid syntax` | Python can't follow the line | a missing comma or other small mark |
| `SyntaxError: Missing parentheses in call to 'print'` | an old Python 2 script | put parentheses around what `print` gets |
| `TypeError: can only concatenate str` | text glued to a number with `+` | use a comma, or `str()` |

Later chapters add rows to this table as new kinds of trouble turn up. Chapter 19 comes back to errors with a font open and real work at stake.

One last thing. Sometimes you'll meet an error whose message you can't make sense of, however slowly you read it. Copy the last line and paste it into a search engine. Somebody has had it before you, and somebody else has explained it. Every programmer does this.

Mira reads her letter of complaint again, from the bottom this time. *NameError: name 'Print' is not defined.* She looks at her line, fixes the capital P and clicks the triangle.

"Complaint withdrawn," she says.

## What you learned

You can read an error now: last line first, the kind before the colon, then the line number. You know that a `SyntaxError` means nothing ran, and that any other error means the script stopped part of the way through. The table above is your summary. Keep it where you can see it.

## Try it yourself

1. Each of these three lines has one mistake. Run them one at a time. Before you run a line, say out loud which error you expect, then see if you were right.

    ```python
    print("Regular", "Bold)
    ```

    ```python
    print(Light)
    ```

    ```python
    pront("Bold")
    ```

2. Write a three-line script where the second line has a `NameError`. Run it and note which lines printed. Then change the mistake into a `SyntaxError` and run it again. What printed this time, and why?
3. Open `hello.py` from chapter 2 and add one of these lines at the end: `print(10 / 0)` or `print("Plum" * "3")`. Run it and read the message. Then add your own row to the table above.

## Next

In chapter 4 you install the toolbag that Oskar's scripts depend on, and FontLab counts the glyphs for you.
