import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import time

# download model
model_path = "face_landmarker.task"
if not os.path.exists(model_path):
    print("Downloading model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        model_path
    )
    print("Done.")

# setting up detector
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    num_faces=1,
    running_mode=vision.RunningMode.VIDEO  
)
detector = vision.FaceLandmarker.create_from_options(options)

# opens webcam
cap = cv2.VideoCapture(0)

def get_status(result):
    if not result.face_landmarks:
        return "away"

    landmarks = result.face_landmarks[0]

    # nose tip (1) and chin (152) give us vertical head orientation
    nose = landmarks[1]
    chin = landmarks[152]

    vertical_diff = chin.y - nose.y

    if vertical_diff < 0.075:
        return "distracted"  # head tilted down
    return "focused"

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    
    timestamp_ms = int(time.time() * 1000)
    result = detector.detect_for_video(mp_image, timestamp_ms)

    status = get_status(result)

    if result.face_landmarks:
        nose = result.face_landmarks[0][1]
        chin = result.face_landmarks[0][152]
        print(f"vertical_diff: {chin.y - nose.y:.3f}")

    color = (0, 255, 0) if status == "focused" else \
            (0, 165, 255) if status == "distracted" else \
            (0, 0, 255)

    cv2.putText(frame, status, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
    cv2.imshow("Productivity Tracker", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()