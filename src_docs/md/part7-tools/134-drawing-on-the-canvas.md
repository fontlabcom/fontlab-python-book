---
this_file: src_docs/md/part7-tools/134-drawing-on-the-canvas.md
---

# 134. Drawing on the canvas

It's Monday 4 January. Mira is back, the package went to Porto on Thursday, and she has spent the morning with the sidebearing panel from chapter 128 docked at the right. By eleven she has an opinion about it.

"It's correct," she says, "and it's in the wrong place. I'm looking at the `n`. The numbers are over there. Can't they sit under the glyph, where the space is?"

They can. This chapter puts two numbers and a line into the Glyph window, drawn by FontLab every time it draws the glyph. You won't open a window, connect a button or start a timer. You'll write one small class, put it in a folder with a particular name, and FontLab will find it and call it.

## What you need

`Plum-practice` open, Fly installed at version 1.3.0 or later, and the app package that came with it. You need chapter 126 for classes and chapter 128 for the word *callback*. No helpers from earlier chapters are used today.

I haven't run this chapter in FontLab 9. I loaded the finished folder with the same loader FontLab uses at start, and I called the class on hand-made glyph measurements in plain Python; the numbers below come from that. What I have not seen is the drawing itself: the line and the numbers appearing in a real Glyph window. The people who wrote the plugin system say the same about their own reporters, so treat the picture as the part to check first.

## Step 1: A class built on another class

Every class you have written so far started from nothing. A class can also start from another class and change only what differs:

```python
class Tool:
    title = "Tool"

    def describe(self):
        return f"{self.title} is ready."


class ShiftTool(Tool):
    title = "Shift"


print(Tool().describe())
print(ShiftTool().describe())
```

```text
Tool is ready.
Shift is ready.
```

Two things are new. The name in brackets after `ShiftTool` says "start with everything `Tool` has". `ShiftTool` has no `describe` of its own, so it uses `Tool`'s. And `title` sits in the class body, outside any method, with no `self.` in front: it belongs to the class, and every object made from the class sees it through `self.title`. `ShiftTool` replaces that one value, and `describe`, which it never wrote, picks up the new one.

In chapter 126's picture, a class was a wardrobe you built yourself. This is a wardrobe bought ready-made, where you swap one drawer.

That's how a plugin works. Somebody else wrote a class called `Reporter` that knows how to live in the Glyph window: how to be listed, switched on and off, and handed a glyph at the right moment. You build on it and supply the one thing it can't know, which is what to draw.

## Step 2: The function FontLab calls

A reporter has one method to write, `compute`. Here is the smallest reporter that draws anything:

```python
from fly.ap.plugins.reporter import Mark, Reporter


class Sidebearings(Reporter):
    name = "spacing_sidebearings"
    title = "Halfmoon Sidebearings"

    def compute(self, snapshot):
        return [Mark("text", ((0, 0),), text="here")]
```

`name` is how FontLab remembers the reporter and `title` is what it shows in its list. `compute` is a callback, like the timer's `on_tick` in chapter 128, with a different caller: FontLab calls it whenever it draws a glyph while the reporter is switched on. It hands over a `snapshot`, which is a set of measurements of the glyph taken a moment ago, and it expects a list of marks back.

A `Mark` is a note saying "draw this, here". The first value is the kind: `"text"`, `"line"`, and a few more. The second is a tuple of points in font units, the units of chapter 43, so `(0, 0)` is the glyph's origin on the baseline. A text mark has one point and so the tuple has one pair in it, which is why there's a comma before the closing bracket. After those come the colour and, by name, the text.

Notice what `compute` doesn't do. It doesn't draw. It returns a list, and FontLab draws what's on it. That split is the same one you made in chapter 123, when `plan_rows` worked out the numbers and something else used them, and it pays in the same way: a method that only returns a list can be called in plain Python, with no window anywhere, to see what it would draw.

`Mark` is an ordinary Python class, so naming a value, as in `text="here"`, is fine. The rule against names inside brackets from chapter 121 was about Qt's own widgets.

## Step 3: Read the snapshot

The snapshot carries what you need. `snapshot.advance` is the glyph's width. `snapshot.bounds`, when the reporter asks for it, is the box around the outline as four numbers: left, bottom, right, top. `snapshot.metrics` holds the font's vertical measures, with `ascender` and `descender` among them.

