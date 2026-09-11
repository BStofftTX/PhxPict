from __future__ import annotations

import argparse
from pathlib import Path

from .database import PhotoDatabase
from .indexer import index_folder


def default_database() -> Path:
    return Path.home() / ".phxpict" / "photos.sqlite3"


def main() -> None:
    parser = argparse.ArgumentParser(description="PhxPict local photo index")
    parser.add_argument("--database", type=Path, default=default_database())
    sub = parser.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index")
    index.add_argument("folder", type=Path)
    search = sub.add_parser("search")
    search.add_argument("text", nargs="?", default="")
    search.add_argument("--date-field", choices=["capture_date", "modified_date"], default="capture_date")
    search.add_argument("--start")
    search.add_argument("--end")
    args = parser.parse_args()
    database = PhotoDatabase(args.database)
    try:
        if args.command == "index":
            count = index_folder(args.folder, database)
            print(f"Indexed {count} image(s). Database total: {database.count()}.")
        else:
            for photo in database.search(args.text, args.date_field, args.start, args.end):
                print(f"{photo.capture_date or photo.modified_date}\t{photo.tags}\t{photo.path}")
    finally:
        database.close()


if __name__ == "__main__":
    main()

