from io import BytesIO
from pathlib import Path

from PIL import Image
from rich import get_console
from textual import work
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Vertical, Horizontal

from config import GOOGLE_BOOK_API
from interfaces import BookData

import requests

try:
    from textual_image.widget import Image as TXImage
    HAS_TX_IMAGE = True
except ImportError:
    HAS_TX_IMAGE = False
    TXImage = None

class BookCard(Static):

    DEFAULT_CSS = """
    BookCard {
        width: 100%;
        height: auto;
        border: round $primary;
        padding: 1 2;
        margin: 1;
        background: transparent;
    }

    BookCard #card-inner {
        height: auto;
    }

    BookCard #cover-col {
        width: 25;
        height: 16;
        margin-right: 2;
        border: solid  $accent;
    }

    BookCard #cover-placeholder {
        width: 25;
        height: 18;
        margin-right: 2;
        content-align: center middle;
        color: $text-muted;
    }

    BookCard #info-col {
        width: 1fr;
        height: auto;
    }

    BookCard #book-title {
        text-style: bold;
        color: $text;
    }

    BookCard #book-subtitle {
        color: $text-muted;
        text-style: italic;
        margin-bottom: 1;
    }

    BookCard #book-author {
        color: $accent;
    }

    BookCard #book-meta {
        color: $text-muted;
        margin-top: 1;
    }

    BookCard #book-description {
        margin-top: 1;
        color: $text;
        width: 100%;
    }

    BookCard #book-isbn {
        color: $text-muted;
        margin-top: 1;
    }
    """

    def __init__(self, book_data: BookData, **kwargs) -> None:
        super().__init__(**kwargs)
        self._book = book_data

    def compose(self) -> ComposeResult:
        info = self._book

        title       = info.title
        subtitle    = info.subtitle
        author_str = "by " + ", ".join(info.author) if info.author else "Author unknown"

        parts: list[str] = []
        
        if publisher := info.publisher:
            parts.append(publisher)
        
        if published := info.published_date:
            parts.append(published[:4])
        
        if pages := info.page_count:
            parts.append(f"{pages} pages")
        
        if info.category:
            parts.append(", ".join(info.category))
        
        meta_str = "  ·  ".join(parts)

        description = info.description
        if len(description) > 280:
            description = description[:280].rsplit(" ", 1)[0] + "…"
        
        if isbn := info.isbn:
            parts.append(isbn)
        
        if bookurl := info.book_url:
            parts.append(bookurl)

        with Horizontal(id="card-inner"):
            if HAS_TX_IMAGE:
                yield TXImage(id="cover-col") # type: ignore[misc]
            else:
                yield Label("📖", id="cover-placeholder")

            with Vertical(id="info-col"):
                yield Label(title,       id="book-title")
                yield Label(subtitle,    id="book-subtitle")
                yield Label(author_str,  id="book-author")
                yield Label(meta_str,    id="book-meta")
                yield Label(description, id="book-description")
                yield Label(f"ISBN: {isbn}" if isbn else "", id="book-isbn")
                yield Label(bookurl if bookurl else "", id="book-url")
    
    def on_mount(self) -> None:

        if self._book.cover_path and HAS_TX_IMAGE:
            self._fetch_cover(self._book.cover_path)

    @work(thread=True)
    def _fetch_cover(self, url: str) -> None:
        if not url or not HAS_TX_IMAGE:
            return
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")  # BytesIO not path
            if TXImage:
                self.app.call_from_thread(
                    self.query_one("#cover-col", TXImage).__setattr__,
                    "image", img,
                )
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Cover error: {e}", severity="error")

    def get_cover_url(self, isbn: str) -> str | None:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={GOOGLE_BOOK_API}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get("totalItems", 0) == 0:
            return None
        
        image_links = data["items"][0]["volumeInfo"].get("imageLinks", {})
        return image_links.get("thumbnail") or image_links.get("smallThumbnail")

    def update_book(self, book_data: BookData) -> None:
        self._book = book_data
        info = book_data
        self.query_one("#book-title", Label).update(info.title or "")
        self.query_one("#book-subtitle", Label).update(info.subtitle or "")
        authors = info.author
        self.query_one("#book-author", Label).update("by " + ", ".join(authors) if authors else "")
        self.query_one("#book-description", Label).update(info.description[:280] if info.description else "")
        self.query_one("#book-url", Label).update(info.book_url or "")
        
        if info.cover_path and info.cover_path != Path(""):
            cover = self.get_cover_url(info.isbn)
            self._fetch_cover(cover)
