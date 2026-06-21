from PIL import Image
import cv2
import queue
import logging
import threading

from numpy import ndarray
from cv2 import COLOR_BGR2RGB, VideoCapture, cvtColor

from services.genai import GenAiService
from state import AppState
from interfaces import CoordinateType
from services.yolo import DetectionService

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

class CameraService:

    def __init__(self, state: AppState, detection: DetectionService, genai: GenAiService) -> None:
        self.state = state
        self.camera = None
        self.detection = detection
        self.genai = genai
        self.thread: threading.Thread | None = None
        self.reader_thread: threading.Thread | None = None
        
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()

    def open_camera(self, camera_index: int | str = 0) -> VideoCapture:
        capture = VideoCapture(camera_index)
        
        if not capture.isOpened():
            raise RuntimeError("cv2 Instance Couldn't Launch")

        self.camera = capture
        
        return capture

    def start_camera(self, capture: VideoCapture):
        
        self.state.is_running = True
        frame_queue = queue.Queue(maxsize=1)      
        
        def reader():
            logging.debug("Reader thread started")
            while self.state.is_running:
                ret, frame = capture.read()
                if ret and not frame_queue.full():
                    frame_queue.put(frame)
            logging.debug("Reader thread exited")
        
        def processor():
            frame_count = 0
            while self.state.is_running:
                try:
                    frame = frame_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                frame_count += 1
                #frame = cv2.flip(frame, 1)
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                self.state.current_frame = frame
                
                if frame_count % 5 == 0:  
                    result = self.detection.get_result(frame)
                    annotated = self.detection.annotated_frame(result)
                    self.state.annotated_frame = annotated
                    box = self.detection.get_box_frame(result)
                    if box is not None and box:
                        self.capture_frame(annotated, box)

                        if self.state.genai_client and self.state.cropped_image:
                            response = self.genai.get_gemini_response(self.state.genai_client,self.state.cropped_image)
                            formatted = self.genai.format_response(response)
                            self.state.genai_response = formatted

            logging.debug("Processor thread exited")
            capture.release()
        
        self.reader_thread = threading.Thread(target=reader, daemon=True)
        self.thread = threading.Thread(target=processor, daemon=True)
        
        self.reader_thread.start()
        self.thread.start()

    def capture_frame(self, frame: ndarray, coord: CoordinateType) -> None:
        self.state.is_running = False
    
        h, w = frame.shape[:2]
        x1 = max(0, int(coord.x1))
        y1 = max(0, int(coord.y1))
        x2 = min(w, int(coord.x2))
        y2 = min(h, int(coord.y2))
        
        if x2 <= x1 or y2 <= y1:
            logging.debug(f"Invalid crop coords: {x1},{y1},{x2},{y2}")
            return None
        
        cropped = frame[y1:y2, x1:x2]
        self.state.cropped_frame = cropped

        rgb = cvtColor(cropped, COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)
        self.state.cropped_image = pil_image
     
    def release_camera(self):
        logging.debug(f"release_camera called, is_running={self.state.is_running}")
        self.state.is_running = False
        self.state.cropped_frame = None
        logging.debug(f"reader alive: {self.reader_thread and self.reader_thread.is_alive()}")
        logging.debug(f"processor alive: {self.thread and self.thread.is_alive()}")

    def _display_loop(self):
        cv2.namedWindow("Book Scanner", cv2.WINDOW_NORMAL)
        while True:
            if self.state.cropped_frame is not None:
                cv2.imshow("Book Scanner", self.state.cropped_frame)
            elif self.state.current_frame is not None and self.state.is_running:
                cv2.imshow("Book Scanner", self.state.current_frame)
            cv2.waitKey(1)
