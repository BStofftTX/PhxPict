# Architecture

## Components

1. **Tkinter desktop UI** — native folder picker, filters, thumbnail gallery, file opening.
2. **Indexer** — recursively discovers supported images and extracts filesystem and EXIF metadata with Pillow.
3. **SQLite index** — persists searchable paths, dates, dimensions, and tags locally.
4. **Content provider interface** — keeps tag generation replaceable and the base application lightweight.
5. **Local CLIP provider** — optional zero-shot pixel classification against a controlled seven-category vocabulary.
6. **Graceful fallback provider** — combines visual tags with deterministic path tags and disables visual inference if optional dependencies or weights cannot load.

## Privacy model

- The index is stored under `~/.phxpict/`.
- Images are read in place and are not uploaded or copied.
- No telemetry or hosted-inference service is included.
- Local CLIP inference receives a filesystem path and runs in-process; image bytes are not placed in an HTTP request.
- The selected model's weights may be downloaded once from Hugging Face and cached locally. Fully offline use is available after caching.
- Future cloud providers must be opt-in and disclose exactly what leaves the computer.

## Visual provider implementation

`LocalCLIPTagProvider` implements `ContentTagProvider.tags_for()` with the Hugging Face zero-shot image-classification pipeline. It loads the model once, scores seven controlled text descriptions against each image, and stores up to three normalized category tags. Its classifier is injectable for deterministic tests.

The default provider is `GracefulFallbackTagProvider(LocalCLIPTagProvider())`. It always retains deterministic filename/folder tags and permanently disables the visual provider for the current indexing run if model initialization or inference is unavailable.

The CLI can explicitly select `auto`, `clip`, or `filename` behavior. The desktop application uses `auto`.

## Future semantic search

Free-text similarity search still requires an embedding/vector index. A later provider can:

1. load the model once;
2. compute and persist image embeddings;
3. embed arbitrary local text queries;
4. retrieve nearest images through a vector index;
5. retain the same no-upload boundary.

Candidate local integrations must be benchmarked for CPU/GPU/RAM use, classification quality, model licensing, and representative-library bias.

## Known boundaries

- Categories are whole-image similarities rather than bounding-box detections.
- `people` includes faces, portraits, and profiles but does not identify anyone.
- `warfare` is broad and needs human validation before archival or evidentiary use.
- SQLite currently stores normalized tags, not raw model scores, bounding boxes, or embeddings.
