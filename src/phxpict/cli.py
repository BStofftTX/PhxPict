from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .database import PhotoDatabase
from .indexer import index_folder
from .providers import (
    GracefulFallbackTagProvider,
    ProviderUnavailableError,
    build_tag_provider,
)


def default_database() -> Path:
    return Path.home() / ".phxpict" / "photos.sqlite3"


def main() -> None:
    parser = argparse.ArgumentParser(description="PhxPict local photo index")
    parser.add_argument("--database", type=Path, default=default_database())
    sub = parser.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index")
    index.add_argument("folder", type=Path)
    index.add_argument(
        "--content-provider",
        choices=["auto", "filename", "clip"],
        default="auto",
        help="auto uses local CLIP when installed and otherwise falls back to filename tags",
    )
    index.add_argument(
        "--clip-model",
        default="openai/clip-vit-base-patch32",
        help="local Hugging Face zero-shot image model",
    )
    search = sub.add_parser("search")
    search.add_argument("text", nargs="?", default="")
    search.add_argument("--date-field", choices=["capture_date", "modified_date"], default="capture_date")
    search.add_argument("--start")
    search.add_argument("--end")
    args = parser.parse_args()
    database = PhotoDatabase(args.database)
    try:
        if args.command == "index":
            provider = build_tag_provider(args.content_provider, args.clip_model)
            count = index_folder(args.folder, database, provider=provider)
            print(f"Indexed {count} image(s). Database total: {database.count()}.")
            if isinstance(provider, GracefulFallbackTagProvider) and provider.fallback_reason:
                print(
                    f"Visual provider unavailable; used filename tags: {provider.fallback_reason}",
                    file=sys.stderr,
                )
        else:
            for photo in database.search(args.text, args.date_field, args.start, args.end):
                print(f"{photo.capture_date or photo.modified_date}\t{photo.tags}\t{photo.path}")
    except ProviderUnavailableError as exc:
        parser.exit(2, f"Visual content provider unavailable: {exc}\n")
    finally:
        database.close()


if __name__ == "__main__":
    main()
