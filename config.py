import os
from pathlib import Path
from dotenv import load_dotenv

from interfaces import BookData

load_dotenv()

BASE_DIR = Path(__file__).parent

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL= "gemini-3.1-flash-lite"
GEMINI_PROMPT = """You are a book identification assistant. Analyze the book in the image and respond ONLY with a valid JSON object in this exact format, no markdown, no backticks, no explanation:
{"title": "exact book title", "author": "full author name", "isbn": "ISBN if visible or null"}
If you cannot identify the book, respond with:
{"title": null, "author": null, "isbn": null}"""

CAMERA_INDEX = 0
CAMERA_MOBILE_URL = "#"

YOLO_MODEL_N = BASE_DIR / "models" / "yolo11n.pt"
YOLO_MODEL_S = BASE_DIR / "models" / "yolo11s.pt"
YOLO_MODEL_L = BASE_DIR / "models" / "yolo11l.pt"

SAMPLE_BOOK = BookData(
    title="Effective Java",
    author=["Joshua Bloch"],
    isbn="9780134685991",
    category=["Computers", "Programming"],
    subtitle="Third Edition",
    publisher="Addison-Wesley Professional",
    published_date="2018-01-06",
    page_count=412,
    description=(
        "Since this Jolt-award winning classic was last updated in 2008, "
        "the Java programming environment has changed dramatically. Java 7 "
        "and Java 8 introduced new features and idioms that challenge developers."
    ),
    cover_path=BASE_DIR / "outputs" / "content.jpg",
    book_url="https://books.google.com/books?id=BIpDDwAAQBAJ",
)
