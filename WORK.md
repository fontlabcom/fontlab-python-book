---
this_file: WORK.md
---

# Current work

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

Independent review, combined-source delivery checks and live FontLab acceptance remain open.

Authored-source whitespace checks pass. The unfiltered Git whitespace check
reports whitespace-only indentation emitted in changed generated HTML by the
existing theme; it is retained for deterministic build parity. No generated
HTML was hand-edited to hide that warning.
