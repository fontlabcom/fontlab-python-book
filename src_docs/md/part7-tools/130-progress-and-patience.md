---
this_file: src_docs/md/part7-tools/130-progress-and-patience.md
---

# 130. Progress and patience

Monday afternoon, 28 December. Ines emptied the names field, selected every glyph in the Font window, and clicked **Shift**. The button stayed pressed in. The window wouldn't move. She clicked again, and a third time, and then sat with her hands in her lap for most of a minute, wondering whether to force FontLab to quit and lose the morning's work. Then the label filled in, three times over.

Nothing had gone wrong. The tool was busy, and a busy tool that says nothing looks the same as a dead one. Today's script does a long job the polite way: it shows how far it has got, it lets you stop it, and FontLab stays awake the whole time.

## What you need

`Plum-practice` open, Fly installed, `halfmoon.py`. The script only measures. It changes nothing in the font, so you can run it, stop it and break it as often as you like.

I haven't run this chapter in FontLab 9. The whole script ran against stand-in widgets, a stand-in timer that I ticked by hand, and a stand-in font with the 274 glyph names yours should have by now. The slice counts below come from that run. How long anything takes, and what a frozen window looks like on your machine, I haven't seen.

## Step 1: Why the window froze

Chapter 121 described the event loop: FontLab goes round and round, and on each turn it repaints what needs repainting, notices clicks, and calls the slots that are owed a call. The loop does one thing at a time. While it's inside your slot, it isn't repainting and it isn't noticing clicks. It gets back to that work when your slot returns.

A slot that takes a hundredth of a second is invisible. A slot that walks 274 glyphs in three masters and measures each one is 822 pieces of work in a single turn of the loop, and for as long as that takes, FontLab can't draw so much as a pressed button popping back up. Ines's second and third clicks weren't lost, either. They waited in a queue, and the loop delivered them when it came round again, which is why the job ran three times.

So the cure isn't to work faster. It's to return sooner.

## Step 2: A bar, and the mistake

Qt has a window made for this, `QProgressDialog`: a line of text, a bar, and a Cancel button. You give it the text, the button's word, the two ends of the bar, and a parent:

```python
dialog = gui.QProgressDialog("Measuring...", "Cancel", 0, len(jobs), parent)
```

`dialog.setValue(n)` moves the bar to `n`. The obvious thing to do with that is this:

```python
def on_go(*args):
    rows = []
    for name, master in jobs:
        rows.append(measure(font, name, master))
        dialog.setValue(len(rows))
```

It reads well and it does nothing useful. `setValue` changes a number inside the dialog and asks for a repaint, and the repaint happens on the next turn of the loop. There is no next turn until `on_go` returns. The bar is told 822 things and gets to show the last of them, when it's all over. Cancel is as dead as every other button. This is the mistake nearly everybody makes with their first progress bar, and it's worth making once on purpose to see it.

Some people get out of it by calling a Qt function in the middle of the loop that forces a turn of the event loop from inside the slot. I'm not going to teach that. It lets a second click start a second job in the middle of the first, and the tools this book learned from don't do it.

## Step 3: Slices

What works is to cut the job into slices and do one slice per turn of the loop. Chapter 128 gave you the machinery: a timer calls a method, the method does a little and returns. There, the timer fired five times a second. Here its interval is zero, which doesn't mean "never" or "all at once". It means "as soon as the loop has nothing else to do". Repainting and clicks come first, and your slice gets every turn that's left.

The job has to remember where it was between slices, and that's what a class is for. The rows measured so far are the bookmark:

```python
def on_tick(self, *args):
    start = len(self.rows)
    for name, master in self.jobs[start:start + SLICE]:
        self.rows.append(measure(self.font, name, master))
    self.dialog.setValue(len(self.rows))
```

You've cut the front off a list before, with `names[:SHOWN]`. A slice with a number on each side of the colon takes the middle: `jobs[25:50]` is the items numbered 25 up to, but not including, 50. Near the end, `jobs[800:825]` asks for more than the list has and gets the 22 that are left, without complaint. That saves a line of arithmetic.

`SLICE` is 25. Too small, and the job spends its time going round the loop. Too large, and each turn takes long enough that the window stutters. Twenty-five glyph layers is a guess that's kind to a slow machine, and it's a name at the top of the script so that you can change it.

## Step 4: Stop, and stop once

