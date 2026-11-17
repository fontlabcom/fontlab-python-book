---
this_file: README.md
---

# FontLab Python book

A tutorial book on Python scripting in FontLab 9: seven parts and 140 chapters, from a first `print` in the Output panel to packaged tools with panels, menus and tests.

The Markdown source is in `src_docs/md`. The built site is in `docs`.

## Build

```sh
uv sync --python 3.13
uv run fontlab-python-book
```

`./build.sh` does the same from any directory. To preview without touching `docs`, pass `--site-dir /tmp/book-preview`. Details, test commands and dependency pins are in [src_docs/README.md](src_docs/README.md) and [DEPENDENCIES.md](DEPENDENCIES.md).

The book is a manuscript in progress: its code samples have not yet been run in FontLab 9.
