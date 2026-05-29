import tkinter as tk
from tkinter import ttk
from ui.monitor_tab import MonitorTab
from ui.analytics_tab import AnalyticsTab
from utils.config import UI_CONFIG

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(UI_CONFIG["window_title"])
        self.root.geometry(f"{UI_CONFIG['window_size'][0]}x{UI_CONFIG['window_size'][1]}")
        self.root.minsize(UI_CONFIG["min_window_size"][0], UI_CONFIG["min_window_size"][1])
        
        self.is_recording = False
        self.setup_ui()
        
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="Control")
        
        self.monitor_tab = MonitorTab(self.notebook)
        self.notebook.add(self.monitor_tab.frame, text="Monitor")
        
        self.analytics_tab = AnalyticsTab(self.notebook)
        self.notebook.add(self.analytics_tab.frame, text="Analytics")
        
        self.setup_control_tab()
        
    def setup_control_tab(self):
        title_label = ttk.Label(self.control_frame, text="Emotion Tracker Control", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        self.status_frame = ttk.Frame(self.control_frame)
        self.status_frame.pack(pady=20)
        
        self.status_label = ttk.Label(self.status_frame, text="Status: Stopped", font=("Arial", 12))
        self.status_label.pack()
        
        self.frames_label = ttk.Label(self.status_frame, text="Frames Processed: 0", font=("Arial", 10))
        self.frames_label.pack(pady=5)
        
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(pady=30)
        
        self.start_button = tk.Button(button_frame, text="START", command=self.start_recording, 
                                     bg="green", fg="white", font=("Arial", 12, "bold"), 
                                     padx=20, pady=10, relief="raised", bd=2)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(button_frame, text="STOP", command=self.stop_recording,
                                    bg="red", fg="white", font=("Arial", 12, "bold"),
                                    padx=20, pady=10, relief="raised", bd=2)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button.config(state=tk.DISABLED)
        
    def start_recording(self):
        self.is_recording = True
        self.status_label.config(text="Status: Recording")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
    def stop_recording(self):
        self.is_recording = False
        self.status_label.config(text="Status: Stopped")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
    def update_frame_count(self, count):
        self.frames_label.config(text=f"Frames Processed: {count}")
        
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        if hasattr(self, 'is_recording') and self.is_recording:
            self.stop_recording()
        self.root.quit()
        self.root.destroy()
