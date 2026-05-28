# ff-synctool

Small Python PoC for reading Firefox's local synced-tabs database and exporting the tab list from each remote device as JSON.

## What it does

When you're signed into Firefox Sync, Firefox mirrors the list of open tabs from every other signed-in device into a local SQLite database (`synced-tabs.sqlite3`) inside your profile directory. The `tabs` table holds one row per remote device, with the actual tab metadata stored as an escaped JSON blob in the `record` column.

[`ff_synctool.export`](src/ff_synctool/export.py) opens that database, decodes each `record`, and writes one `tab_<guid>.json` file per remote device into the current directory.

## Where to find `synced-tabs.sqlite3`

Inside your active Firefox profile folder:

- **Linux:** `~/.mozilla/firefox/<profile>/synced-tabs.sqlite3`
- **macOS:** `~/Library/Application Support/Firefox/Profiles/<profile>/synced-tabs.sqlite3`
- **Windows:** `%APPDATA%\Mozilla\Firefox\Profiles\<profile>\synced-tabs.sqlite3`

Close Firefox before reading the file, or copy it elsewhere first — SQLite may refuse to open it while Firefox holds a lock.

## Installation

The fastest way is [`uv`](https://docs.astral.sh/uv/) — no manual venv, no system Python pollution.

Run it once, zero install, latest published version:

```sh
uvx ff-synctool-export path/to/synced-tabs.sqlite3
```

Install as a persistent CLI on your `$PATH`:

```sh
uv tool install ff-synctool
ff-synctool-export path/to/synced-tabs.sqlite3
```

Or use pip / pipx if you prefer:

```sh
pipx install ff-synctool      # isolated install, recommended for pip users
pip install ff-synctool       # into the active environment
```

## Usage

```sh
ff-synctool-export path/to/synced-tabs.sqlite3
```

Or run the module directly from a checkout (no install needed):

```sh
python -m ff_synctool.export path/to/synced-tabs.sqlite3
```

This writes a `tab_<guid>.json` file per remote device into the working directory. Each file looks roughly like:

```json
{
  "id": "DFKDGhG1_yV-",
  "clientName": "mike's Firefox Developer Edition on Mike-MBP",
  "tabs": [
    {
      "title": "The lethal trifecta for AI agents…",
      "urlHistory": ["https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/"],
      "icon": "https://simonwillison.net/favicon.ico",
      "lastUsed": 1750500277
    }
  ]
}
```

## `ff_synctool.commands`

[`ff_synctool.commands`](src/ff_synctool/commands.py) is a second exploratory module that dumps the `remote_tab_commands` table — the queue Firefox uses for "Send Tab to Device". It currently hardcodes the database path (`synced_tabs.sqlite3`) and prints each pending command (open URL / close tab) to stdout.

## Schema reference

```text
sqlite> PRAGMA table_info(tabs);
0|guid|TEXT|1||1
1|record|TEXT|1||0
2|last_modified|INTEGER|1||0
```

## Status

Proof of concept. Read-only against your Firefox profile, no warranty. Not affiliated with Mozilla.

## Development

With [`uv`](https://docs.astral.sh/uv/) (recommended — auto-creates `.venv`, locks resolution):

```sh
uv sync --extra dev
uv run ruff check .
uv run pytest
```

Or plain pip in your own venv:

```sh
pip install -e ".[dev]"
ruff check .
pytest
```

CI runs ruff + pytest on Python 3.12, 3.13, and 3.14 — see [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Releases

Tag-driven publish to PyPI via [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (no API tokens) — see [.github/workflows/release.yml](.github/workflows/release.yml).

To cut a release:

1. Bump `version` in [pyproject.toml](pyproject.toml).
2. Commit and tag matching the version, prefixed with `v` (e.g. `git tag v0.1.1 && git push --tags`).
3. The workflow verifies the tag matches `pyproject.toml`, builds sdist + wheel, and publishes to PyPI.

First-time setup: on [pypi.org](https://pypi.org), add this repo as a trusted publisher for the `ff-synctool` project (workflow `release.yml`, environment `pypi`).

## Roadmap / suggested improvements

Concrete next steps to turn this into something more durable, ordered roughly by impact-vs-effort:

- [x] **Tests with pytest.** See [tests/test_export.py](tests/test_export.py).
- [x] **CI via GitHub Actions.** Ruff + pytest on Ubuntu, Python 3.12/3.13/3.14.
- [x] **Project metadata + src layout.** PEP 621 [pyproject.toml](pyproject.toml), `src/ff_synctool/` package, console script `ff-synctool-export`. Stdlib-only at runtime.
- [x] **Tag-driven PyPI release workflow.** See [.github/workflows/release.yml](.github/workflows/release.yml).
- [ ] **CLI polish in `ff_synctool.export`.**
  - Use the `--json` argument (currently parsed but ignored) or remove it.
  - Add `--output-dir` so output doesn't pollute CWD.
  - Replace f-string path joins with `pathlib.Path`.
  - Close the sqlite connection (`contextlib.closing` or explicit `conn.close()`).
  - Open the DB read-only: `sqlite3.connect(f"file:{path}?mode=ro", uri=True)` so a running Firefox can't be corrupted.
- [ ] **Normalise `ff_synctool.commands`.** Drop the hardcoded filename, take the DB path as an argument, add an `if __name__ == "__main__": main()` guard, and consider merging into `export` as a subcommand (`export tabs` / `export commands`).
- [ ] **Type hints + ruff/mypy.** Small surface area, easy win.
- [ ] **LICENSE file.** MIT or Apache-2.0 — currently absent.
- [ ] **Optional: pretty-print mode.** A `--format=table` flag that prints titles + URLs to stdout for quick inspection without writing files.
