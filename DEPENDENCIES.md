---
this_file: DEPENDENCIES.md
---

The docs builder is an installable Python 3.13+ package declared in `pyproject.toml`. `uv sync` installs it with Fire 0.7.1, ProperDocs 1.6.7, MkDocs 1.6.1, MaterialX 10.1.8 and pymdown-extensions 11.0.1; `uv.lock` records transitive dependencies. Fire exposes the single build function; ProperDocs and the existing theme/extensions render the site. These dependencies cover documentation builds only. The legacy `src_docs/requirements.in` and hashed `src_docs/requirements.txt` remain available as the documentation-only recipe.
