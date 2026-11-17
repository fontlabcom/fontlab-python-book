---
this_file: src_docs/md/part7-tools/128-keep-up-with-the-font.md
---

# 128. Keep up with the font

Thursday, late in the afternoon. The Sidebearings panel sits at the right edge of FontLab and Ines has stopped losing it. She presses the key for the next glyph, the Glyph window shows `o`, and the panel still says `n in Light`. She clicks **Look again**. Next glyph, click. Next glyph, click. By the sixth glyph she has a name for the button, and it isn't printable.

A panel that shows the wrong glyph is worse than no panel, because sooner or later somebody believes it. Today the button goes. The panel will go and look for itself, often enough that nobody can catch it out, and it will hold its tongue when there's nothing new to say.

## What you need

`Plum-practice` open with the Light showing, a Glyph window on `n`, Fly installed, and `sidebearing_panel.py` from chapter 127. The panel reads and changes nothing.

I haven't run this chapter in FontLab 9. I ran the script against stand-in widgets and a stand-in timer that I could make tick as many times as I liked. The script follows an example in FontLab's collection of Python examples, `live_glyph_panel.py`, which watches the current glyph the same way.

## Step 1: Be told, or go and look

There are two ways to keep up with something that changes.

The first is to be told. That's what a button does. In chapter 122 you handed the button a function, `on_again`, and the button called it at each click. A function you hand over so that somebody else can call it later has a name: a *callback*. Every slot is one. So is `build`, which `create_panel` calls when the panel's inside is ready. You don't call a callback. You leave it at the desk and get on with your day.

So the tidy answer would be a signal that says "the user moved to another glyph", with a slot of yours connected to it. I looked for one and didn't find one I could check. FontLab does send signals when a glyph is edited, and none that I could verify for the moment somebody steps from `n` to `o`.

That leaves the second way: go and look. Ask "which glyph is it now?" again and again, and act when the answer changes. It sounds crude. It's how a great many working tools keep up, and at the pace of a person pressing keys it costs next to nothing, as you'll measure in step 4.

Going to look still needs somebody to say *when*. A script can't loop and wait, because while your loop runs, nothing else in FontLab can. What you need is something that calls you back at a steady beat.

## Step 2: A timer

Qt has that something, and it's a small object called a timer. Add these lines at the end of the panel's `__init__`, and add `core` beside `gui` at the top of the script, as in chapter 121:

```python
self.timer = core.QTimer(content)
self.timer.setInterval(200)
self.timer.timeout.connect(self.on_again)
```

`QTimer(content)` makes a timer that belongs to the panel's inside, so when the panel goes, the timer goes with it. `setInterval` takes thousandths of a second, so 200 is a fifth of a second. `timeout` is the timer's signal, the way `clicked` is a button's, and you connect a slot to it in the same way: the function's name, no brackets.

Run the script. Step to `o`. The panel says `n in Light`.

Nothing is wrong with those three lines. One is missing. A timer that has been made and set is a clock with the pendulum held still. It needs a push:

```python
self.timer.start()
```

Put that under the `connect` line and run the script again. Step to `o`, and the panel follows before you've looked across at it. Step to `H`, and it follows again. The button is still there, and nobody needs it.

A made timer is not a running timer. When a live tool sits there doing nothing and shows no error, look for the `start`.

## Step 3: Say nothing when nothing changed

The panel now writes its label five times a second, and almost every time it writes the text that was already there. In a minute that's 300 writes to say `n in Light` once.

Does it matter? For four short lines, you may never see the cost. For a tool that fills a list of 274 names, you would: the list would be rebuilt five times a second, and your place in it lost each time. The habit worth having is the one a good colleague has. Look as often as you like. Speak when you have news.

To know whether there's news, the panel must remember what it said last. That's a value that has to live between one tick and the next, which is the thing a drawer on `self` is for:

```python
def on_tick(self, *args):
    text = self.look()
    if text == self.shown:
        return
    self.shown = text
    self.label.setText(text)
```

`self.shown` starts as `None` in `__init__`. The text for a glyph is never `None`, so the first tick always has news. After that, a tick that finds the same text leaves by the early `return` and touches nothing on screen.

Look at what counts as news. The comparison is on the whole text, so anything that changes any of the four lines is news: another glyph, another master, or a sidebearing that somebody has dragged. You didn't write a rule for each. You compared what you'd say with what you said.

`self.look()` is chapter 127's `refresh` with one change. It gives the text back, and leaves the writing to `on_tick`. It still catches whatever goes wrong and turns it into text. An error in a slot that runs at a click is one error. An error in a slot that runs five times a second is 300 a minute, and because an error message is also text, the comparison deals with that too: the panel writes it once and waits.

## Step 4: Count the looks

"It costs next to nothing" is a claim, and you have a panel to check it with. Give the object two more drawers, `looks` and `writes`, both starting at 0. Add one to `looks` at the top of every tick, add one to `writes` when there's news, and show both in a second, smaller label:

```python
self.small.setText(f"Looks {self.looks}, writes {self.writes}")
```

That line goes after the early `return`, with the other write. If it sat above the `return` it would change the screen at every tick, and you'd have put back the chatter you took out.

So the line of counts only moves when the glyph text does. Between moves it shows the count as it stood at the last piece of news. That's the point of it: a big jump in `looks` beside a step of one in `writes` is the picture of a panel that looked a lot and said little.

## The whole script

The button and its slot are gone. Save this as `live_panel.py`:

