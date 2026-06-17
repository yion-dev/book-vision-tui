from cv2 import VideoCapture
from textual.containers import Horizontal, Vertical
from textual.events import Key

from config import CAMERA_MOBILE_URL, SAMPLE_BOOK
from screens.widgets.book_card import BookCard
from screens.widgets.scan_history import HistoryTab
from state import AppState

from textual.app import App, ComposeResult
from textual.widgets import Button, Header

from services.cv2 import CameraService
from services.genai import GenAiService
from services.yolo import DetectionService

class Screen(App):

    CSS = """
    
    Screen {
        layout: vertical;
    }
    
    #main-row {
        height: 100%;
    }
 
    BookCard {
        width: 100%;
        height: 50%;
    }
 
    HistoryTab {
        width: 100%;
        height: 40%;
    }

    #button-row Button {
        margin-right: 1;
        min-width: 14;
        border: none;
        height: 3;

    }

    #button-row {
        height: auto;
        width: 100%;
        layout: horizontal;
        align: right middle;
        padding: 0 1;
        border-top: solid $primary-darken-2;
        background: transparent;
    }
    """
 
    TITLE = "Book Scanner"
    SUB_TITLE = "Scan a book or smth"
    THEME = "rose-pine-moon"

    def __init__(
        self,
    ):
        super().__init__()
        self.state = AppState()
        
        self.gemini = GenAiService(self.state)

        self.detection = DetectionService(self.state)
        
        self.camera = CameraService(self.state, self.detection)
        self.capture_camera: VideoCapture | None = None

    def on_mount(self) -> None:
        try:
            self.theme = "rose-pine-moon"

            self.capture_camera = self.camera.open_camera(CAMERA_MOBILE_URL)
            self.camera.start_camera(self.capture_camera)

            history = self.query_one("#HistoryTab", HistoryTab)
            history.add_entry("9780134685991", "Effective Java",  "Joshua Bloch")
            history.add_entry("9780132350884", "Clean Code",      "Robert C. Martin")
        
        except Exception as e:
            self.notify("ERROR: " + str(e), severity="error")

    def on_key(self, event: Key) -> None:
        if event.key == "escape" and self.capture_camera:
            self.camera.release_camera(self.capture_camera)
            self.exit()

    def compose(self) -> ComposeResult:
 
        yield Header()
        
        with Vertical(id="main-row"):
            yield BookCard(SAMPLE_BOOK, id="BookCard")
            yield HistoryTab(id="HistoryTab")
        
            with Horizontal(id="button-row"):
                yield Button("\\[STOP]", id="btn-stop", variant="error")
                yield Button("\\[Export CSV]", id="btn-export", variant="primary")

