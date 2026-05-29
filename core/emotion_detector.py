import cv2
import threading
import time
from deepface import DeepFace
from utils.config import DEEPFACE_CONFIG, DETECTION_TIMEOUT, MIN_CONFIDENCE_THRESHOLD

class EmotionDetector:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmotionDetector, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.model_loaded = False
            self._initialized = True
    
    def load_model(self):
        if not self.model_loaded:
            try:
                test_frame = cv2.imread("test.jpg") if cv2.imread("test.jpg") is not None else None
                if test_frame is None:
                    test_frame = cv2.zeros((100, 100, 3), dtype=cv2.uint8)
                
                DeepFace.analyze(test_frame, **DEEPFACE_CONFIG)
                self.model_loaded = True
            except Exception:
                pass
    
    def detect_emotion(self, frame):
        if not self.model_loaded:
            self.load_model()
        
        if frame is None:
            return None, 0.0
        
        try:
            start_time = time.time()
            
            result = DeepFace.analyze(frame, **DEEPFACE_CONFIG)
            
            if time.time() - start_time > DETECTION_TIMEOUT:
                return None, 0.0
            
            if isinstance(result, list):
                result = result[0]
            
            emotions = result.get('emotion', {})
            if not emotions:
                return None, 0.0
            
            dominant_emotion = max(emotions, key=emotions.get)
            confidence = emotions[dominant_emotion] / 100.0
            
            if confidence < MIN_CONFIDENCE_THRESHOLD:
                return "uncertain", confidence
            
            return dominant_emotion, confidence
            
        except Exception:
            return None, 0.0
    
    def is_model_ready(self):
        return self.model_loaded
