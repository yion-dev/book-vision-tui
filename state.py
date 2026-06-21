from PIL import Image
from google import genai
import numpy as np
from dataclasses import dataclass

from interfaces import BookData, BookType

@dataclass
class AppState:
    last_result: dict | None = None
    
    is_running: bool = False
    current_frame: np.ndarray | None = None 
    annotated_frame: np.ndarray | None = None 
    cropped_frame:  np.ndarray | None = None
    cropped_image: Image.Image | None = None

    genai_client: genai.Client | None = None
    genai_response: BookData | None = None
