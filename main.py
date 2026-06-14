import cv2
import mediapipe as mp
import time

from tracker import build_detector, get_status, open_webcam, draw_status
from database import init_db, log_session

# main function to run tracker
def main():
    conn = init_db()
    detector = build_detector()
    cap = open_webcam()

    current_state = None
    state_start_time = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int(time.time() * 1000)
        result = detector.detect_for_video(mp_image, timestamp_ms)

        status = get_status(result)

        # log session whenever state changes
        if status != current_state:
            now = time.time()
            if current_state is not None:
                log_session(conn, state_start_time, now, current_state)
            current_state = status
            state_start_time = now

        draw_status(frame, status)
        cv2.imshow("Productivity Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # log the final session on quit
    if current_state is not None:
        log_session(conn, state_start_time, time.time(), current_state)

    cap.release()
    cv2.destroyAllWindows()
    conn.close()


if __name__ == "__main__":
    main()
