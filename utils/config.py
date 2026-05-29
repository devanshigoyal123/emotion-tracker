import os

PROCESS_EVERY_N_FRAMES = 3
MAX_FRAME_SIZE = (640, 480)
CAMERA_FPS = 10
DETECTION_TIMEOUT = 3
MIN_CONFIDENCE_THRESHOLD = 0.5
DATA_DIR = "data"
CSV_COLUMNS = ["timestamp", "emotion", "confidence"]

DEEPFACE_CONFIG = {
    "actions": ["emotion"],
    "enforce_detection": False,
    "detector_backend": "opencv",
    "silent": True
}

UI_CONFIG = {
    "window_title": "Emotion Tracker",
    "window_size": (800, 600),
    "min_window_size": (600, 400)
}
