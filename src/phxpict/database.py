from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class Photo:
    path: str
    filename: str
    capture_date: str | None
    modified_date: str
    tags: str
    width: int | None
    height: int | None


class PhotoDatabase:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS photos (
                path TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                capture_date TEXT,
                modified_date TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '',
                width INTEGER,
                height INTEGER,
                indexed_at TEXT NOT NULL
            )
            """
        )
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_capture ON photos(capture_date)")
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_modified ON photos(modified_date)")
        self.connection.commit()

    def upsert(self, photo: Photo) -> None:
        self.connection.execute(
            """INSERT INTO photos(path, filename, capture_date, modified_date, tags, width, height, indexed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(path) DO UPDATE SET
                 filename=excluded.filename, capture_date=excluded.capture_date,
                 modified_date=excluded.modified_date, tags=excluded.tags,
                 width=excluded.width, height=excluded.height, indexed_at=excluded.indexed_at""",
            (*photo.__dict__.values(), datetime.now().isoformat(timespec="seconds")),
        )

    def commit(self) -> None:
        self.connection.commit()

    def search(
        self,
        text: str = "",
        date_field: str = "capture_date",
        start: str | None = None,
        end: str | None = None,
        limit: int = 500,
    ) -> list[Photo]:
        if date_field not in {"capture_date", "modified_date"}:
            raise ValueError("date_field must be capture_date or modified_date")
        clauses, values = [], []
        for token in text.lower().split():
            clauses.append("(lower(filename) LIKE ? OR lower(tags) LIKE ? OR lower(path) LIKE ?)")
            like = f"%{token}%"
            values.extend([like, like, like])
        if start:
            clauses.append(f"{date_field} >= ?")
            values.append(start)
        if end:
            clauses.append(f"{date_field} <= ?")
            values.append(end + "T23:59:59")
        sql = "SELECT path, filename, capture_date, modified_date, tags, width, height FROM photos"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += f" ORDER BY COALESCE(capture_date, modified_date) DESC LIMIT {int(limit)}"
        return [Photo(**dict(row)) for row in self.connection.execute(sql, values)]

    def count(self) -> int:
        return int(self.connection.execute("SELECT COUNT(*) FROM photos").fetchone()[0])

    def close(self) -> None:
        self.connection.close()

