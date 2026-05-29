import os
import csv
import pandas as pd
from datetime import datetime, date
from utils.config import DATA_DIR, CSV_COLUMNS

class DataManager:
    def __init__(self):
        self.data_dir = DATA_DIR
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_today_filename(self):
        today = date.today()
        return os.path.join(self.data_dir, f"emotions_{today.strftime('%Y-%m-%d')}.csv")
    
    def save_emotion_data(self, emotion, confidence):
        filename = self.get_today_filename()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            file_exists = os.path.exists(filename)
            
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                if not file_exists:
                    writer.writerow(CSV_COLUMNS)
                
                writer.writerow([timestamp, emotion, confidence])
                
        except Exception:
            pass
    
    def load_emotion_data(self, target_date=None):
        if target_date is None:
            target_date = date.today()
        
        filename = os.path.join(self.data_dir, f"emotions_{target_date.strftime('%Y-%m-%d')}.csv")
        
        try:
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df
            else:
                return pd.DataFrame(columns=CSV_COLUMNS)
        except Exception:
            return pd.DataFrame(columns=CSV_COLUMNS)
    
    def get_available_dates(self):
        dates = []
        try:
            for filename in os.listdir(self.data_dir):
                if filename.startswith('emotions_') and filename.endswith('.csv'):
                    date_str = filename.replace('emotions_', '').replace('.csv', '')
                    try:
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        dates.append(parsed_date)
                    except ValueError:
                        continue
        except Exception:
            pass
        
        return sorted(dates, reverse=True)
    
    def get_emotion_statistics(self, target_date=None):
        df = self.load_emotion_data(target_date)
        
        if df.empty:
            return {
                'total_records': 0,
                'dominant_emotion': 'None',
                'avg_confidence': 0.0,
                'emotion_counts': {},
                'confidence_by_emotion': {}
            }
        
        emotion_counts = df['emotion'].value_counts().to_dict()
        dominant_emotion = df['emotion'].mode().iloc[0] if not df['emotion'].mode().empty else 'None'
        avg_confidence = df['confidence'].mean()
        
        confidence_by_emotion = df.groupby('emotion')['confidence'].mean().to_dict()
        
        return {
            'total_records': len(df),
            'dominant_emotion': dominant_emotion,
            'avg_confidence': avg_confidence,
            'emotion_counts': emotion_counts,
            'confidence_by_emotion': confidence_by_emotion
        }
    
    def get_emotion_timeline(self, target_date=None):
        df = self.load_emotion_data(target_date)
        
        if df.empty:
            return pd.DataFrame()
        
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        
        timeline = df.groupby(['hour', 'minute', 'emotion']).size().reset_index(name='count')
        timeline['time'] = pd.to_datetime(timeline[['hour', 'minute']].assign(day=1, month=1, year=2024))
        
        return timeline
