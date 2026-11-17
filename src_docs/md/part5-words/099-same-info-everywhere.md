---
this_file: src_docs/md/part5-words/099-same-info-everywhere.md
---

# 99. The same info in every font

Thursday of week nineteen. Oskar opens the studio's oldest family, Quince, which was delivered years ago as six separate font files. He reads the six copyright lines aloud. Two say 2019 and four say 2020. One spells the studio "Half Moon". One has a full stop at the end and five don't. The designer is "O. Lindqvist" in three files and "Oskar Lindqvist" in the others.

"Nobody decided any of that," he says. "Somebody typed it six times."

Plum's three weights live in one font, so they share one family name and one copyright line. As soon as a family is several files, each file has its own Font Info, and typing a thing six times produces six spellings. The cure is to type it once, in a file that belongs to no font, and have a script compare every open font with it.

That file is today's new thing. Until now a script's settings sat at its top, in capitals, and changing them meant editing the script. A settings file keeps the values outside the code.

## What you need

- `Plum-practice` open in FontLab 9, with Fly installed.
- `halfmoon.py`.
- A second font to compare. Close FontLab's font, copy `Plum-practice.vfj` in your file manager, name the copy `Plum-practice-copy.vfj`, and open both. In the copy, open **File > Font Info**, change the designer to `S. Sagano` and empty the copyright line. Now you have a family of two that disagrees.

I couldn't run the code in FontLab 9. I ran the script in plain Python with two stand-in fonts and a real settings file, including the broken files below. The way it lists the open fonts is copied from Fly's own tools. One limit shapes the whole chapter: Fly's writer refuses to write into any font except the current one, so the script reports on all open fonts and changes one.

## Step 1: Write the settings file

JSON is a text format for the kind of data you keep in dictionaries and lists. Python reads and writes it with the `json` module. Let the script write the first file from the good font, so you don't have to type it. Click the window of `Plum-practice`, the font with the right values, and run:

```python
import json
from pathlib import Path

import fly.ap.core.scripting as scripting

package = scripting.current_package()
info = package.info
settings = {
    "familyName": info.familyName,
    "openTypeNameDesigner": info.openTypeNameDesigner,
    "copyright": info.copyright,
}
path = Path(package.path).parent / "family-info.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=4, ensure_ascii=False)
print(path)
```

`json.dump` takes the data and an open file. `indent=4` puts each entry on its own line, and `ensure_ascii=False` keeps a letter like é as itself. Open `family-info.json` in a text editor:

```text
{
    "familyName": "GG Plum",
    "openTypeNameDesigner": "Sora Sagano",
    "copyright": "GG Plum by Sora Sagano. Released under CC0 1.0 Universal: no rights reserved. Practice copy for the Halfmoon book."
}
```

It looks like a Python dictionary, and that resemblance is a trap you'll walk into in step 3. Ines can open this file and correct a name without ever seeing a line of code.

## Step 2: Read it back

```python
with open(path, encoding="utf-8") as f:
    settings = json.load(f)
print(settings["openTypeNameDesigner"])
print(len(settings))
```

```text
Sora Sagano
3
```

`json.load` gives back a dictionary, the same one you dumped. The keys are the attribute names from chapter 95, so `getattr(package.info, key)` can read the matching field for each. The settings file has become the table.

## Step 3: The mistake

Mira adds a line to the file by hand, for the version name, changes her mind and deletes it. She leaves the comma on the line above, after the copyright text. In a Python dictionary a comma after the last entry is allowed. She runs the reading code:

```text
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 5 column 1 (char 209)
```

JSON is stricter than Python. No comma after the last entry. Double quotation marks only, never single ones. No comments. The message is the reader's view of the mistake: after a comma it expected another name in quotes, and at line 5 it found the closing brace. Your Python may word it differently, and the line number will be there either way. Look at that line and the one before it.

A settings file is edited by people, in a hurry, without a traceback to guide them. So the script must expect the file to be wrong and say so in a sentence. `JSONDecodeError` is a kind of `ValueError`, which you've caught since chapter 19.

## Step 4: Trust nothing from outside

Even a file that parses can be wrong. Somebody could misspell a key, or add `"versionMajor": 2` because it seemed handy, and a script that passes every key to the writer would do what the file says. Decide what the file may contain, and check at the door:

```python
ALLOWED = {"familyName", "openTypeNameDesigner", "copyright"}


def read_settings(path):
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
    for key, value in settings.items():
        if key not in ALLOWED:
            raise ValueError(f"{key} is not a field this script may set")
        if not isinstance(value, str):
            raise ValueError(f"{key} must be text in quotation marks")
    return settings
```

`isinstance(value, str)` asks whether a value is a string. In JSON, `2026` without quotes is a number, and a number in the family name would be refused later by the writer with a message about some other tool. Better to refuse here, with the key's name. The `raise` lines are yours, as in chapter 97.

After `read_settings` returns, the rest of the script can believe the dictionary. Every check of the file happens in one function, at the moment the file comes in.

## The whole script

