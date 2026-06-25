from cv2 import VideoCapture
from google.genai._interactions.types.error_event import Error
from textual.containers import Horizontal, Vertical
from textual.events import Key

from config import CURRENT_CAMERA, SAMPLE_BOOK
from screens.widgets.book_card import BookCard
from screens.widgets.scan_history import HistoryTab
from state import AppState

from textual.app import App, ComposeResult
from textual.widgets import Button, Header, LoadingIndicator

from services.cv2 import CameraService
from services.genai import GenAiService
from services.yolo import DetectionService

class Screen(App):

    CSS = """
        Screen {
            layout: vertical;
        }
        
        #main-row {
            height: 1fr;
        }
        
        #left-panel {
            width: 50%;
            height: 100%;
        }
        
        #right-panel {
            width: 50%;
            height: 100%;
        }

        CameraView {
            width: 100%;
            height: 1fr;
        }

        BookCard {
            width: 100%;
            height: 50%;
        }

        HistoryTab {
            width: 100%;
            height: 1fr;
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

        #button-row Button {
            margin-right: 1;
            min-width: 14;
            border: none;
            height: 3;
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
        
        self.camera = CameraService(self.state, self.detection, self.gemini)
        self.capture_camera: VideoCapture | None = None

    def on_mount(self) -> None:
        try:

            self.query_one("#loading", LoadingIndicator).display = False
            self.set_interval(1, self.check_result)
            self.theme = "rose-pine-moon"

            client = self.gemini.initialize_gemini_client()
            self.capture_camera = self.camera.open_camera(CURRENT_CAMERA)
            self.state.genai_client = client

        except Exception as e:
            self.notify("ERROR: " + str(e), severity="error")

    def on_key(self, event: Key) -> None:
        if event.key == "escape" and self.capture_camera:
            self.camera.release_camera()
            self.exit()

    def check_result(self):
        if self.state.genai_response:
            book = self.state.genai_response
            self.query_one(BookCard).update_book(book)
            self.query_one(HistoryTab).add_entry(
                isbn=book.isbn or "",
                title=book.title or "",
                author=", ".join(book.author) if book.author else ""
            )

            self.query_one(BookCard).display = True
            self.query_one(LoadingIndicator).display = False
            
            self.state.genai_response = None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        try:
            match event.button.id:
                case "btn-stop":
                    self.camera.release_camera()
                    self.capture_camera = None
                    self.notify("Stopped")

                case "btn-scan":
                    self.query_one(BookCard).display = False
                    self.query_one(LoadingIndicator).display = True

                    if self.capture_camera:
                        self.camera.release_camera()
                        self.capture_camera = None

                    self.capture_camera = self.camera.open_camera(CURRENT_CAMERA)
                    self.camera.start_camera(self.capture_camera)
                    self.notify("Scanning...")
        except Exception as e:
            self.notify(f"Error Occured: {e}", severity="error")
            self.query_one(LoadingIndicator).display = False
            self.query_one(BookCard).display = True

    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Vertical(id="main-row"):
            yield LoadingIndicator(id="loading")
            yield BookCard(SAMPLE_BOOK, id="BookCard")
            yield HistoryTab(id="HistoryTab")
            
            with Horizontal(id="button-row"):
                yield Button("\\[STOP]", id="btn-stop", variant="error")
                yield Button("\\[SCAN BOOK]", id="btn-scan", variant="primary")
