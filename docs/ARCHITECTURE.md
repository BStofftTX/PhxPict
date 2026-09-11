# Architecture

## MVP components

1. **Tkinter desktop UI** — native folder picker, filters, thumbnail gallery, file opening.
2. **Indexer** — recursively discovers supported images and extracts filesystem and EXIF metadata with Pillow.
3. **SQLite index** — persists searchable paths, dates, dimensions, and tags locally.
4. **Content provider interface** — makes tag generation replaceable without coupling ML dependencies to the core app.
5. **Filename baseline provider** — deterministic offline categories derived from path/filename words.

## Privacy model

- The index is stored under `~/.phxpict/`.
- Images are read in place and are not uploaded or copied.
- No telemetry or network service is included.
- Future cloud providers must be opt-in and disclose exactly what leaves the computer.

## Real semantic provider path

Implement `ContentTagProvider.tags_for()` with a local image-text embedding model. The recommended production path is a separate optional dependency group and a background worker that:

1. loads the model once;
2. computes embeddings or scores against a controlled vocabulary;
3. stores normalized tags and optional embeddings;
4. allows free-text similarity search through a vector index;
5. never transmits images unless the user explicitly enables a cloud provider.

Candidate local integrations should be benchmarked for CPU/GPU/RAM use and licensing before selection. The baseline intentionally avoids silently downloading multi-gigabyte models.

