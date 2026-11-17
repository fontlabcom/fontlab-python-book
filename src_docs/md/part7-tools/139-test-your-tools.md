---
this_file: src_docs/md/part7-tools/139-test-your-tools.md
---

# 139. Test your tools

It's Monday 11 January. On Friday the build stopped at "Glyph proof" the first time through, and it took twenty minutes to find out why.

The week before, Mira had tidied `proof_html.py`, chapter 115's glyph proof. One of the things she tidied was its copy of `key`, the small function from chapter 112 that makes two spellings of a name comparable. She took out `.lower()`, because the names she was looking at were all in the same capitals anyway. They weren't, for one weight. The proof uses `key` to find font files, and it stopped finding one.

The change was one word, the build broke, and nobody knew for four days. Today you write down what your functions are supposed to do, in a form Python can check in a second, in the Terminal, with FontLab closed.

## What you need

`uv` from chapter 4 and the Terminal from chapter 137. The `spacing-tools` folder from chapter 133, with copies of chapter 115's `proof_html.py` and chapter 136's `plum_report.py` put inside it, next to `pyproject.toml`. No FontLab at all.

This is the one chapter where I can say the opposite of what I usually say. I ran all of it. Every block of Terminal output below is copied from a real run on my machine, including the failures. Your version numbers and timings will differ.

## Step 1: A claim Python can check

You have checked your work all through this book by running a script and reading what it printed. That works, and it has two costs. You have to be there. And you have to remember what the right answer looked like.

`assert` is a Python word that does the reading for you:

```python
assert 2 + 2 == 4
assert len("Plum") == 4
```

`assert` is followed by something that should be true. If it is, nothing happens at all, and the script goes on. If it isn't, the script stops with an `AssertionError`. A line of `assert` is a claim, written where Python can hold you to it.

A test is a function that makes a few such claims about one of your functions:

```python
def key(text):
    return "".join([c for c in text.lower() if c.isalnum()])


def test_key_ignores_capitals_and_punctuation():
    assert key("Plum-SemiBold") == key("plum semibold")
```

The test's name says what's being claimed, in words, and starts with `test_`. That start matters, as you'll see in a moment.

Notice what the test doesn't say. It doesn't say how `key` works. It says what must come out for something that goes in. Mira could rewrite `key` from top to bottom tomorrow, and as long as those two spellings still come out equal, the test has no complaint. A test fixes the behaviour and leaves the code free.

## Step 2: Something to run them

You could call each test function yourself. There's a tool that does it for you, and it's the one nearly everybody uses: pytest. It looks in the folder for files whose names start with `test_`, runs every function in them whose name starts with `test_`, and reports.

It isn't installed, and it doesn't need to be. In the Terminal, in the `spacing-tools` folder:

```text
uv run --no-project --with pytest --with fontParts pytest -q
```

The `-q` at the end asks pytest for its short report. This is chapter 137's `--with` again: run pytest, with pytest and fontParts available for this one run. You'll need fontParts in step 4. `--no-project` is new. `uv` sees the `pyproject.toml` that chapter 133 wrote for FontLab's installer and takes the folder for a project of its own kind, which it isn't: without those two words it stops and complains that the file has no version.

## Step 3: A file you can't import

Here is the natural first test file, and the mistake. Save it as `test_proof.py` in `spacing-tools`:

```python
from proof_html import key


def test_key_ignores_capitals_and_punctuation():
    assert key("Plum-SemiBold") == key("plum semibold")
```

Run pytest:

```text
test_proof.py:1: in <module>
    from proof_html import key
proof_html.py:7: in <module>
    import fly.ap.core.scripting as scripting
E   ModuleNotFoundError: No module named 'fly'
```

The test never ran. `key` needs nothing from FontLab; it takes a string and returns a string. But it lives in a file whose imports need FontLab, and importing one function means importing its whole file. The last line of pytest's report says `Interrupted: 1 error during collection`: it gave up before running any test in any file.

Delete `test_proof.py`. As long as it's in the folder, pytest stops there and runs nothing else.

The cure is to sort your functions by what they need. The plain functions can't stay in a script that starts by importing Fly, because Python runs those imports before it lets you have anything else from the file. They need a package of their own, of the kind chapter 133 made. In `spacing-tools`, make a folder `plain` beside the folder `spacing_tools`, and in it a file `__init__.py`:

