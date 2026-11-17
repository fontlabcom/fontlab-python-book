# this_file: src/fontlab_python_book/__init__.py
"""Build the book using the dependencies installed with this package."""

import os
import subprocess
import sys
from pathlib import Path

import fire


def build(
    site_dir: str | None = None,
    config: str | None = None,
    verbose: bool = False,
) -> None:
    """Build the docs strictly; use --site-dir for a separate preview folder.

    Run in the book checkout, or supply --config=/path/to/src_docs/mkdocs.yml.
    """
    config_path = Path(config or "src_docs/mkdocs.yml").resolve()
    if config is None and not config_path.is_file():
        config_path = Path(__file__).resolve().parents[2] / "src_docs/mkdocs.yml"
    if not config_path.is_file():
        raise SystemExit(
            "Book sources not found; run in the checkout or pass --config."
        )
    command = [
        sys.executable,
        "-m",
        "properdocs",
        "build",
        "--strict",
        "--clean",
        "-f",
        str(config_path),
    ]
    if site_dir is not None:
        command.extend(["--site-dir", str(site_dir)])
    if verbose:
        command.append("--verbose")
    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = env.get("SOURCE_DATE_EPOCH") or "0"
    result = subprocess.run(
        command, cwd=config_path.parent.parent, env=env, check=False
    )
    if result.returncode:
        raise SystemExit(result.returncode)


def main() -> None:
    """Expose the single build function through Python Fire."""
    fire.Fire(build)
