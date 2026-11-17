---
this_file: src_docs/README.md
---

# Build the book site

The source in `src_docs/md` contains the seven-part, 140-chapter manuscript.

Install `uv`, then run from the repository root:

```sh
uv sync --python 3.13
uv run fontlab-python-book
```

The small `fontlab-python-book` package installs Fire and the documentation dependencies. Its Fire CLI has one function: build the docs. No subcommand is needed. It accepts `--site-dir`, `--config` and `--verbose`. `uv sync` installs the project and dependencies from `uv.lock` into `.venv`. Both `./build.sh` and `sh src_docs/build.sh` use that environment and retain direct ProperDocs argument forwarding, installing dependencies on the first run as needed.

ProperDocs builds the Markdown in `src_docs/md` into `docs` with strict validation. The clean build replaces generated files in that destination. To inspect without changing `docs`, select a separate output directory:

```sh
uv run fontlab-python-book --site-dir /tmp/fontlab-python-book-preview
uv run python -m unittest discover -s tests_build -v
```

You can also install into an existing Python 3.13+ environment with `uv pip install -e .`, then run `fontlab-python-book` directly. The wheel contains the builder, not the manuscript: keep the source checkout available. Run an installed wheel's command from the book checkout, or pass `--config /path/to/checkout/src_docs/mkdocs.yml`.

All navigation targets and internal link targets must exist: warnings fail the strict build. Add chapters to `src_docs/mkdocs.yml` only when their source files exist. Keep images original and document their provenance; this scaffold imports no other book's media.

The package pins the existing ProperDocs 1.6.7, MkDocs 1.6.1, MaterialX 10.1.8 and pymdown-extensions 11.0.1 versions, plus Fire 0.7.1. `pyproject.toml` declares the installed dependencies; refresh `uv.lock` deliberately with `uv lock`. Keep the legacy documentation-only requirements recipe aligned when changing these four documentation pins:

```sh
uv pip compile --python-version 3.13 --generate-hashes --output-file src_docs/requirements.txt src_docs/requirements.in
```

`SOURCE_DATE_EPOCH` defaults to `0` (the Unix epoch), so builds need no Git commands. Set it explicitly to use a different reproducible timestamp.

The base fltheme26 CSS and JavaScript use versioned external URLs from the manual reference. No manual-specific template or menu is copied. Network delivery, visual appearance, keyboard access and mobile behaviour require browser acceptance; static build success does not establish these. No canonical deployment URL or publication route is configured.