```python
# Small functions that need nothing from FontLab, so that tests can
# import them anywhere. FontLab scripts borrow them from here.


def key(text):
    return "".join([c for c in text.lower() if c.isalnum()])
```

Then, in `proof_html.py`, delete `def key` and its line, and put this line with the other imports:

```python
from plain import key
```

The rest of `proof_html.py` still says `key(...)`, so nothing else in it has to change. `key` is now a borrowed name, and the function itself lives where a test can reach it. Copy the changed `proof_html.py` back over the one FontLab runs.

FontLab has to be able to find `plain` too, or the glyph proof stops with `No module named 'plain'`. In `pyproject.toml`, the line chapter 133 wrote becomes:

```text
packages = ["spacing_tools", "plain"]
```

When the tests pass, run chapter 133's Check Package, run `install.vfpy` again and restart FontLab. I haven't seen that second install run.

This is the lasting idea of the chapter, more than `assert` or pytest. A function that works something out from plain values can be tested anywhere. A function that reaches into FontLab can only be tested in FontLab, by hand. So keep the working-out apart from the reaching-in. You did this in chapter 136 without being told why: `summary` and `lines` are handed a font and print nothing.

## Step 4: A font for the tests

`plum_report.summary` needs a font. There isn't one in the Terminal.

Chapter 136 solves this too. `summary` uses only names from the fontParts agreement, and the fontParts project ships plain objects that keep that agreement with no editor behind them. A test can build a tiny font from those in a dozen lines, with glyphs whose every number you chose:

```python
from fontParts.fontshell import RFont

font = RFont(showInterface=False)
glyph = font.newGlyph("n")
glyph.unicode = 0x6E
glyph.width = 600
print(len(font))
```

`RFont(showInterface=False)` makes an empty font and no window. `newGlyph` adds a glyph and hands it back. `0x6E` is the code for `n`, written the way chapter 6 showed.

Because you built the font, you know the right answers before the report runs. That's what makes a claim possible. You can't write `assert facts["glyphs"] == 274` about Plum and trust it next month, when Plum has 280. You can write `== 4` about a font you made with four glyphs, and it stays true.

## The whole script

```python
# Tests for the functions that don't need FontLab. Run them in the
# Terminal:  uv run --no-project --with pytest --with fontParts pytest -q
from fontParts.fontshell import RFont

import plain
import plum_report


def small_font():
    font = RFont(showInterface=False)
    font.info.familyName = "Test"
    font.info.styleName = "Regular"
    for name, code, width in [("n", 0x6E, 600), ("m", 0x6D, 900), ("space", 0x20, 250)]:
        glyph = font.newGlyph(name)
        glyph.unicode = code
        glyph.width = width
        if name != "space":
            pen = glyph.getPen()
            pen.moveTo((50, 0))
            pen.lineTo((width - 50, 0))
            pen.lineTo((width - 50, 500))
            pen.closePath()
    font.newGlyph("n.alt").width = 620
    font.kerning[("n", "m")] = -10
    return font


def test_key_ignores_capitals_and_punctuation():
    assert plain.key("Plum-SemiBold") == plain.key("plum semibold")


def test_key_keeps_digits():
    assert plain.key("Plum v1.004") == "plumv1004"


def test_summary_counts_glyphs_and_pairs():
    facts = plum_report.summary(small_font())
    assert facts["glyphs"] == 4
    assert facts["pairs"] == 1


def test_summary_lists_glyphs_without_a_character():
    facts = plum_report.summary(small_font())
    assert facts["without"] == ["n.alt"]


def test_summary_sorts_the_empty_glyphs():
    facts = plum_report.summary(small_font())
    assert facts["empty"] == ["n.alt", "space"]


def test_summary_finds_the_widest():
    facts = plum_report.summary(small_font())
    assert facts["widest"].name == "m"


def test_lines_for_an_empty_font():
    font = RFont(showInterface=False)
    font.info.familyName = "Test"
    font.info.styleName = "Regular"
    assert plum_report.lines(font) == [
        "Test Regular",
        "Glyphs            0",
        "No character      0",
        "Nothing drawn     0",
        "Kerning pairs     0",
    ]
```

Save it as `test_tools.py` in `spacing-tools`, beside the `plain` folder and `plum_report.py`.

`small_font` builds the font: `n` and `m` with a triangle drawn in each, a `space` with nothing drawn, an `n.alt` with no character and nothing drawn, and one kerning pair. The pen lines are chapter 46's. Every test that wants a font calls `small_font()` and gets a fresh one, so no test can spoil the font for the next.

