import tkinter as tk
from tkinter import ttk
from datetime import date, datetime, timedelta
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use('TkAgg')
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
from core.data_manager import DataManager

class AnalyticsTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.data_manager = DataManager()
        self.selected_date = date.today()
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(control_frame, text="Select Date:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.date_var = tk.StringVar()
        self.date_combo = ttk.Combobox(control_frame, textvariable=self.date_var, state="readonly", width=15)
        self.date_combo.pack(side=tk.LEFT, padx=5)
        self.date_combo.bind("<<ComboboxSelected>>", self.on_date_selected)
        
        refresh_button = ttk.Button(control_frame, text="Refresh", command=self.load_data)
        refresh_button.pack(side=tk.LEFT, padx=10)
        
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=4, font=("Arial", 10))
        self.stats_text.pack(fill=tk.X)
        
        charts_frame = ttk.Frame(main_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        left_chart_frame = ttk.LabelFrame(charts_frame, text="Emotion Distribution", padding=5)
        left_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_chart_frame = ttk.LabelFrame(charts_frame, text="Emotion Timeline", padding=5)
        right_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.setup_pie_chart(left_chart_frame)
        self.setup_timeline_chart(right_chart_frame)
        
    def setup_pie_chart(self, parent):
        if MATPLOTLIB_AVAILABLE:
            self.pie_fig, self.pie_ax = plt.subplots(figsize=(4, 3))
            self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, parent)
            self.pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            no_chart_label = ttk.Label(parent, text="Pie chart not available\n(matplotlib issue)", 
                                      font=("Arial", 10), justify=tk.CENTER)
            no_chart_label.pack(fill=tk.BOTH, expand=True)
        
    def setup_timeline_chart(self, parent):
        if MATPLOTLIB_AVAILABLE:
            self.timeline_fig, self.timeline_ax = plt.subplots(figsize=(4, 3))
            self.timeline_canvas = FigureCanvasTkAgg(self.timeline_fig, parent)
            self.timeline_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            no_chart_label = ttk.Label(parent, text="Timeline chart not available\n(matplotlib issue)", 
                                      font=("Arial", 10), justify=tk.CENTER)
            no_chart_label.pack(fill=tk.BOTH, expand=True)
        
    def load_data(self):
        available_dates = self.data_manager.get_available_dates()
        
        if available_dates:
            date_strings = [d.strftime('%Y-%m-%d') for d in available_dates]
            self.date_combo['values'] = date_strings
            self.date_combo.set(date_strings[0])
            self.selected_date = available_dates[0]
        else:
            self.date_combo['values'] = [date.today().strftime('%Y-%m-%d')]
            self.date_combo.set(date.today().strftime('%Y-%m-%d'))
            self.selected_date = date.today()
        
        self.update_charts()
        
    def on_date_selected(self, event):
        selected_date_str = self.date_var.get()
        self.selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        self.update_charts()
        
    def update_charts(self):
        stats = self.data_manager.get_emotion_statistics(self.selected_date)
        timeline_data = self.data_manager.get_emotion_timeline(self.selected_date)
        
        self.update_stats_display(stats)
        self.update_pie_chart(stats)
        self.update_timeline_chart(timeline_data)
        
    def update_stats_display(self, stats):
        self.stats_text.delete(1.0, tk.END)
        
        stats_text = f"""Total Records: {stats['total_records']}
Dominant Emotion: {stats['dominant_emotion']}
Average Confidence: {stats['avg_confidence']:.2%}
Date: {self.selected_date.strftime('%Y-%m-%d')}"""
        
        self.stats_text.insert(1.0, stats_text)
        
    def update_pie_chart(self, stats):
        if not MATPLOTLIB_AVAILABLE:
            return
            
        self.pie_ax.clear()
        
        if not stats['emotion_counts']:
            self.pie_ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=self.pie_ax.transAxes)
            self.pie_canvas.draw()
            return
        
        emotions = list(stats['emotion_counts'].keys())
        counts = list(stats['emotion_counts'].values())
        
        colors = plt.cm.Set3(range(len(emotions)))
        wedges, texts, autotexts = self.pie_ax.pie(counts, labels=emotions, autopct='%1.1f%%', colors=colors)
        
        self.pie_ax.set_title('Emotion Distribution')
        self.pie_canvas.draw()
        
    def update_timeline_chart(self, timeline_data):
        if not MATPLOTLIB_AVAILABLE:
            return
            
        self.timeline_ax.clear()
        
        if timeline_data.empty:
            self.timeline_ax.text(0.5, 0.5, 'No timeline data', ha='center', va='center', transform=self.timeline_ax.transAxes)
            self.timeline_canvas.draw()
            return
        
        emotions = timeline_data['emotion'].unique()
        colors = plt.cm.Set3(range(len(emotions)))
        
        for i, emotion in enumerate(emotions):
            emotion_data = timeline_data[timeline_data['emotion'] == emotion]
            self.timeline_ax.plot(emotion_data['time'], emotion_data['count'], 
                               marker='o', label=emotion, color=colors[i], linewidth=2, markersize=4)
        
        self.timeline_ax.set_title('Emotion Timeline')
        self.timeline_ax.set_xlabel('Time')
        self.timeline_ax.set_ylabel('Count')
        self.timeline_ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        self.timeline_ax.tick_params(axis='x', rotation=45)
        
        self.timeline_fig.tight_layout()
        self.timeline_canvas.draw()
