import os
from pathlib import Path
from dotenv import load_dotenv

from interfaces import BookData

load_dotenv()

BASE_DIR = Path(__file__).parent

GOOGLE_BOOK_API = os.getenv("GOOGLE_BOOK_API")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL= "gemini-3.1-flash-lite"
GEMINI_PROMPT = """Analyze the book in the image and respond ONLY with a valid JSON object with exactly these keys, no markdown, no backticks, no explanation:
{
  "title": "exact book title",
  "author": ["author full name"],
  "isbn": "ISBN if visible or null",
  "subtitle": "subtitle if visible or empty string",
  "publisher": "publisher if visible or empty string",
  "published_date": "year or date if visible or empty string",
  "page_count": 0,
  "category": ["genre or category if known or empty array"],
  "description": "brief one sentence description of the book or empty string",
  "cover_url": "a direct URL to a high quality cover image of this book from Google Books or Open Library, or null if unknown"
  "book_url": "a URL to purchase this book on Amazon, Book Depository, or any major book retailer, or null if unknown"
}
If you cannot identify the book respond with all string fields as null and arrays as empty arrays and page_count as 0."""

CAMERA_INDEX = 0
CAMERA_MOBILE_URL = "http://172.25.55.207:4747/video"
CURRENT_CAMERA=CAMERA_MOBILE_URL

YOLO_MODEL_N = BASE_DIR / "models" / "yolo11n.pt"
YOLO_MODEL_S = BASE_DIR / "models" / "yolo11s.pt"
YOLO_MODEL_L = BASE_DIR / "models" / "yolo11l.pt"

USED_MODEL = YOLO_MODEL_L

SAMPLE_BOOK = BookData(
    title="\\[BOOK TITLE]",
    author=["\\[AUTHOR]"],
    isbn="\\[ISBN]",
    category=["\\[CATEGORY(s)]"],
    subtitle="\\[SUBTITLE]",
    publisher="\\[PUBLISHER]",
    published_date="\\[DATE]",
    page_count=0,
    description=("\\[DESCRIPTION]"),
    cover_path="#",
    book_url="\\[BOOKURL]",
)
