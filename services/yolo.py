import logging

from numpy import ndarray
from ultralytics import YOLO
from ultralytics.engine.results import Results

from config import USED_MODEL
from interfaces import CoordinateType
from state import AppState

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

class DetectionService:

    def __init__(self, state: AppState) -> None:
        self.model = YOLO(USED_MODEL, verbose=False)
        self.state = state
        pass

    def get_result(self, frame: ndarray) -> list[Results]:
        all_classes = list(self.model.names.keys())
        results: list[Results] = self.model(frame, classes=all_classes[73], verbose=False)

        if not results:
            return []
        
        return results
    
    def get_box_frame(self, results: list[Results]) -> CoordinateType | None:
        boxes = results[0].boxes

        if boxes is None or len(boxes) == 0:
            return None

        for box in boxes:
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            conf = box[0].conf

            logging.debug(f"Current CONFIDENCE --> {conf}")

            if conf > 0.8:
                return CoordinateType(x1,y1,x2,y2)

            return None

    def annotated_frame(self, result: list[Results]) -> ndarray:
        annotated = result[0].plot()
        return annotated
