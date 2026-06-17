import numpy as np
from dataclasses import dataclass

@dataclass
class AppState:
    current_frame: np.ndarray | None = None 
    is_running: bool = False
    last_result: dict | None = None