```python
#FLM: Sync Font Info
# Compares every open font with family-info.json, which sits beside the
# current font, and writes the differences into the current font only.
import json
from pathlib import Path

import halfmoon
from fly import fl
import fly.ap.core.scripting as scripting

DRY_RUN = True
FILE_NAME = "family-info.json"
ALLOWED = {"familyName", "openTypeNameDesigner", "copyright"}


def read_settings(path):
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
    for key, value in settings.items():
        if key not in ALLOWED:
            raise ValueError(f"{key} is not a field this script may set")
        if not isinstance(value, str):
            raise ValueError(f"{key} must be text in quotation marks")
    return settings


def differences(package, settings):
    found = []
    for key, wanted in settings.items():
        actual = getattr(package.info, key) or ""
        if actual != wanted:
            found.append((None, key, actual, wanted))
    return found


def main():
    current = scripting.current_package()
    if current is None:
        halfmoon.tell("Open a font first.")
        return
    path = Path(current.path).parent / FILE_NAME
    try:
        settings = read_settings(path)
    except FileNotFoundError:
        halfmoon.tell(f"I can't find {FILE_NAME} beside the font.")
        return
    except ValueError as problem:
        halfmoon.tell(f"{FILE_NAME} can't be used: {problem}")
        return
    packages = [fl.flPackage(item) for item in fl.flWorkspace.instance().packages()]
    todo = []
    waiting = 0
    for package in packages:
        found = differences(package, settings)
        mine = package.id == current.id
        print(f"{Path(package.path).name}{'  (current)' if mine else ''}")
        for master, key, actual, wanted in found:
            print(f"  {key}: {repr(actual)} should be {repr(wanted)}")
        if not found:
            print("  agrees")
        elif mine:
            todo = found
        else:
            waiting += 1
    if waiting:
        print(f"{waiting} other fonts differ. Click each one and run again.")
    if not todo:
        print("Nothing to change in the current font.")
        return
    if DRY_RUN:
        print(f"Dry run. {len(todo)} fields would change in the current font.")
        return
    result = scripting.write_font_info(current, todo, undo_name="Sync Font Info")
    print(f"{result['changed']} fields changed in the current font.")


main()
```

Save it as `sync_font_info.py`. With `Plum-practice` in front, the dry run prints:

```text
Plum-practice.vfj  (current)
  agrees
Plum-practice-copy.vfj
  openTypeNameDesigner: 'S. Sagano' should be 'Sora Sagano'
  copyright: '' should be 'GG Plum by Sora Sagano. Released under CC0 1.0 Universal: no rights reserved. Practice copy for the Halfmoon book.'
1 other fonts differ. Click each one and run again.
Nothing to change in the current font.
```

Click the copy's window and run again. The `(current)` label moves, and the last line becomes `Dry run. 2 fields would change in the current font.` Set `DRY_RUN = False`, run, and run once more:

```text
Plum-practice.vfj
  agrees
Plum-practice-copy.vfj  (current)
  agrees
Nothing to change in the current font.
```

Notes on the listing.

`fl.flWorkspace.instance().packages()` is FontLab's list of open fonts, and `fl.flPackage(item)` turns each entry into a package like the one `current_package()` gives you. Each package has an `id`, a number that's different for every open font. Comparing ids is how the script knows which of them is in front.

`differences` builds the writer's four-part tuples straight away, with the value it found as the old value. The report prints from the same list that the writer gets, so what you read in the dry run is what will be written.

The script takes no family name or designer from its own top. `FILE_NAME` and `ALLOWED` say where to look and what is permitted, and the values themselves come from the file. The same script serves Plum and Quince without an edit, which the copyright script of chapter 98 couldn't.

There are two `except` lines after one `try`. Python takes the first that fits. A missing file and a broken file need different sentences, because the reader has to do different things about them.

The script reads other fonts and writes only the one in front. I'd have liked one run to repair them all. Fly's writer answers a font that isn't current with `The preview font is no longer current; reopen the tool.`, and I found no proven way to bring another font to the front from a script. For Quince, that's six clicks and six runs, and every run prints how many fonts still differ. Six runs of a script that can't misspell is still better than typing six lines.

## Break it on purpose

Each of these breaks the settings file, and the script should answer each with one sentence and change nothing. Repair the file after each.

1. Put a comma after the last entry. You should see the message from step 3, after `family-info.json can't be used:`.
2. Misspell a key as `copyrihgt`: `copyrihgt is not a field this script may set`.
3. Replace `"GG Plum"` with `2026`, without quotes: `familyName must be text in quotation marks`.
4. Rename the file: `I can't find family-info.json beside the font.`

Four ways to be wrong, four sentences, and no traceback. A person who has never seen Python can fix each one.

## What the script can't do

It compares only fonts that are open. A font left closed on the disk isn't checked, and the script can't know that it exists.

It looks for the settings beside the current font. If the six files of a family live in six folders, each run reads a different file, or none.

It sets three text fields. The version is deliberately not among them. A version changes with every release, by a rule, and chapter 97 owns that rule.

## What you learned

A settings file keeps values outside the code, so a person can change them without editing a script, and JSON is the usual format: `json.dump` writes a dictionary and `json.load` reads it back. JSON is stricter than Python, with double quotes only and no comma after the last entry. Whatever comes from a file gets checked in one place, as it comes in, and refused with a sentence that names the key. `fl.flWorkspace.instance().packages()` lists the open fonts, which a script can read freely, though Fly's writer changes only the current one.

## Try it yourself

1. Add `"styleName"` to `ALLOWED` and to the file. Why is that a bad idea for a family, and what does the report say about the three masters?
2. Make the report end with a count: `2 of 2 fonts agree.` or `1 of 2 fonts agree.`
3. Write the opposite script: for every open font, save its three values to `<file name>-info.json` beside it. Compare two of the files in a text editor.

## Next

Names, Unicode, features and Font Info each have their own checking script now, and nobody will remember to run them all before a delivery. Chapter 100 calls them all from one.
