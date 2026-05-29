import tkinter as tk
from tkinter import ttk
from collections import Counter
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use('TkAgg')
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class MonitorTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.current_emotion = "None"
        self.current_confidence = 0.0
        self.session_emotions = []
        self.session_start_time = None
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        emotion_frame = ttk.Frame(main_frame)
        emotion_frame.pack(fill=tk.X, pady=20)
        
        self.emotion_label = ttk.Label(emotion_frame, text="None", font=("Arial", 48, "bold"))
        self.emotion_label.pack()
        
        self.confidence_label = ttk.Label(emotion_frame, text="Confidence: 0%", font=("Arial", 14))
        self.confidence_label.pack(pady=10)
        
        self.confidence_bar = ttk.Progressbar(emotion_frame, length=300, mode='determinate')
        self.confidence_bar.pack(pady=10)
        
        session_frame = ttk.LabelFrame(main_frame, text="Session Statistics", padding=10)
        session_frame.pack(fill=tk.X, pady=20)
        
        self.session_duration_label = ttk.Label(session_frame, text="Duration: 00:00:00", font=("Arial", 12))
        self.session_duration_label.pack(anchor=tk.W)
        
        self.total_detections_label = ttk.Label(session_frame, text="Total Detections: 0", font=("Arial", 12))
        self.total_detections_label.pack(anchor=tk.W)
        
        chart_frame = ttk.LabelFrame(main_frame, text="Top Emotions This Session", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self.setup_chart(chart_frame)
        
    def setup_chart(self, parent):
        if MATPLOTLIB_AVAILABLE:
            self.fig, self.ax = plt.subplots(figsize=(6, 4))
            self.canvas = FigureCanvasTkAgg(self.fig, parent)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.update_chart()
        else:
            no_chart_label = ttk.Label(parent, text="Charts not available\n(matplotlib issue)", 
                                      font=("Arial", 12), justify=tk.CENTER)
            no_chart_label.pack(fill=tk.BOTH, expand=True)
        
    def update_emotion(self, emotion, confidence):
        self.current_emotion = emotion
        self.current_confidence = confidence
        
        self.emotion_label.config(text=emotion.title())
        self.confidence_label.config(text=f"Confidence: {confidence:.1%}")
        self.confidence_bar['value'] = confidence * 100
        
        if emotion != "None" and emotion != "uncertain":
            self.session_emotions.append(emotion)
            self.update_session_stats()
            self.update_chart()
            
    def update_session_stats(self):
        total_detections = len(self.session_emotions)
        self.total_detections_label.config(text=f"Total Detections: {total_detections}")
        
    def update_chart(self):
        if not MATPLOTLIB_AVAILABLE:
            return
            
        self.ax.clear()
        
        if not self.session_emotions:
            self.ax.text(0.5, 0.5, 'No emotions detected yet', ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        emotion_counts = Counter(self.session_emotions)
        top_emotions = emotion_counts.most_common(5)
        
        emotions = [item[0] for item in top_emotions]
        counts = [item[1] for item in top_emotions]
        
        bars = self.ax.bar(emotions, counts)
        self.ax.set_title('Top Emotions This Session')
        self.ax.set_xlabel('Emotion')
        self.ax.set_ylabel('Count')
        
        for bar, count in zip(bars, counts):
            self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        str(count), ha='center', va='bottom')
        
        plt.setp(self.ax.get_xticklabels(), rotation=45)
        self.fig.tight_layout()
        self.canvas.draw()
        
    def reset_session(self):
        self.session_emotions = []
        self.session_start_time = None
        self.update_session_stats()
        self.update_chart()
