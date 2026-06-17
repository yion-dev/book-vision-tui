from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class BookType():
    title: str | None
    author: str | None
    isbn: str | None

@dataclass
class CoordinateType:
    x1: float
    x2: float
    y1: float
    y2: float

@dataclass
class BookData:
    title: str
    author: list[str]
    isbn: str
    subtitle: str = ""
    publisher: str = ""
    published_date: str = ""
    page_count: int = 0
    category: list[str] = field(default_factory=list)
    description: str = ""
    cover_path: Path = Path("")
    book_url: str = ""
