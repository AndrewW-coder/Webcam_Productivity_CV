import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

MODEL_PATH = "models/face_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

# tilt threshold for distracted state
GAZE_THRESHOLD = 0.075  

# download model if doesn't exist
def download_model(): 
    if not os.path.exists(MODEL_PATH):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        print("Downloading model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Done.")

# build face detector
def build_detector():
    download_model()
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        num_faces=1,
        running_mode=vision.RunningMode.VIDEO,
        min_face_detection_confidence=0.3,  
        min_face_presence_confidence=0.3,   
        min_tracking_confidence=0.3     
    )
    return vision.FaceLandmarker.create_from_options(options)

# get the status of the user based on the face landmarks
def get_status(result):
    if not result.face_landmarks:
        return "away"

    landmarks = result.face_landmarks[0]
    nose = landmarks[1]
    chin = landmarks[152]
    vertical_diff = chin.y - nose.y

    if vertical_diff < GAZE_THRESHOLD:
        return "distracted"
    return "focused"


# get the color of the frame based on the status
def get_frame_color(status):
    return (0, 255, 0) if status == "focused" else \
           (0, 165, 255) if status == "distracted" else \
           (0, 0, 255)


def open_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")
    return cap


def draw_status(frame, status):
    color = get_frame_color(status)
    cv2.putText(frame, status, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)