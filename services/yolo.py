from numpy import ndarray
from ultralytics import YOLO
from ultralytics.engine.results import Results

from config import YOLO_MODEL_N
from state import AppState

class DetectionService:

    def __init__(self, state: AppState) -> None:
        self.model = YOLO(YOLO_MODEL_N, verbose=False)
        self.state = state
        pass

    def get_result(self, frame: ndarray) -> list[Results]:
        all_classes = list(self.model.names.keys())
        results: list[Results] = self.model(frame, classes=all_classes[0], verbose=False)

        if not results:
            return []
        
        return results

    def annotated_frame(self, result: list[Results]) -> ndarray:
        annotated = result[0].plot()
        return annotated
