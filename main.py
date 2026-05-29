#!/usr/bin/env python3

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

import cv2
from deepface import DeepFace
from PIL import Image, ImageTk

VALID_EXPRESSIONS = {'happy', 'sad', 'angry', 'surprise', 'neutral'}
FRAME_ANALYSIS_INTERVAL = 10
WINDOW_WIDTH = 980
WINDOW_HEIGHT = 640


class EmotionTrackerMain:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Emotion Tracker')
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        self.root.configure(bg='#f8fafc')
        self.root.resizable(False, False)

        self.camera = None
        self.video_panel = None
        self.analysis_thread = None
        self.analysis_lock = threading.Lock()
        self.running = False
        self.frame_counter = 0
        self.latest_label = 'Starting...'
        self.latest_confidence = 0.0
        self.latest_bbox = None

        self.setup_ui()
        self.open_camera()

    def setup_ui(self):
        header_frame = ttk.Frame(self.root, padding=(20, 16, 20, 10))
        header_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            header_frame,
            text='Emotion Tracker',
            font=('Segoe UI', 24, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        status_label = ttk.Label(
            header_frame,
            text='Live webcam emotion detection',
            font=('Segoe UI', 10),
            foreground='#555'
        )
        status_label.pack(side=tk.RIGHT)

        content_frame = ttk.Frame(self.root, padding=(20, 0, 20, 20))
        content_frame.pack(fill=tk.BOTH, expand=True)

        video_frame = ttk.Frame(content_frame, relief=tk.RIDGE, borderwidth=1)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        self.video_panel = tk.Label(video_frame, bg='black')
        self.video_panel.pack(fill=tk.BOTH, expand=True)

        info_frame = ttk.Frame(content_frame, width=300)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        info_title = ttk.Label(
            info_frame,
            text='Current Status',
            font=('Segoe UI', 16, 'bold')
        )
        info_title.pack(anchor=tk.W, pady=(0, 12))

        self.emotion_text = ttk.Label(
            info_frame,
            text='Emotion: Starting...',
            font=('Segoe UI', 14)
        )
        self.emotion_text.pack(anchor=tk.W, pady=(0, 12))

        self.confidence_text = ttk.Label(
            info_frame,
            text='Confidence: 0%',
            font=('Segoe UI', 14)
        )
        self.confidence_text.pack(anchor=tk.W, pady=(0, 12))

        self.frame_text = ttk.Label(
            info_frame,
            text='Frames processed: 0',
            font=('Segoe UI', 12)
        )
        self.frame_text.pack(anchor=tk.W, pady=(0, 12))

        self.camera_status = ttk.Label(
            info_frame,
            text='Camera: initializing...',
            font=('Segoe UI', 12)
        )
        self.camera_status.pack(anchor=tk.W, pady=(0, 12))

        instruction_label = ttk.Label(
            info_frame,
            text='Smiling will display Happy 😊 clearly above the face.',
            font=('Segoe UI', 10),
            foreground='#444',
            wraplength=280,
            justify=tk.LEFT
        )
        instruction_label.pack(anchor=tk.W, pady=(12, 0))

    def open_camera(self):
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.camera.isOpened():
            self.show_camera_error('Unable to open the webcam. Please connect a camera and restart the app.')
            return

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.running = True
        self.camera_status.config(text='Camera: live')
        self.root.after(20, self.video_loop)

    def show_camera_error(self, message):
        messagebox.showerror('Camera error', message)
        self.root.destroy()

    def video_loop(self):
        if not self.running:
            return

        ret, frame = self.camera.read()
        if not ret:
            self.camera_status.config(text='Camera: disconnected')
            self.root.after(200, self.video_loop)
            return

        frame = cv2.flip(frame, 1)
        self.frame_counter += 1

        if self.frame_counter % FRAME_ANALYSIS_INTERVAL == 0:
            if self.analysis_thread is None or not self.analysis_thread.is_alive():
                frame_for_analysis = frame.copy()
                self.analysis_thread = threading.Thread(
                    target=self.analyze_frame,
                    args=(frame_for_analysis,),
                    daemon=True
                )
                self.analysis_thread.start()

        display_frame = self.draw_overlay(frame)
        self.update_stats()

        image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        self.video_panel.configure(image=image)
        self.video_panel.image = image

        self.root.after(20, self.video_loop)

    def analyze_frame(self, frame):
        try:
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )

            if isinstance(result, list):
                result = result[0]

            emotions = result.get('emotion', {}) or {}
            dominant_emotion = result.get('dominant_emotion') or ''
            if not dominant_emotion and emotions:
                dominant_emotion = max(emotions, key=emotions.get)

            dominant_emotion = self.normalize_expression(dominant_emotion)
            confidence = 0.0
            if dominant_emotion in emotions:
                confidence = float(emotions.get(dominant_emotion, 0.0)) / 100.0
            else:
                confidence = max((float(v) for v in emotions.values()), default=0.0) / 100.0

            if dominant_emotion == 'happy':
                display_label = 'Happy 😊'
            else:
                display_label = dominant_emotion.title()

            region = result.get('region') or {}
            face_box = None
            if region:
                x = int(region.get('x', 0))
                y = int(region.get('y', 0))
                w = int(region.get('w', 0))
                h = int(region.get('h', 0))
                if w > 0 and h > 0:
                    face_box = (x, y, x + w, y + h)

            self.latest_label = display_label
            self.latest_confidence = confidence
            self.latest_bbox = face_box

        except Exception:
            self.latest_label = 'No face detected'
            self.latest_confidence = 0.0
            self.latest_bbox = None

    def normalize_expression(self, emotion):
        if not isinstance(emotion, str):
            return 'neutral'

        expression = emotion.strip().lower()
        if expression in VALID_EXPRESSIONS:
            return expression
        if expression in {'fear', 'disgust', 'contempt'}:
            return 'neutral'
        return 'neutral'

    def draw_overlay(self, frame):
        display_frame = frame.copy()

        if self.latest_bbox:
            x1, y1, x2, y2 = self.latest_bbox
            x1 = max(0, min(x1, display_frame.shape[1] - 1))
            y1 = max(0, min(y1, display_frame.shape[0] - 1))
            x2 = max(0, min(x2, display_frame.shape[1] - 1))
            y2 = max(0, min(y2, display_frame.shape[0] - 1))

            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label_text = f"{self.latest_label} • {self.latest_confidence * 100:.0f}%" if self.latest_confidence > 0 else self.latest_label
            text_y = y1 - 10 if y1 - 10 > 20 else y1 + 25
            cv2.putText(
                display_frame,
                label_text,
                (x1, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )
        else:
            cv2.putText(
                display_frame,
                self.latest_label,
                (16, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

        return display_frame

    def update_stats(self):
        self.emotion_text.config(text=f'Emotion: {self.latest_label}')
        self.confidence_text.config(text=f'Confidence: {self.latest_confidence * 100:.0f}%')
        self.frame_text.config(text=f'Frames processed: {self.frame_counter}')

    def on_closing(self):
        self.running = False
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.root.destroy()

    def run(self):
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.root.mainloop()


def main():
    app = EmotionTrackerMain()
    app.run()


if __name__ == '__main__':
    main()