```python
#FLM: Live Sidebearings
# A panel at the side of FontLab that shows the sidebearings of the
# current glyph and keeps up as you move about. Changes nothing.
import sys

import fly.ap.core.scripting as scripting
from fly import ap, fl, qt
from fly.tr.proxy.fl.objects.glyph import pGlyph

core, gui = qt.QtCore, qt.QtGui
KEY = "tools.sidebearings"
TITLE = "Sidebearings"
EVERY = 200


def keep(key, things):
    kept = vars(sys).setdefault("kept_windows", {})
    if key in kept:
        kept[key][0].close()
    kept[key] = things


def glyph_text():
    font = fl.CurrentFont()
    glyph = fl.CurrentGlyph()
    if font is None or glyph is None:
        return "No glyph is showing."
    master = scripting.current_package().master
    rich = pGlyph(font, glyph)
    lines = [
        f"{rich.name} in {master}",
        f"Left {rich.getLSB(master)}",
        f"Width {rich.getAdvance(master)}",
        f"Right {rich.getRSB(master)}",
    ]
    return "\n".join(lines)


class LivePanel:
    def __init__(self, content):
        self.shown = None
        self.looks = 0
        self.writes = 0
        self.label = gui.QLabel("", content)
        self.small = gui.QLabel("", content)
        layout = gui.QVBoxLayout(content)
        layout.addWidget(self.label)
        layout.addWidget(self.small)
        self.timer = core.QTimer(content)
        self.timer.setInterval(EVERY)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start()
        self.on_tick()

    def look(self):
        try:
            return glyph_text()
        except Exception as problem:
            return f"Didn't work.\n{type(problem).__name__}: {problem}"

    def on_tick(self, *args):
        self.looks += 1
        text = self.look()
        if text == self.shown:
            return
        self.shown = text
        self.writes += 1
        self.label.setText(text)
        self.small.setText(f"Looks {self.looks}, writes {self.writes}")


def main():
    made = []

    def build(content):
        made.append(LivePanel(content))

    owner = ap.FontLab().create_panel(TITLE, build, area="right")
    keep(KEY, [owner, made[0]])


main()
```

`keep`, `glyph_text` and `main` are chapter 127's, word for word, apart from the class name. The key is the same too, `tools.sidebearings`, and that's on purpose: `keep` finds the shelf that chapter 127's script made in `sys`, closes the panel with the button, if it's still open, and puts this one in its place.

`EVERY` is a name for the 200. A number that decides how a tool feels belongs at the top, where you'll find it when you want to change the feel.

The last line of `__init__` calls `self.on_tick()` once by hand. Without it the panel would be empty for its first fifth of a second. A slot is a plain method, and you can call it yourself when that's useful.

## Run it

With `n` in the Glyph window and the Light showing, the panel opens with:

```text
n in Light
Left 84
Width 499
Right 80
Looks 1, writes 1
```

Wait about five seconds, then step to `o`:

```text
o in Light
Left 50
Width 494
Right 50
Looks 27, writes 2
```

Your count of looks will be whatever your five seconds came to. Mine was 27: one look when the panel opened, 25 that found nothing new, and the one that found `o`. Wait again and go to `H`:

```text
H in Light
Left 88
Width 612
Right 84
Looks 52, writes 3
```

Now drag the left sidebearing of `H` a little way in the Glyph window. The numbers in the panel should follow the drag, a fifth of a second behind at most, and `writes` should climb with them. Use **Edit > Undo** to put the `H` back, and the panel should follow that too. Nobody wrote code for "a sidebearing was dragged" or for "Undo". The text changed, and the panel saw that it had.

Run the script a second time. The first panel closes and a second opens, with its counts back at 1. The first panel's timer went when its panel went, because you made it with `QTimer(content)`. I haven't seen that happen in FontLab; in the stand-in, a closed panel's timer never ticks again. A panel's own cross may only hide it, and then its timer goes on ticking out of sight until you run the script again.

## Break it on purpose

Take the news test out. Delete these two lines from `on_tick`:

```python
if text == self.shown:
    return
```

Run the script, leave `n` showing, and wait about a minute. You'll see something near this:

```text
Looks 300, writes 300
```

The label of counts is now busy all the time, and the panel has written `n in Light` some 300 times to an audience of one. Nothing looks broken. This kind of waste doesn't announce itself, which is the reason the counts are there. Put the two lines back.

Then make the panel lazy. Change the line at the top to `EVERY = 5000` and run the script. Step from `n` to `o`. For up to five seconds the panel says `n in Light` above a glyph that is plainly an `o`, and it's chapter 127's panel again without even a button to press. Put 200 back.

## What you learned

A callback is a function you hand over for somebody else to call, and a timer calls yours at a steady beat once you've started it. When there's no signal for the change you care about, you can look for the change yourself, often. A live tool should remember what it last showed and write only when that differs. A slot that runs many times a second must never let an error out, and should count its own work so that you can see what it costs.

## Try it yourself

1. Add a tick box, **Follow**, that starts ticked. Connect its `clicked` signal to a slot that reads the box with chapter 123's `read` and calls `self.timer.start()` or `self.timer.stop()`. Untick it, step to another glyph, and watch the panel hold still.
2. Add a line to the glyph text that gives the time of the last write, with `datetime.now()` from chapter 119. Put it in `on_tick`, where the write happens. Then work out what would go wrong if you put it in `glyph_text` instead.
3. At one look every 200 thousandths of a second, how many looks is an eight-hour day? Work it out in the Scripting panel. Then try `EVERY = 1000`, use the panel for a few minutes, and decide which you'd give Ines.

## Next

The panel keeps up, and Ines has gone back to the Shift tool to open up the Light. Every time she opens it, the Left box says 0, and every time she types 12 into it. Chapter 129 gives a tool a memory that outlasts FontLab itself: a small file of settings, read when the tool opens and written when she clicks.
