from textual.widget import Widget
from textual.app import ComposeResult
from textual.reactive import reactive
from textual_image.widget import Image as TImage
from PIL import Image as PILImage
import numpy as np
import cv2

class CameraView(Widget):
    def compose(self) -> ComposeResult:
        yield TImage(id="camera-image")
    
    def update_frame(self, frame: np.ndarray) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil = PILImage.fromarray(rgb)
        self.query_one("#camera-image", TImage).image = pil
