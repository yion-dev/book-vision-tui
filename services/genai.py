import json
import PIL.Image as pil

from pathlib import Path

from google import genai
from google.genai.types import GenerateContentResponse

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_PROMPT
from interfaces import BookType
from state import AppState

class GenAiService:

    def __init__(self, state: AppState) -> None:
        self.state = state
        self.genClient = None
        pass

    def initialize_gemini_client(self) -> genai.Client:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        self.genClient = gemini_client
        return gemini_client

    def get_gemini_response(
            self,
            client: genai.Client,
            image: pil.Image,
            model: str = GEMINI_MODEL,
            prompt: str = GEMINI_PROMPT
    ) -> GenerateContentResponse:
        response = client.models.generate_content(
            model=model,
            contents=[
            prompt,
            image
        ])
        return response

    def format_response(self,content: GenerateContentResponse) -> BookType:
        if not content.text:
            raise ValueError("Gemini Response Content Text is not Valid")
        return json.loads(content.text) 

    def open_image(self, path: Path) -> pil.Image:
        pil_image = pil.open(path)
        return pil_image
