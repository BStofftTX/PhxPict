from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from PIL import Image, UnidentifiedImageError

from .database import Photo, PhotoDatabase
from .providers import ContentTagProvider, FilenameTagProvider


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".heic"}


def iter_images(root: Path) -> Iterator[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def _capture_date(image: Image.Image) -> str | None:
    try:
        raw = image.getexif().get(36867) or image.getexif().get(306)
        if raw:
            return datetime.strptime(str(raw), "%Y:%m:%d %H:%M:%S").isoformat()
    except (ValueError, TypeError):
        pass
    return None


def inspect_photo(path: Path, provider: ContentTagProvider) -> Photo:
    stat = path.stat()
    capture, width, height = None, None, None
    try:
        with Image.open(path) as image:
            capture = _capture_date(image)
            width, height = image.size
    except (UnidentifiedImageError, OSError):
        pass
    return Photo(
        path=str(path.resolve()),
        filename=path.name,
        capture_date=capture,
        modified_date=datetime.fromtimestamp(stat.st_mtime).isoformat(),
        tags=", ".join(provider.tags_for(path)),
        width=width,
        height=height,
    )


def index_folder(
    root: Path,
    database: PhotoDatabase,
    provider: ContentTagProvider | None = None,
    progress: Callable[[int, Path], None] | None = None,
) -> int:
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    tagger = provider or FilenameTagProvider()
    count = 0
    for count, path in enumerate(iter_images(root), start=1):
        database.upsert(inspect_photo(path, tagger))
        if count % 50 == 0:
            database.commit()
        if progress:
            progress(count, path)
    database.commit()
    return count