From chapter 61, the left sidebearing is the distance from zero to the left edge of the outline, and the right sidebearing is the distance from the right edge to the width. So one small function is enough:

```python
def edges(snapshot):
    if snapshot.bounds is not None:
        left, bottom, right, top = snapshot.bounds
        return left, right
    xs = []
    for contour in snapshot.contours:
        for node in contour.nodes:
            if node.on_curve:
                xs.append(node.x)
    if not xs:
        return None
    return min(xs), max(xs)
```

It has three ways out. If the box is there, it gives the box's two sides. If not, it collects the x of every on-curve node and gives the least and the greatest; that's a fair second best, a little off for a round glyph whose curve bulges past its nodes. If there are no nodes at all, the glyph is empty and it gives `None`. Whoever calls it has one thing to check.

The box is only there if you ask. A reporter asks with one more line in the class body, `needs_bounds = True`. FontLab doesn't measure what no reporter wants, because all of this happens while it draws, many times a second when you drag a node.

That's the rule for a callback of this kind: be quick, and change nothing. `compute` gets measurements, not the glyph, so it couldn't change the font if it tried. Keep it that way in spirit too. Don't open files in it, don't print in it, and don't loop over the font.

## Step 4: Leave out `self`

Here is the mistake to make once. You write `compute` the way you'd write a loose function:

```python
from fly.ap.plugins.reporter import Mark, Reporter


class Sidebearings(Reporter):
    name = "spacing_sidebearings"
    title = "Halfmoon Sidebearings"

    def compute(snapshot):
        return [Mark("text", ((0, 0),), text="here")]
```

Called by hand, it says:

```text
TypeError: Sidebearings.compute() takes 1 positional argument but 2 were given
```

You gave one value and Python counts two, because the object itself always arrives first. Chapter 126 met this error from the other side. Put `self` back.

In FontLab you wouldn't see a traceback in your face. `Reporter` wraps every call to `compute` in a `try`, for the reason your slots have caught their own errors since chapter 122: an error that escapes while a window is being drawn can take more than your plugin down with it. The reporter draws nothing and reports the error once, not once for every redraw. So when a reporter is switched on and the canvas stays bare, the first thing to do is call `compute` yourself, in plain Python, and read what it says.

## Step 5: A folder FontLab finds

A reporter isn't run from the Scripts menu. It lives in a folder, called a bundle, inside FontLab's user data folder, the one chapter 129 wrote the settings file into:

```text
Extensions/
    reporters/
        Sidebearings.fontlabReporter/
            plugin.json
            sidebearings.py
```

The folder's name ends in `.fontlabReporter` and sits in `reporters`; both say what kind of plugin this is. `sidebearings.py` holds the class. `plugin.json` is a JSON file, the format from chapter 99, that introduces it:

```json
{
  "id": "spacing_sidebearings",
  "name": "Halfmoon Sidebearings",
  "kind": "reporter",
  "version": "1.0.0",
  "entry": "sidebearings:Sidebearings",
  "min_app_version": "1.0.0"
}
```

`entry` is the file's name without `.py`, a colon, and the class's name. `id` must equal the class's `name`, and `name` must equal its `title`. Saying the same thing in two places looks wasteful, and it's there on purpose: FontLab can read the JSON and list the plugin without running any of your Python, and when it does run it, a mismatch tells it the two files have drifted apart.

FontLab looks for bundles when it starts. Make the folders, save the two files, and restart.

## The whole script

Save this as `sidebearings.py` in the bundle folder:

```python
# Shows a glyph's sidebearings in the Glyph window. Changes nothing.
from fly.ap.plugins.reporter import Mark, Reporter

BLUE = (80, 145, 190)
GAP = 7


def edges(snapshot):
    if snapshot.bounds is not None:
        left, bottom, right, top = snapshot.bounds
        return left, right
    xs = []
    for contour in snapshot.contours:
        for node in contour.nodes:
            if node.on_curve:
                xs.append(node.x)
    if not xs:
        return None
    return min(xs), max(xs)


class Sidebearings(Reporter):
    name = "spacing_sidebearings"
    title = "Halfmoon Sidebearings"
    layer = "background"
    needs_bounds = True

    def compute(self, snapshot):
        found = edges(snapshot)
        if found is None:
            return []
        left, right = found
        low = snapshot.metrics.descender
        high = snapshot.metrics.ascender
        width = snapshot.advance
        return [
            Mark("line", ((width, low), (width, high)), BLUE),
            Mark("text", ((0, low),), BLUE, text=f"{left:g}"),
            Mark("text", ((width + GAP, low),), BLUE, text=f"{width - right:g}"),
        ]
```

