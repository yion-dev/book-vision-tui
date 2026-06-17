import cv2
import threading

from PIL import Image
from numpy import ndarray
from cv2 import VideoCapture, cvtColor, COLOR_BGR2RGB

from interfaces import CoordinateType
from services.yolo import DetectionService
from state import AppState

class CameraService:

    def __init__(self, state: AppState, detection: DetectionService) -> None:
        self.state = state
        self.camera = None
        self.detection = detection
        pass

    def open_camera(self, camera_index: int | str = 0) -> VideoCapture:
        capture = VideoCapture(camera_index)
        
        if not capture.isOpened():
            raise RuntimeError("cv2 Instance Couldn't Launch")

        self.camera = capture
        
        return capture

    def _camera_loop(self, capture: VideoCapture):
        while True:
            ret, frame = capture.read()

            if not ret:
                break

            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame = cv2.flip(frame, 1)
            
            self.state.current_frame = frame
            
            result = self.detection.get_result(frame)
            
            annotated = self.detection.annotated_frame(result)
            
            cv2.namedWindow("Recording", cv2.WINDOW_NORMAL)
            cv2.imshow("Recording", annotated)

            cv2.waitKey(1)
    
    def start_camera(self, capture: VideoCapture):
        thread = threading.Thread(target=self._camera_loop, args=(capture,), daemon=True)
        thread.start()

    def capture_frame(self, frame: ndarray, coord: CoordinateType) -> Image.Image:
        cropped = frame[coord.y1:coord.y2, coord.x1:coord.x2]
        processed_frame = cvtColor(cropped, COLOR_BGR2RGB)
        pil_image = Image.fromarray(processed_frame)
        return pil_image
     
    def release_camera(self, capture: VideoCapture):
        capture.release()
        cv2.destroyAllWindows()