Each test makes one claim, or two that belong together. When one fails, its name tells you what's wrong before you read any code.

Two tests are there because of things this book already got wrong once. `test_key_ignores_capitals_and_punctuation` pins down what Mira's tidying broke. `test_summary_sorts_the_empty_glyphs` pins down chapter 136's mistake, the order that differed between editors. A good time to write a test is right after a bug: you know what went wrong, and the test keeps it from coming back unnoticed.

## Run it

```text
uv run --no-project --with pytest --with fontParts pytest -q
```

Six dots and an F:

```text
......F                                                                  [100%]
    def test_lines_for_an_empty_font():
        font = RFont(showInterface=False)
        font.info.familyName = "Test"
        font.info.styleName = "Regular"
>       assert plum_report.lines(font) == [
            "Test Regular",
            "Glyphs            0",
            "No character      0",
            "Nothing drawn     0",
            "Kerning pairs     0",
        ]
E       AssertionError: assert ['Test Regula... pairs     0'] == ['Test Regula... pairs     0']
E
E         At index 3 diff: 'Nothing drawn     0  ' != 'Nothing drawn     0'

1 failed, 6 passed in 0.46s
```

I didn't plant that. I wrote the last test expecting it to pass, and it found a flaw in chapter 136's script that neither of us saw. Read the line that starts `At index 3`. When no glyph is empty, the report's fourth line ends in two spaces: the gap before a list of names that isn't there. Nobody sees two spaces at the end of a line in the Output panel, but a program reading the report would.

A dot is a test that passed, an `F` one that failed. For a failure pytest shows the test, marks the line with `>`, and on the `E` lines shows both sides of the `==` and where they part. That's more than a bare `assert` would tell you.

The fix is in `plum_report.py`, in `lines`. Replace the "Nothing drawn" line with these two:

```python
empty = f"Nothing drawn     {len(facts['empty'])}  {', '.join(facts['empty'])}"
out.append(empty.strip())
```

`strip` is chapter 27's. Keep the indentation of the line you replaced. Run pytest again:

```text
.......                                                                  [100%]
7 passed in 0.06s
```

It took six hundredths of a second. Send Tove the new file. And since you fixed the copy in `spacing-tools`, copy it over the `plum_report.py` that FontLab runs.

## Break it on purpose

Do what Mira did. In `plain/__init__.py`, change `text.lower()` to `text` and run pytest:

```text
>       assert plain.key("Plum-SemiBold") == plain.key("plum semibold")
E       AssertionError: assert 'PlumSemiBold' == 'plumsemibold'

>       assert plain.key("Plum v1.004") == "plumv1004"
E       AssertionError: assert 'Plumv1004' == 'plumv1004'

FAILED test_tools.py::test_key_ignores_capitals_and_punctuation - AssertionEr...
FAILED test_tools.py::test_key_keeps_digits - AssertionError: assert 'Plumv10...
2 failed, 5 passed in 0.07s
```

That's the bug from the top of the chapter, found in seven hundredths of a second where Friday took four days. The names of the two failed tests say what `key` no longer does. Put `.lower()` back and run it once more to see seven dots.

Now be clear about what the seven dots mean. They mean that seven claims about two files hold. They say nothing about `shift_tool`, about Undo, about the export, or about anything else that touches FontLab. Those are still checked the old way, by running them and looking. Tests cover the working-out, and they're one more reason to move as much of each script as you can into working-out.

## What you learned

`assert` states something that should be true and stops the script when it isn't. A test is a function of such claims, named for what it claims. pytest finds the files and functions that start with `test_`, runs them all, and shows where a failed claim parted from the truth. Only functions that can be imported without FontLab can be tested this way, so they live in a file of their own. A test needs data whose right answers you know, which means data you built. And passing tests are a statement about what they cover and nothing else.

## Try it yourself

1. Write `test_key_of_an_empty_string`. Decide what `key("")` should give before you run it.
2. Add a glyph to `small_font` that's wider than `m`. Run pytest and read which tests fail. Then decide for each whether the test or the font should change.
3. Find one more function in any script from Part 6 that takes plain values and returns plain values. Move it to `plain/__init__.py`, import it back into the script, and write two tests for it.

## Next

Oskar's holiday ends next week. In July he left a sheet with eleven lines on it and a folder called `chores`. The last chapter is his first morning back in the new year: what he finds, what's on the new list, and where you go from here.
