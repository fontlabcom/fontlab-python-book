---
this_file: src_docs/md/part2-a-toolbox/025-the-missing-list.md
---

# 25. The missing list

Friday. Yesterday's answer about Hungarian went down well, and it has had the usual effect of a good answer, which is more questions. The publisher's rights person has sent Ines a list of five languages they sell books in: French, German, Hungarian, Polish and Czech.

"She wants to know what's missing for each one," Ines says. "And I want to know how many letters that is in total, because I'm the one who has to say when they'll be drawn."

Mira could run `have_we_got.py` five times with five test sentences. But a sentence isn't a language. The Hungarian one happened to have no capital Ő in it. What she needs is to take everything a language needs, take away everything the font has, and see what's left.

That's a subtraction. Python has a container you can subtract.

## What you need

- FontLab 9 with Fly installed, and `Plum-practice` open.
- `have_we_got.py` from [chapter 24](024-find-by-unicode.md).

## Step 1: A bag with no doubles

Type this, with no font involved yet:

```python
letters = set("banana")
print(letters)
print(len(letters))
```

```text
{'b', 'n', 'a'}
3
```

Your three letters may come out in a different order. That's the first thing to know about what you've made.

This is a **set**. Picture a cloth bag. You can drop things in and you can ask whether something's in there, but the things have no order, and the bag won't hold two of the same. "banana" has six letters and three different ones, and the bag kept the three.

A list is a row. It has a first and a last, and it can hold the same thing twice. A set has no first and no last, and holds each thing once. You can check that it has no first:

```python
print(letters[0])
```

```text
TypeError: 'set' object is not subscriptable
```

"Subscriptable" is Python's word for "you can use square brackets on it". You can't. There's no place number 0 in a bag.

When you want to read a set, put it in order on the way out with `sorted`, which you know from chapter 10. It hands you a list:

```python
print(sorted(letters))
```

```text
['a', 'b', 'n']
```

You can also write a set out by hand, with curly braces and no colons: `{"a", "b", "n"}`. Curly braces with colons make a dictionary. Curly braces without make a set. One trap: empty curly braces, `{}`, make an empty dictionary, as you saw in chapter 21. For an empty set you write `set()`.

## Step 2: Take one bag from another

Here's what sets are for. Two small ones:

```python
need = set("äöüß")
have = set("abcäö")

print(sorted(need - have))
```

```text
['ß', 'ü']
```

The minus sign between two sets means "everything in the first that isn't in the second". German needs four special letters, this pretend font has two of them, and the two left over are the missing list. You wrote no loop and no `if`. The subtraction is the whole question.

There are two more signs, and you'll want both today.

```python
print(sorted(need & have))
print(sorted(need | have))
```

```text
['ä', 'ö']
['a', 'b', 'c', 'ß', 'ä', 'ö', 'ü']
```

`&` means "in both". Read it as "and": in `need` and in `have`. `|` is the upright bar, on most keyboards near the Return key, and it means "in either". Read it as "or". It pours both bags into one, and because a set won't hold doubles, the ä and the ö show up once.

The three have names from school math that you may remember: difference, intersection and union. You don't need the names to use the signs.

Notice that the order matters for minus and not for the other two. `have - need` is a different question: what does the font have that the language doesn't need? Here that's a, b and c.

## Step 3: Everything the font has

Now the real font. Yesterday you built `by_number`, a dictionary filed by Unicode value. Today you want something simpler, the bag of characters that Plum can show.

```python
from fly import fl

font = fl.CurrentFont()
have = set()
for glyph in font.glyphs:
    if glyph.unicode is not None:
        have.add(chr(glyph.unicode))

print(len(have))
```

```text
204
```

`add` is to a set what `append` is to a list: it drops one more thing in. `chr` turns each glyph's number back into its character, as in chapter 23. So `have` holds 204 characters: A, B, é, €, the space and all the rest.

Asking a set whether it holds something uses `in`, the same word as for lists and dictionaries:

```python
print("é" in have)
print("ő" in have)
```

```text
True
False
```

## Step 4: Everything a language needs

Next, the other bag. Hungarian writes with the plain letters a to z plus nine accented ones. The plain ones Plum has, so I'll only list the nine:

```python
letters = "áéíóöőúüű"
need = set(letters)
print(sorted(need - have))
```

```text
['ő', 'ű']
```

The same two as yesterday. But yesterday's sentence had no capitals in it apart from the first letter, and a book has chapter titles. A function that lives in a drawer of an object is called a **method**. You've used several without the word: `append` on a list, `split` on text. Text has one called `upper`, which hands back the same text in capitals:

```python
print(letters.upper())
```

```text
ÁÉÍÓÖŐÚÜŰ
```

Pour both into one bag with the "or" sign, then subtract:

```python
need = set(letters) | set(letters.upper())
missing = need - have
print(len(need), "needed,", len(missing), "missing:", sorted(missing))
```

```text
18 needed, 4 missing: ['Ő', 'ő', 'Ű', 'ű']
```