Three things can end the job: it runs out of work, the person clicks **Cancel**, or something raises an error. All three want the same handful of actions, so there's one method for them:

```python
def finish(self, text):
    self.over = True
    self.timer.stop()
    self.dialog.setLabelText(text)
    self.dialog.setCancelButtonText("Close")
    print(text)
```

`self.timer.stop()` is the line that matters most, and Break it shows why. The button changes its word because, once the job is over, there's nothing left to cancel. But it's still the same button, and it still sends the same signal, `canceled`. (Qt spells it with one l.) So the slot for that signal has to know whether the job is already over:

```python
def on_cancel(self, *args):
    if not self.over:
        self.finish(f"Stopped. {len(self.rows)} of {len(self.jobs)} layers measured.")
    core.QTimer.singleShot(0, self.dialog.close)
```

I left `self.over` out of my first version. The job ran to the end and said "Done", I clicked **Close**, and the Output panel got a second line: "Stopped. 822 of 822 layers measured." A tool that tells you it stopped a job it finished isn't one you'd trust with a font.

The last line is there because of what Qt does with this button. As far as I know from Qt's own documents, a click on it hides the dialog at once, whatever the button says. A hidden window isn't a closed one: it's still there, out of sight, and so is its timer. So the slot closes it properly. `QTimer.singleShot(0, ...)` means "call this once, the next time the loop comes round", which is a polite way to close a window from inside one of its own signals. It also means the sentence in the label is on show while the job runs and after `Done`, but a `Stopped` sentence is only ever read in the Output panel, where `finish` prints it.

Cancelling doesn't throw anything away. The rows measured before the click are still in `self.rows`, and for a job that only reads, half an answer is a fine thing to be left with.

## The whole script

```python
#FLM: Long Job
# Measures every glyph in every master, a slice at a time, behind a
# progress window with a Cancel button. Changes nothing.
import halfmoon
import fly.ap.core.scripting as scripting
from fly import fl, qt

core, gui = qt.QtCore, qt.QtGui
KEY = "halfmoon.longjob"
SLICE = 25
SHOWN = 6


def measure(font, name, master):
    rich = halfmoon.rich(font, font[name])
    return (name, master, rich.getLSB(master), rich.getAdvance(master), rich.getRSB(master))


class LongJob:
    def __init__(self, parent, font, jobs):
        self.font = font
        self.jobs = jobs
        self.rows = []
        self.looks = 0
        self.over = False
        self.dialog = gui.QProgressDialog("Measuring...", "Cancel", 0, len(jobs), parent)
        self.dialog.setWindowTitle("Long Job")
        self.dialog.setMinimumDuration(0)
        self.dialog.setAutoReset(False)
        self.dialog.setAutoClose(False)
        self.dialog.setAttribute(core.Qt.WA_DeleteOnClose)
        self.dialog.canceled.connect(self.on_cancel)
        self.timer = core.QTimer(self.dialog)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(0)

    def finish(self, text):
        self.over = True
        self.timer.stop()
        self.dialog.setLabelText(text)
        self.dialog.setCancelButtonText("Close")
        print(text)
        for row in self.rows[:SHOWN]:
            print(row)

    def on_tick(self, *args):
        self.looks += 1
        try:
            start = len(self.rows)
            for name, master in self.jobs[start:start + SLICE]:
                self.rows.append(measure(self.font, name, master))
            self.dialog.setValue(len(self.rows))
            if len(self.rows) == len(self.jobs):
                self.finish(f"Done. {len(self.rows)} layers measured in {self.looks} slices.")
        except Exception as problem:
            self.finish(f"Didn't work.\n{type(problem).__name__}: {problem}")

    def on_cancel(self, *args):
        if not self.over:
            self.finish(f"Stopped. {len(self.rows)} of {len(self.jobs)} layers measured.")
        core.QTimer.singleShot(0, self.dialog.close)


def main():
    font = fl.CurrentFont()
    if font is None:
        halfmoon.tell("Open a font first.")
        return
    masters = scripting.current_package().masters
    jobs = []
    for glyph in font.glyphs:
        for master in masters:
            jobs.append((glyph.name, master))

    def build(parent):
        job = LongJob(parent, font, jobs)
        return job.dialog

    scripting.show_script_dialog(build, KEY)


main()
```

Save it as `long_job.py`.

`main` makes the list of jobs before any window opens: one pair, a glyph name and a master name, for every glyph in every master. That's the cheap part, a list of 822 pairs of words. `measure` is the expensive part, and it's the same three calls the Sidebearings panel made in chapter 127.

