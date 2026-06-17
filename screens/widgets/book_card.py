from pathlib import Path

from PIL import Image
from textual import work
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Vertical, Horizontal

from interfaces import BookData

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
        width: 24;
        height: 18;
        margin-right: 2;
    }

    BookCard #cover-placeholder {
        width: 24;
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
        #self.notify(f"{self._book.cover_path} | {HAS_TX_IMAGE}")

        if self._book.cover_path and HAS_TX_IMAGE:
            self._fetch_cover(self._book.cover_path)

    @work(thread=True)
    def _fetch_cover(self, path: Path) -> None:
        if not path or not HAS_TX_IMAGE:
            return
        try:
            img = Image.open(path).convert("RGB")
            #self.app.call_from_thread(self.notify, f"Image loaded: {img.size}")
            self.app.call_from_thread(
                    self.query_one("#cover-col", TXImage).__setattr__, # type: ignore[misc]
                "image", img,
            )
            #self.app.call_from_thread(self.notify, "Image set on widget")
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Cover error: {e}", severity="error")

    def update_book(self, book_data: BookData) -> None:
        self._book = book_data
        info = book_data

        self.query_one("#book-title",       Label).update(info.title)
        self.query_one("#book-subtitle",    Label).update(info.subtitle)
        authors = info.author
        self.query_one("#book-author",      Label).update("by " + ", ".join(authors) if authors else "")
        self.query_one("#book-description", Label).update(info.description[:280])
        self.query_one("#book-url", Label).update(info.book_url)           

        if info.cover_path and TXImage:
            self._fetch_cover(info.cover_path)
