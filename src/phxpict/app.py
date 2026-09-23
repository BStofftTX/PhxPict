from __future__ import annotations

import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from .cli import default_database
from .database import Photo, PhotoDatabase
from .indexer import index_folder
from .providers import GracefulFallbackTagProvider, build_tag_provider

BRAND = "MacroStofft"
PAGE_SIZE = 100


class PhxPictApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"PhxPict — {BRAND}")
        self.geometry("1100x720")
        self.minsize(760, 520)
        self.database = PhotoDatabase(default_database())
        self.photos: list[Photo] = []
        self.thumbnail_refs: list[ImageTk.PhotoImage] = []
        self.status = tk.StringVar(value=f"Ready · {self.database.count()} indexed photos · Local-only index")
        self.query = tk.StringVar()
        self.date_field = tk.StringVar(value="capture_date")
        self.start = tk.StringVar()
        self.end = tk.StringVar()
        self.offset = 0
        self.result_count = 0
        self._build()
        self.search()

    def _build(self) -> None:
        header = tk.Frame(self, bg="#102A43", padx=20, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="PhxPict", fg="white", bg="#102A43", font=("Helvetica", 24, "bold")).pack(side="left")
        tk.Label(header, text="Private photo search by MacroStofft", fg="#BCCCDC", bg="#102A43").pack(side="left", padx=14)
        tk.Button(header, text="Index photo folder", command=self.choose_folder, bg="#2CB1BC", fg="white", relief="flat", padx=14, pady=8).pack(side="right")

        filters = ttk.Frame(self, padding=12)
        filters.pack(fill="x")
        ttk.Label(filters, text="Content").grid(row=0, column=0, sticky="w")
        query = ttk.Entry(filters, textvariable=self.query)
        query.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        query.bind("<Return>", lambda _event: self.new_search())
        ttk.Label(filters, text="Date type").grid(row=0, column=1, sticky="w")
        ttk.Combobox(filters, textvariable=self.date_field, values=("capture_date", "modified_date"), state="readonly", width=16).grid(row=1, column=1, padx=4)
        ttk.Label(filters, text="From YYYY-MM-DD").grid(row=0, column=2, sticky="w")
        ttk.Entry(filters, textvariable=self.start, width=14).grid(row=1, column=2, padx=4)
        ttk.Label(filters, text="To YYYY-MM-DD").grid(row=0, column=3, sticky="w")
        ttk.Entry(filters, textvariable=self.end, width=14).grid(row=1, column=3, padx=4)
        ttk.Button(filters, text="Search", command=self.new_search).grid(row=1, column=4, padx=(8, 0))
        filters.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, bg="#F0F4F8", highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.gallery = tk.Frame(self.canvas, bg="#F0F4F8")
        self.gallery.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.gallery, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        footer = ttk.Frame(self, padding=8)
        footer.pack(side="bottom", fill="x")
        ttk.Label(footer, textvariable=self.status, anchor="w").pack(side="left", fill="x", expand=True)
        self.previous_button = ttk.Button(footer, text="Previous", command=self.previous_page)
        self.previous_button.pack(side="right", padx=(8, 0))
        self.next_button = ttk.Button(footer, text="Next", command=self.next_page)
        self.next_button.pack(side="right")

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(title="Choose a photo repository")
        if not selected:
            return
        self.status.set(f"Indexing {selected}…")
        threading.Thread(target=self._index, args=(Path(selected),), daemon=True).start()

    def _index(self, root: Path) -> None:
        worker_database = PhotoDatabase(default_database())
        try:
            provider = build_tag_provider("auto")

            def update_progress(count: int, path: Path) -> None:
                self.after(0, self.status.set, f"Indexed {count}: {path.name}")

            count = index_folder(
                root,
                worker_database,
                provider=provider,
                progress=update_progress,
            )
            total = worker_database.count()
            mode = "local visual + filename tags"
            if isinstance(provider, GracefulFallbackTagProvider) and provider.fallback_reason:
                mode = "filename tags (visual model unavailable)"
            self.after(0, self.status.set, f"Indexed {count} images · {total} total · {mode}")
            self.after(0, self.new_search)
        # Keep the GUI responsive and convert worker failures into a user-facing error.
        except Exception as exc:  # noqa: BLE001
            self.after(0, messagebox.showerror, "Indexing failed", str(exc))
        finally:
            worker_database.close()

    def new_search(self) -> None:
        self.offset = 0
        self.search()

    def search(self) -> None:
        try:
            args = (
                self.query.get(), self.date_field.get(),
                self.start.get() or None, self.end.get() or None,
            )
            self.result_count = self.database.search_count(*args)
            self.photos = self.database.search(*args, limit=PAGE_SIZE, offset=self.offset)
        # Search can cross SQLite, filesystem, and UI boundaries; report failures cleanly.
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Search error", str(exc))
            return
        for child in self.gallery.winfo_children():
            child.destroy()
        self.thumbnail_refs.clear()
        for index, photo in enumerate(self.photos):
            self._photo_card(photo, index // 5, index % 5)
        first = self.offset + 1 if self.result_count else 0
        last = min(self.offset + len(self.photos), self.result_count)
        self.status.set(
            f"Showing {first}-{last} of {self.result_count} matches · "
            f"{self.database.count()} indexed photos · Data stays local"
        )
        self.previous_button.configure(state="normal" if self.offset else "disabled")
        self.next_button.configure(
            state="normal" if self.offset + PAGE_SIZE < self.result_count else "disabled"
        )

    def previous_page(self) -> None:
        self.offset = max(0, self.offset - PAGE_SIZE)
        self.search()
        self.canvas.yview_moveto(0)

    def next_page(self) -> None:
        if self.offset + PAGE_SIZE < self.result_count:
            self.offset += PAGE_SIZE
            self.search()
            self.canvas.yview_moveto(0)

    def _photo_card(self, photo: Photo, row: int, column: int) -> None:
        card = tk.Frame(self.gallery, bg="white", bd=1, relief="solid", padx=8, pady=8)
        card.grid(row=row, column=column, padx=8, pady=8, sticky="n")
        try:
            with Image.open(photo.path) as image:
                image.thumbnail((180, 130))
                thumb = ImageTk.PhotoImage(image.copy())
            self.thumbnail_refs.append(thumb)
            tk.Label(card, image=thumb, bg="white").pack()
        except OSError:
            tk.Label(card, text="Preview unavailable", width=22, height=8, bg="#D9E2EC").pack()
        tk.Label(card, text=photo.filename, bg="white", wraplength=180, font=("Helvetica", 10, "bold")).pack(pady=(6, 2))
        tk.Label(card, text=photo.tags or "untagged", bg="white", fg="#486581", wraplength=180).pack()
        tk.Label(card, text=(photo.capture_date or photo.modified_date)[:10], bg="white", fg="#829AB1").pack()
        def handle_open(_event: object, path: str = photo.path) -> None:
            open_path(path)

        card.bind("<Double-Button-1>", handle_open)
        for child in card.winfo_children():
            child.bind("<Double-Button-1>", handle_open)


def open_path(path: str) -> None:
    if sys.platform == "darwin":
        subprocess.Popen(["open", path])
    elif sys.platform.startswith("win"):
        subprocess.Popen(["explorer", path])
    else:
        subprocess.Popen(["xdg-open", path])


def main() -> None:
    app = PhxPictApp()
    app.mainloop()


if __name__ == "__main__":
    main()
