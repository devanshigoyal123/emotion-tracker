import cv2
import threading
import time
from queue import Queue
from utils.config import CAMERA_FPS, MAX_FRAME_SIZE

class CameraHandler:
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.frame_queue = Queue(maxsize=5)
        self.capture_thread = None
        self.frame_skip_counter = 0
        
    def initialize_camera(self):
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                return False
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, MAX_FRAME_SIZE[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, MAX_FRAME_SIZE[1])
            self.camera.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
            
            return True
        except Exception:
            return False
    
    def start_capture(self):
        if self.camera is None:
            if not self.initialize_camera():
                return False
        
        self.is_running = True
        self.frame_skip_counter = 0
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        return True
    
    def stop_capture(self):
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def _capture_frames(self):
        frame_interval = 1.0 / CAMERA_FPS
        
        while self.is_running:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                
                self.frame_skip_counter += 1
                
                if self.frame_skip_counter % 3 == 0:
                    resized_frame = cv2.resize(frame, MAX_FRAME_SIZE)
                    
                    if not self.frame_queue.full():
                        self.frame_queue.put(resized_frame)
                    else:
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put(resized_frame)
                        except:
                            pass
                
                time.sleep(frame_interval)
                
            except Exception:
                time.sleep(0.1)
                continue
    
    def get_frame(self):
        try:
            return self.frame_queue.get(timeout=0.1)
        except:
            return None
    
    def is_camera_available(self):
        return self.camera is not None and self.camera.isOpened()
    
    def get_frame_count(self):
        return self.frame_skip_counter
