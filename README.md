# PhxPict

**A privacy-first, cross-platform photo search application created and owned by MacroStofft.**

PhxPict indexes a photo repository selected by the user and makes images searchable by:

- camera capture date (EXIF when available);
- filesystem modification date;
- filename, folder, and content tags;
- categories such as people/profiles, nature, buildings, automobiles, trains, planes, and warfare.

The MVP runs locally on Windows, macOS, and Linux. It does not upload photographs, require an account, or depend on a cloud service.

## Working MVP

- Native folder picker
- Recursive photo indexing
- Persistent SQLite catalog in `~/.phxpict/photos.sqlite3`
- EXIF and file metadata extraction
- Searchable content tags
- Capture/modification date range filters
- Responsive thumbnail gallery
- Double-click to open an image in the operating system
- CLI for automation and headless environments
- Extensible `ContentTagProvider` interface for later local ML integration

## Quick start

Python 3.9+ with Tk support is required.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -e .
phxpict
```

## CLI

```bash
phxpict-cli index /path/to/photos
phxpict-cli search nature --date-field capture_date --start 2020-01-01 --end 2026-12-31
phxpict-cli search "people automobiles"
```

Each space-separated search term must match the path, filename, or tags.

## Content search today

The MVP ships with a deterministic filename/folder baseline. For example, `Family/Beach portrait.jpg` receives `people` and `nature` tags. This demonstrates the end-to-end indexing and search architecture without forcing a large ML model download.

See [Architecture](docs/ARCHITECTURE.md) for the local semantic-model provider path and [Roadmap](docs/ROADMAP.md) for planned features.

## Test

```bash
python -m unittest discover -s tests -v
```

## Repository layout

```text
src/phxpict/       application, indexer, database, provider interface
tests/             automated core tests
docs/              architecture and roadmap
```

## Current limitations

- Baseline categories use filename and directory terms, not pixels.
- HEIC support depends on the Pillow build/platform codec.
- The UI indexes in a worker thread, but very large libraries still need cancellation and incremental-update controls.
- Installers and code signing are not included in this MVP.
- People search is category-level only; face recognition/identity labeling is intentionally deferred for privacy design review.

## Ownership and licensing

PhxPict is a MacroStofft project. Copyright © 2026 MacroStofft. All rights reserved pending final license selection. See [LICENSE.md](LICENSE.md).

