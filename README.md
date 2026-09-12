# PhxPict

**A privacy-first, cross-platform photo search application created and owned by MacroStofft.**

PhxPict indexes a photo repository selected by the user and makes images searchable by:

- camera capture date (EXIF when available);
- filesystem modification date;
- filename, folder, and optional local visual-content tags;
- categories such as people/profiles, nature, buildings, automobiles, trains, planes, and warfare.

The MVP runs locally on Windows, macOS, and Linux. It does not upload photographs, require an account, or depend on a cloud service.

## Working MVP

- Native folder picker
- Recursive photo indexing
- Persistent SQLite catalog in `~/.phxpict/photos.sqlite3`
- EXIF and file metadata extraction
- Searchable local visual-content tags through an optional CLIP model
- Capture/modification date range filters
- Responsive thumbnail gallery
- Paginated results so large libraries do not render every thumbnail at once
- HEIC/HEIF support for common iPhone photo libraries
- Double-click to open an image in the operating system
- CLI for automation and headless environments
- Extensible `ContentTagProvider` interface with graceful lightweight fallback

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

## Local visual-content search

The normal install stays lightweight. In `auto` mode PhxPict uses a local CLIP
zero-shot image classifier when its optional dependencies are installed, then
combines pixel-derived tags with deterministic filename/folder tags. If the
model or dependencies cannot load, indexing continues with filename/folder
tags instead of failing.

Install local visual search:

```bash
python -m pip install -e ".[visual]"
phxpict-cli index /path/to/photos --content-provider clip
```

The default model is `openai/clip-vit-base-patch32`. On first use, model weights
may be downloaded and cached by Hugging Face. Image files remain on the
computer and are passed only to the in-process model; PhxPict contains no image
upload or cloud-inference code.

Provider modes:

- `auto` (default): visual tags when available, graceful filename fallback;
- `clip`: require local visual inference and report a clear error if unavailable;
- `filename`: deterministic path/filename tags only.

The controlled visual vocabulary is: `people`, `nature`, `buildings`,
`automobiles`, `trains`, `planes`, and `warfare`.

See [Architecture](docs/ARCHITECTURE.md) for the local semantic-model provider path and [Roadmap](docs/ROADMAP.md) for planned features.

## Test

```bash
python -m unittest discover -s tests -v
```

## Tomorrow-ready demo

See [Demo Guide](docs/DEMO.md). For a library containing thousands of photos,
install and cache the local visual model before the visit, then pre-index the
library or a representative copy. Local visual inference is private but can be
slow on CPU; searches are fast after indexing.

## Repository layout

```text
src/phxpict/       application, indexer, database, provider interface
tests/             automated core tests
docs/              architecture and roadmap
```

## Current limitations

- Visual search is broad category classification, not object detection, face
  identity recognition, or proof that a depicted event actually occurred.
- CLIP confidence is relative to the seven controlled labels and can produce
  false positives, especially for ambiguous, historical, or composite scenes.
- Optional CLIP dependencies and model weights are substantially larger than
  the base install; CPU indexing can be slow on large libraries.
- The GUI uses `auto` mode but does not yet expose model or threshold settings.
- HEIC support depends on the Pillow build/platform codec.
- The UI indexes in a worker thread, but very large libraries still need cancellation and incremental-update controls.
- Installers and code signing are not included in this MVP.
- People search is category-level only; face recognition/identity labeling is intentionally deferred for privacy design review.

## Ownership and licensing

PhxPict is a MacroStofft project. Copyright © 2026 MacroStofft. All rights reserved pending final license selection. See [LICENSE.md](LICENSE.md).
