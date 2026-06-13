import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

# download the model if it doesn't exist
model_path = "blaze_face_short_range.tflite"
if not os.path.exists(model_path):
    print("Downloading model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite",
        model_path
    )
    print("Done.")

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceDetectorOptions(base_options=base_options, min_detection_confidence=0.5)
detector = vision.FaceDetector.create_from_options(options)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = detector.detect(mp_image)

    status = "focused" if result.detections else "away"
    cv2.putText(frame, status, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                (0, 255, 0) if status == "focused" else (0, 0, 255), 2)
    cv2.imshow("Productivity Tracker", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()