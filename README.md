
## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/DeepPythonist/EmotionTracker.git
   cd EmotionTracker
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Control Tab
- Click **START** to begin emotion detection
- Click **STOP** to stop recording
- Monitor status and frame count

### Monitor Tab
- View current detected emotion in large text
- See confidence level with progress bar
- Track session statistics and top emotions

### Analytics Tab
- Select date from dropdown to view historical data
- View emotion distribution pie chart (if matplotlib available)
- Review summary statistics
- Monitor current session emotions



## Performance Optimization

The application implements several optimization techniques:

- Processes every 3rd frame (not every frame)
- Uses `enforce_detection=False` for better edge case handling
- Implements frame skipping when processing takes >100ms
- Resizes frames to 640x480 before processing
- Caches DeepFace model on first load
- Uses threading to separate UI from processing



## Project Structure

```
EmoNet/
├── main.py                    # Main application
├── requirements.txt           # Dependencies
├── README.txt                # Installation guide
├── PRIVACY.txt               # Privacy policy
├── LICENSE.txt               # MIT License
├── core/                     # Core modules
│   ├── camera_handler.py
│   ├── emotion_detector.py
│   └── data_manager.py
├── ui/                       # UI components
│   ├── main_window.py
│   ├── monitor_tab.py
│   └── analytics_tab.py
├── utils/                    # Utility modules
│   └── config.py
└── data/                     # Data storage folder
```

## Technical Details

- **CPU Usage**: <15% on modern i5 processors
- **RAM Usage**: <500MB
- **Detection Latency**: <2 seconds per processed frame
- **UI Responsiveness**: No freezing during processing

## Dependencies

- deepface==0.0.79
- opencv-python==4.8.1.78
- pandas>=2.0.0,<2.2.0
- matplotlib>=3.7.0,<3.9.0
- seaborn>=0.12.0,<0.14.0
- pillow>=9.0.0,<11.0.0
- tensorflow>=2.13.0,<2.16.0
- numpy>=1.21.0,<2.0.0

## Support

If you have any issues:
- Email: devanshig35#gmail.com  














Project ka idea:
“Mam, maine ek real-time emotion detection project banaya hai. Isme webcam open hota hai, system face detect karta hai, phir DeepFace library ke through face ka emotion analyze karta hai. Emotion face ke upar label ke form me show hota hai, jaise Happy, Sad, Angry, Surprise, Neutral.”

Code ka flow:

Sabse pehle TensorFlow warnings hide ki
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

Iska use unnecessary TensorFlow warning messages ko terminal me hide karne ke liye kiya.

Libraries import ki
import cv2
from deepface import DeepFace

cv2 webcam open karne, face box draw karne aur video window show karne ke liye use hoti hai.
DeepFace face ka emotion detect karne ke liye use hoti hai.

Webcam open kiya
cap = cv2.VideoCapture(0)

0 ka matlab default laptop camera. Agar external camera hota, toh kabhi-kabhi 1 use hota.

Camera check kiya
if not cap.isOpened():
    print("Camera not found")
    exit()

Agar camera open nahi hota toh program error dene ke bajaye safely stop ho jata hai.

Face detector load kiya
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

Ye OpenCV ka pre-trained face detection model hai. Isse camera frame me face locate hota hai.

Emotion labels define kiye
emotion_map = {
    "happy": "Happy 😊",
    "sad": "Sad 😔",
    "angry": "Angry 😠",
    "surprise": "Surprise 😮",
    "neutral": "Neutral 😐"
}

DeepFace jo raw emotion name deta hai, usko readable label me convert kiya.

Main loop chalaya
while True:

Ye loop continuously webcam se frame read karta hai. Iski wajah se real-time video chalti rehti hai.

Frame read aur mirror kiya
ret, frame = cap.read()
frame = cv2.flip(frame, 1)

cap.read() camera se current frame leta hai.
cv2.flip(frame, 1) video ko mirror jaisa banata hai, jaise selfie camera.

Frame ko grayscale me convert kiya
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

Face detection grayscale image par fast aur better hoti hai.

Face detect kiya
faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.2,
    minNeighbors=5,
    minSize=(80, 80)
)

Ye function image me face search karta hai aur face ka position deta hai: x, y, width, height.

Face ke around rectangle banaya
cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

Isse detected face ke around green box show hota hai.

DeepFace se emotion analyze kiya
result = DeepFace.analyze(
    face_img,
    actions=["emotion"],
    enforce_detection=False
)

Yahan cropped face image DeepFace ko di gayi.
actions=["emotion"] ka matlab sirf emotion detect karna hai.
enforce_detection=False se program crash nahi hota agar face thoda unclear ho.

Dominant emotion nikala
emotion = data.get("dominant_emotion", "neutral")

DeepFace multiple emotions ka score deta hai, lekin sabse strong emotion ko dominant_emotion bolta hai.

Face ke upar emotion text show kiya
cv2.putText(
    frame,
    label,
    (x, y - 15),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0, 255, 0),
    2
)

Isse face box ke upar emotion label show hota hai.

Video window show ki
cv2.imshow("Real Time Emotion Tracker", frame)

Ye final output window open karta hai.

Q press karne par app close hoti hai
if cv2.waitKey(1) & 0xFF == ord("q"):
    break

User q press kare toh loop stop ho jata hai.

Camera release kiya
cap.release()
cv2.destroyAllWindows()

Program close hone ke baad camera free ho jata hai aur window close ho jati hai.