Three lines set the dialog up, and each one switches off something a `QProgressDialog` would otherwise do by itself. `setMinimumDuration(0)` shows it at once (left alone, it waits four seconds to see whether the job is worth a window). `setAutoReset(False)` and `setAutoClose(False)` keep it from emptying its bar and vanishing the moment the bar is full, which would hide the word "Done" before anybody read it.

The timer is made with the dialog as its parent, so when the dialog goes, the timer goes with it. And `build` hands back `job.dialog` and lets go of `job`, as chapter 126's `build` did: the dialog and the timer hold `self.on_cancel` and `self.on_tick`, and those methods hold the job.

## Run it

Run the script with `Plum-practice` open. A small window appears with a bar that fills from left to right, and while it fills you can drag the window about. When it's full, the label and the Output panel say this, with my stand-in's numbers in the rows:

```text
Done. 822 layers measured in 33 slices.
('.notdef', 'Light', 0, 500, 0)
('.notdef', 'Regular', 0, 500, 0)
('.notdef', 'Bold', 0, 500, 0)
('A', 'Light', 22, 554, 22)
('A', 'Regular', 13, 596, 11)
('A', 'Bold', 3, 596, -33)
```

Thirty-three slices: 32 of 25, and one of the 22 that were left. The six rows are the first of the 822, there to show that the job did measure something. Click **Close**, and the window goes.

Run it again, and this time click **Cancel** while the bar is under way. The window goes, and the Output panel says where the job had got to. I stopped my stand-in after 14 slices:

```text
Stopped. 350 of 822 layers measured.
```

followed by the same six rows. Your number will be whatever the bar had reached, and always a multiple of 25: Cancel is a click, a click waits for the loop, and the loop comes round between slices, never in the middle of one. If the bar is full before you can reach the button, your machine is quick. Set `SLICE = 1` and try again.

One more thing, for tools that change the font. Don't put a commit in each slice, or one job would leave 33 steps in **Edit > Undo**. Do the slow part in slices, the measuring and planning, and make the change in one commit at the end. Chapter 131 does this to the Shift tool.

## Break it on purpose

Delete `self.timer.stop()` from `finish` and run the script. The bar fills and the label says "Done", and it all looks right. Then look at the Output panel:

```text
Done. 822 layers measured in 34 slices.
Done. 822 layers measured in 35 slices.
Done. 822 layers measured in 36 slices.
```

and on and on, each with its six rows, as fast as FontLab can print them. The timer is still firing. Every tick finds an empty slice, sees that the rows are all there, and finishes again. A zero-interval timer that nobody stops is a job that never ends. Click **Close** to kill it (closing the dialog takes its child, the timer, with it), and put the line back.

Now set `SLICE = 822` and run it:

```text
Done. 822 layers measured in 1 slices.
```

One slice, one turn of the loop, and the bar never shows a middle. That's Ines's freeze, with a progress window that had no chance to appear. The machinery is all there, and it's the size of the slice that makes it work. Set `SLICE` back to 25.

## What you learned

FontLab's event loop does one thing at a time, so a slot that doesn't return leaves the whole program unable to repaint or to notice a click. A long job stays polite by doing a slice of its work each time a zero-interval timer fires, and keeping its place in an object between slices. A `QProgressDialog` shows the bar and sends `canceled` when its button is clicked, and one `finish` method, guarded so that it runs once, serves for done, stopped and failed alike. A tool that changes the font plans in slices and commits once.

## Try it yourself

1. Make the label say how far the job has got, as in `Measuring... 350 of 822`, by calling `setLabelText` in `on_tick`. Then change it to say which glyph is being measured. Which of the two would you rather watch?
2. After a Cancel the window is gone, and the sentence about where the job stopped is in a panel Ines may not have open. Use `halfmoon.tell` to say it in a message box as well. Where does the call go so that it appears once, and only after a Cancel?
3. Give `finish` one more line of output: how many of the measured rows have a negative number on either side. Use the bracketed list from chapter 37 with an `if`.

## Next

Ines can see that a long job is alive, and she can stop it. That leaves her three clicks, which shifted every glyph in the Light three times. Chapter 131 makes the Shift tool one that deserves to be clicked by somebody who doesn't read scripts: one click, one Undo, a button that can't be pressed twice, and messages that say what to do.
