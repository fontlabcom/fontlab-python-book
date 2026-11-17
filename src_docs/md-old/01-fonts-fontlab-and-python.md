---
this_file: src_docs/md/01-fonts-fontlab-and-python.md
---

# 1. Fonts, FontLab and Python

A useful first script can be one line long. Before you write it, you need to know where that line runs, what it can reach, and what you expect to see. This chapter connects three subjects: the font you are making, the editor you use, and the language that lets you automate part of the work.

You need no programming experience to read this chapter. The exercise uses FontLab 9, requires no open font, and prints a message without changing font data.

## A typeface becomes usable font data

A **typeface** is a design: the related forms and proportions that give letters their appearance. A **font** contains data that software can use to display that design. A **font family** groups related fonts, such as Regular and Bold. These terms describe different aspects of the same work. You design the forms; you deliver font data that applications can use. [FontLab manual: Fonts and font families](https://help.fontlab.com/fontlab/9/articles/fonts-and-font-families/index.html).

Suppose you are designing a fictional family called Harbour Sans. Its Regular and Bold drawings belong to the same typeface. If you deliver those two styles as separate font files, each file contains the data for its particular style. The family is the relationship between them, not a third drawing or an extra file.

### Characters and glyphs

A **character** is a unit of text, such as the lowercase letter *a*. A **glyph** is a form supplied by a font to represent text. Unicode identifies the character *a* with the codepoint `U+0061`; it does not prescribe the drawing of its bowl or stem.

The distinction matters when you write scripts. A font can contain several glyphs for one character, such as alternate forms of *a*. Conversely, an application may display two characters with one ligature glyph, such as an *fi* combination. Counting characters in text and counting glyphs in a font therefore answer different questions. [FontLab manual: Fonts and encodings](https://help.fontlab.com/fontlab/9/articles/fonts-and-encodings/index.html).

Font data also includes spacing and rules that help applications select and position glyphs. The application interprets those rules. A font does not itself run the text-layout process.

## What FontLab does

FontLab is a font editor for macOS and Windows. You use it to draw and edit glyphs, adjust spacing, organize families and export fonts for use in other applications. Its tools cover both the shapes you see and the data needed to make those shapes work in text. [FontLab product overview](https://www.fontlab.com/font-editor/fontlab/).

Many tasks begin with direct editing: you choose a tool, select something and make a change. Scripting gives you another way to describe a task. For example, a script can inspect font data and prepare a report, or apply a repeated operation to a chosen group of glyphs. The FontLab 9 manual describes both reading and editing through Python. [FontLab manual: Python scripting](https://help.fontlab.com/fontlab/9/articles/python-scripting/index.html).

Before automating an edit, write its scope in ordinary language. “Report on the selected glyphs” and “change every glyph in every open font” are very different requests. For your first exercise, the scope is smaller: display one message.

## Python and the application

**Python** is a programming language. A **script** is a program you write in that language to carry out a task. The **interpreter** is the software that executes Python code. Python can work with text and numbers independently of a font editor. [Python tutorial: Whetting your appetite](https://docs.python.org/3.11/tutorial/appetite.html).

FontLab 9 includes Python 3.11. You do not need to install another copy of Python for this exercise. Its **Scripting** panel provides an editor for your code, and its **Output** panel displays printed messages and errors. [FontLab manual: Python scripting](https://help.fontlab.com/fontlab/9/articles/python-scripting/index.html).

Later scripts will use an **application programming interface**, usually shortened to **API**: the functions and objects through which code accesses FontLab. Ordinary Python instructions and FontLab API calls are separate things. The line below uses Python's own `print` function; it needs no FontLab API import.

## Print your first message

The panel route below follows the FontLab 9 manual. The code and expected output have been checked in Python 3.11 outside FontLab; the panel procedure has not yet been independently tested for this book.

1. Open **Window > Panels > Scripting**.
2. If the editor contains code, choose **Save Script As...** from the panel's local menu and save it under a new `.py` filename. Before continuing, open that file in a text editor and confirm that the saved copy contains your existing work.
3. Choose **New Script** from the panel's local menu.
4. Check that the editor is empty, then enter this line:

    ```python
    print("My first FontLab script")
    ```

5. Confirm that the sample line is the only code in the editor.
6. Click **Run**.
7. Open **Window > Panels > Output** and look for this message:

    ```text
    My first FontLab script
    ```

The quoted text is a **string**, Python's type for text. The quotation marks tell Python where that text begins and ends. The parentheses supply it to `print`, which writes the message without the enclosing quotation marks. [Python tutorial: Text](https://docs.python.org/3.11/tutorial/introduction.html#text).

Change only the words between the quotation marks, then run the script again. The new message should appear in **Output**. Keep the plain quotation marks, the parentheses and the lowercase spelling of `print`.

You now have a small experiment you can repeat: change an input, run the code, and compare the output with what you expected. Before a script edits a font, you will need the same clarity about which data it reads, which data it changes and how you will inspect the result.
