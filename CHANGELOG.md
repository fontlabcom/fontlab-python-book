---
this_file: CHANGELOG.md
---

## 2026-11-17 — Read-only build workflow

Added a pinned GitHub Actions build for main pushes and pull requests. It uses
uv 0.13.7 and Python 3.13, checks the lock, runs the 8 existing builder tests,
builds the complete site strictly and requires committed generated output parity.
The exact local build commands pass; all generated files retain their frozen
candidate bytes. Actionlint passes. The workflow has read-only permissions and
no publication step. Actual GitHub CI remains unverified until delivery.

## 2026-11-17 — Public installer link

Chapter 4 points to the canonical standalone installer download. The strict book
build passed in 3.21 seconds and regenerated that chapter and search output.
The linked file is generated from the canonical installer by its own project;
live URL verification and reviewed delivery remain separate gates.


## 2026-11-17 — Instamix teaching update

Revised chapters 4, 133 and 134 for the corrected Instamix bootstrap, declared
project versions, current installer generation, extension manifests/archives and
canonical lowercase plugin suffixes. The package-checking example reads the
actual Instamix project contract instead of maintaining a second id parser.
App's lowercase bundle floor is 1.2.31. Native manuscript examples remain
unverified; source checks do not establish a running FontLab workflow.

The existing 8 build-command tests pass. The complete strict book build passes
in 2.89 seconds. Focused fixture checks validate the printed project checker,
negative metadata/files, the reporter draft wrap, manifest and CLI examples;
all Python fences on the affected teaching pages compile. The check used an
ordinary installed fixed candidate wheel; publication/native acceptance is
separate. No dependencies, builders or archived chapters changed.

## Unreleased: new book

- Moved the earlier manuscript to `src_docs/md-old/` and its tests to `tests_docs-old/`.
- Started the new tutorial book in `src_docs/md/`: start page, seven part folders, Part 1 chapters 1 to 7.
- Parts 1 and 2 (chapters 1 to 40) written and revised.
- Part 3, Shapes (chapters 41 to 60), written: contours, pens, transforms, components, anchors, accent building with a problem report. Revised.
- Part 4, Space (chapters 61 to 80), written: sidebearings, spacing groups, metrics rules, tabular figures, kerning pairs and classes, kerning proof, spreadsheet round trip, scaling, spacing audit.
- Opening pages for Parts 2, 3 and 4.
- Part 5, Words (chapters 81 to 100), written and revised: glyph names and Unicode, OpenType feature text, Font Info, pre-flight.
- Part 6, Families (chapters 101 to 120), written and revised: masters, compatibility, interpolation, export, inspection of exported files, the Friday build, the release folder.
- Part 7, Tools (chapters 121 to 140), written: windows and widgets, a panel with Undo, menus, packaging, a reporter plugin, Glyphs scripts through Glyport, fontParts through Fontport, Remopy, GrabLab, pytest, and the closing chapter. Opening pages for Parts 5, 6 and 7.
- Part 7 corrected: Glyport's run handle, pytest in the package folder, Remopy's two time limits, the progress dialog's Cancel, Fly's partial-write message, and 37 smaller points.
- Chapters 21 to 80 revised for Fly's refusal to edit bases of automatic glyphs (`allow_bases=True`) and its refusal to write automatic glyphs at all.
- Continuity: Oskar returns from leave in chapter 93; stated there and in the Part 5 opener.
- Media: seven pencil illustrations on the part openers and two SVG diagrams (chapters 41 and 119), each with alt text and a caption; how they were made is in `src_docs/md/assets/PROVENANCE.md`. The site leaves that file out.
- Continuity pass over the whole book: back-references to named functions checked (fixed in 007 and 082), calendar read end to end (fixed in 060), unparseable blocks confirmed deliberate.
- Examples no longer import a shared `halfmoon` module. Every script calls Fly, TypeRig and FontLab directly and writes out the small helpers it uses, so each one runs by itself after chapter 4's install. Chapter 33 teaches modules with real ones; the packaging chapters build `spacing_tools` with all of its source on the page.
- All 140 chapters are in the nav; about 243,000 words of prose outside code listings.
- No sample has been run in FontLab 9 yet.

## Unreleased: root build launcher

- Add executable `build.sh` forwarding arguments to the strict site build from any working directory.
- Default build timestamps to the Unix epoch without invoking Git; retain explicit `SOURCE_DATE_EPOCH` overrides.
- Update build instructions; shell syntax, 8 documentation tests and a strict scratch build pass.

## Unreleased: installable docs builder

- Add `fontlab-python-book` package, dependency lock and default Fire docs build function with config/output/verbose options.
- Use the package environment in shell builds while retaining direct ProperDocs flags.
- Document installation and limit distribution archives to the builder and its tests.
- Verify 16 tests, fresh wheel installation, archive contents and strict full-book preview builds.