There's no `#FLM` line, because this file never appears in the Scripts menu.

The class body has four lines of facts before any method. `layer = "background"` asks for the marks to go behind the outline, so they don't cover the nodes Mira is dragging. `needs_bounds = True` is the request from step 3.

`compute` asks `edges` for the two sides and returns an empty list for an empty glyph: nothing to say, nothing drawn. Otherwise it makes three marks. The line stands at the glyph's width and runs from the font's descender to its ascender. The left number sits at zero and the right number a little past the line, both at the descender, which puts them under the glyph in the space they describe. `GAP` keeps the right number from touching the line.

The right sidebearing is `width - right`. The `:g` in the two f-strings, which you used in chapter 107, prints 70.0 as `70` and leaves 50.5 alone.

## Run it

You can check the class before FontLab ever sees it. With a snapshot for an `n` as Plum ships it in the Regular, where the width is 523 and the outline runs from 70 to 457, `compute` returns three marks:

```text
line   at x 523, descender to ascender
text   "70"  at x 0
text   "66"  at x 530
```

Left 70, width 523, right 66. If you kept the shift from chapter 123, your own `n` is ten wider on each side, and your numbers will be 80 and 76. For the shipped `o`, both texts say `38`. For `space`, which has no outline, the list is empty.

Then restart FontLab, open the `n` in a Glyph window, and choose **View > Reporters**. Halfmoon Sidebearings should be in the list. Switch it on. What I expect, and haven't seen, is a blue line at the right edge of the glyph's width and two blue numbers under the glyph. Drag the whole outline ten units to the right and, as you let go, the left number should go up by ten and the right one down by ten. Then choose **Edit > Undo**. Nobody clicked anything, and no timer is running: FontLab drew the glyph again, so it called `compute` again.

Mira switches it on and closes the docked panel.

## Break it on purpose

Open `plugin.json` and change `"name"` to `"Sidebearings"`. Restart. The reporter isn't in the list. The loader refused the bundle:

```text
ValueError: manifest id/name/kind must match the entry class
```

It refused before running any drawing code, and it went on to load everything else. A bundle with a mistake in it is skipped and logged, and the others load. Put the name back.

Now, in `sidebearings.py`, delete the two lines in `compute` that test `found is None`. Call `compute` with an empty glyph:

```text
TypeError: cannot unpack non-iterable NoneType object
```

`edges` gave `None` and the next line tried to split it into two names. In the Glyph window this would be the quiet failure from step 4: nothing drawn for `space`, one report, and every other glyph fine. A plugin is called for every glyph the user opens, including the ones you didn't think of. Put the test back.

## What you learned

A class can be built on another class, keeping all of it and replacing a value or a method. A plugin is such a class in a folder FontLab searches at start, with a small JSON file that introduces it. Its one method is a callback that FontLab calls on every draw, so it must be quick, change nothing, and return a list of marks for FontLab to draw. And because it only returns a list, you can call it in plain Python and read the answer before you trust it on the canvas.

## Try it yourself

1. Add a fourth mark: the width, as text, at the top of the line. Use `snapshot.metrics.ascender` for the height.
2. Mira wants a warning when the two sides of a round glyph differ. Give the two numbers a red colour, `(220, 50, 45)`, when they differ by more than 4, and keep them blue otherwise. Check with the `o`, and then with a made-up snapshot where they differ by 10.
3. Make a second bundle, with its own folder, id and class, that draws one line at half the glyph's width. Work out which of the six values in `plugin.json` must change, and which may stay.

## Next

On Tuesday a friend of Mira's sends her a script that finds glyphs with stray single points. It was written for another font editor, and its first line imports a module FontLab doesn't have. Chapter 135 reads a script from somewhere else, and finds out how much of it runs here.