Four, not two. Mira guessed at the capitals in her message yesterday. Now she knows.

One caution about `upper`. It follows the rules of Unicode, and for a few letters those rules are odd. The German ß has no capital in everyday spelling, so `"ß".upper()` hands back `SS`, two letters. Your set of German capitals ends up with an S in it and no capital ß. For this job that does no harm, since Plum has an S. It does mean that "German: complete" below leaves out the capital sharp s, ẞ, which Plum doesn't have. Keep it in mind when a count looks odd.

## Step 5: Five languages at once

You have five languages and one question to ask of each. That's a dictionary and a loop. The keys are the language names and the values are the special letters:

```python
languages = {
    "French": "àâæçéèêëîïôœùûüÿ",
    "German": "äöüß",
    "Hungarian": "áéíóöőúüű",
    "Polish": "ąćęłńóśźż",
    "Czech": "áčďéěíňóřšťúůýž",
}

for language, letters in languages.items():
    need = set(letters) | set(letters.upper())
    missing = need - have
    if len(missing) == 0:
        print(f"{language}: complete")
    else:
        missing_text = " ".join(sorted(missing))
        print(f"{language}: {len(missing)} missing: {missing_text}")
```

```text
French: complete
German: complete
Hungarian: 4 missing: Ő ő Ű ű
Polish: 16 missing: Ą ą Ć ć Ę ę Ł ł Ń ń Ś ś Ź ź Ż ż
Czech: 18 missing: Č č Ď ď Ě ě Ň ň Ř ř Š š Ť ť Ů ů Ž ž
```

There's one new thing in that listing, `" ".join(...)`. It's the opposite of `split` from chapter 9. `split` cuts a string into a list. `join` glues a list into one string, and the string in front of the dot is the glue. Here the glue is a single space. It makes the missing letters print as a neat row and not as a list with brackets and quote marks, which Ines would have to explain to the rights person.

I typed those five alphabets from a reference book. They're the letters each language needs beyond a to z, and nothing more: no quote marks, no special punctuation. A real check would add those. This one answers the question that was asked.

Look at what the result says about Plum. It's a font for Western Europe. French and German are done, down to the œ and the ÿ. Hungarian is nearly done. Polish and Czech have hardly been started: Polish has only its ó, and Czech only the acute accents it shares with everyone else.

## Step 6: How many to draw

Ines wanted a total. You might add 4 and 16 and 18 and say 38. Are you sure no letter is on two lists? Polish and Czech are neighbors, and neighbors share.

Don't guess. Pour every missing list into one bag and count the bag. A set won't hold doubles, so anything shared gets counted once:

```python
to_draw = set()
for language, letters in languages.items():
    need = set(letters) | set(letters.upper())
    to_draw = to_draw | (need - have)

print(len(to_draw), "characters to draw")
```

```text
38 characters to draw
```

Thirty-eight after all. This time the plain sum was right, because the letters these languages share, like á and ó, are ones Plum already has. Add Slovak to the dictionary and it stops being right: Slovak wants č, ď, ň, š, ť and ž as well, and the sum would count them twice. The set never does.

`to_draw = to_draw | ...` is the pattern from the counter in chapter 7, `count = count + 1`, done with bags. Take what's in the box, pour more in, put the result back in the same box.

Mira sends Ines three lines and a number. Ines does her own sum: thirty-eight letters, most of them a base letter with an accent the font partly has. "Two weeks," she tells the rights person, "if nothing else comes in." Something else always comes in.

Put the pieces together and save them as `missing_chars.py`: the lines that fill `have` from step 3, the `languages` dictionary and its loop from step 5, and the total from step 6.

??? info "Going deeper: where real language lists come from"
    Nobody types alphabets from memory for production work. The Unicode Consortium publishes a free database called CLDR that lists the characters each language uses, and several font tools ship ready-made lists built from it. In chapter 27 you read such a list from a text file, so that the next language is a file somebody sends you and not a line you type.

## What you learned

A set is a bag that holds each thing once and keeps no order. With two sets, `-` gives what's in the first and not the second, `&` what's in both and `|` everything in either, and that turns "what's missing?" into one subtraction. `add` puts one thing in, `sorted` lays a set out for reading, and `' '.join(...)` glues a list of strings into one line.

## Try it yourself

1. Add Turkish to the dictionary with the letters `çğıöşü` and run the script. Then look at what `"ı".upper()` and `"i".upper()` give you, and say why a careful Turkish check needs one more capital than `upper` provides.
2. Turn the subtraction around. Which characters does Plum have that none of the five languages asked for and that aren't plain letters a to z or A to Z? Build one big `need` set first. You'll get figures and punctuation, and some letters. Which languages might those letters be for?
3. Use `&` to find which special letters Hungarian and Czech have in common. Then find the letters that Polish and Czech share. Does the answer fit what step 6 said about the total?

## Next

In chapter 26 the report stops living in the Output panel. Ines wants a file she can attach to an email.
