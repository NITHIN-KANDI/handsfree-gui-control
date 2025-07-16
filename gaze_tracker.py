import cv2
import numpy as np
import mediapipe as mp
import pyautogui
from collections import deque
import time
from scipy.spatial import distance as dist
from sklearn.neighbors import KNeighborsClassifier
import threading

class GazeTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1,
                                                          min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.screen_w, self.screen_h = pyautogui.size()
        self.center_x, self.center_y = self.screen_w // 2, self.screen_h // 2
        self.calibration_points = {}
        self.calibration_data = {'features': [], 'labels': []}
        self.gaze_classifier = None
        self.gaze_history = deque(maxlen=10)
        self.position_history = deque(maxlen=10)
        self.ema_dx = None
        self.ema_dy = None
        self.current_gaze_zone = "Center"
        self.running = False

        self.latest_dx = 0.0
        self.latest_dy = 0.0
        self.blink_timestamps = deque(maxlen=2)
        self.blink_triggered = False

    def get_eye_info(self, face_landmarks, w, h):
        try:
            left_eye = np.array([(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h)
                                 for i in [33, 133, 160, 144, 158, 153]])
            right_eye = np.array([(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h)
                                  for i in [362, 263, 387, 373, 380, 374]])
            left_center = left_eye.mean(axis=0)
            right_center = right_eye.mean(axis=0)

            left_iris = face_landmarks.landmark[468]
            right_iris = face_landmarks.landmark[473]

            eye_center = ((left_center[0] + right_center[0]) / 2, (left_center[1] + right_center[1]) / 2)
            iris_center = ((left_iris.x + right_iris.x) / 2 * w, (left_iris.y + right_iris.y) / 2 * h)
            eye_width = dist.euclidean(left_eye[0], right_eye[0])
            return eye_center, iris_center, eye_width
        except:
            return None, None, None

    def get_blink_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def calibrate_point(self, name, key_char='c', num_frames=25):
        print(f"Calibrating: {name}")
        features, labels = [], []
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    ec, ic, ew = self.get_eye_info(face_landmarks, w, h)
                    if ec and ic and ew > 30:
                        dx = (ic[0] - ec[0]) / ew
                        dy = (ic[1] - ec[1]) / ew
                        features.append([dx, dy])
                        labels.append(name)
                        if len(features) >= num_frames:
                            avg_dx = np.mean([f[0] for f in features])
                            avg_dy = np.mean([f[1] for f in features])
                            self.calibration_points[name] = (ec, ic, avg_dx, avg_dy, ew)
                            self.calibration_data['features'].extend(features)
                            self.calibration_data['labels'].extend(labels)
                            print(f"[{name}] Calibrated with dx={avg_dx:.3f}, dy={avg_dy:.3f}")
                            return

            cv2.putText(frame, f"Look at {name} and press '{key_char.upper()}'", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
            cv2.imshow("Calibration", frame)
            if cv2.waitKey(1) & 0xFF == ord(key_char):
                continue

    def train(self):
        if len(self.calibration_data['features']) > 5:
            self.gaze_classifier = KNeighborsClassifier(n_neighbors=3)
            self.gaze_classifier.fit(self.calibration_data['features'], self.calibration_data['labels'])

    def get_smoothed(self, dx, dy):
        self.gaze_history.append((dx, dy))
        if len(self.gaze_history) < 3:
            return dx, dy
        sma_dx = np.mean([x for x, _ in self.gaze_history])
        sma_dy = np.mean([y for _, y in self.gaze_history])
        if self.ema_dx is None:
            self.ema_dx, self.ema_dy = dx, dy
        else:
            self.ema_dx = 0.3 * dx + 0.7 * self.ema_dx
            self.ema_dy = 0.3 * dy + 0.7 * self.ema_dy
        return 0.5 * self.ema_dx + 0.3 * sma_dx + 0.2 * dx, 0.5 * self.ema_dy + 0.3 * sma_dy + 0.2 * dy

    def track_loop(self):
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            h, w, _ = frame.shape
            results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    ec, ic, ew = self.get_eye_info(face_landmarks, w, h)
                    if ec is None or ew < 30:
                        continue
                    dx = (ic[0] - ec[0]) / ew
                    dy = (ic[1] - ec[1]) / ew
                    sm_dx, sm_dy = self.get_smoothed(dx, dy)

                    self.latest_dx = sm_dx
                    self.latest_dy = sm_dy

                    # Blink detection
                    left_eye = [(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h)
                                for i in [33, 160, 158, 133, 153, 144]]
                    right_eye = [(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h)
                                 for i in [362, 387, 380, 263, 373, 374]]
                    left_ear = self.get_blink_ratio(left_eye)
                    right_ear = self.get_blink_ratio(right_eye)
                    avg_ear = (left_ear + right_ear) / 2.0

                    BLINK_THRESHOLD = 0.21
                    now = time.time()
                    if avg_ear < BLINK_THRESHOLD:
                        if not self.blink_timestamps or now - self.blink_timestamps[-1] > 0.3:
                            self.blink_timestamps.append(now)

                        if len(self.blink_timestamps) == 2 and self.blink_timestamps[-1] - self.blink_timestamps[0] < 1.0:
                            self.blink_timestamps.clear()
                            self.blink_triggered = True

                    if self.gaze_classifier:
                        self.current_gaze_zone = self.gaze_classifier.predict([[sm_dx, sm_dy]])[0]

    def consume_blink_trigger(self):
        if self.blink_triggered:
            self.blink_triggered = False
            return True
        return False

    def start_tracking(self):
        thread = threading.Thread(target=self.track_loop)
        thread.daemon = True
        thread.start()

    def stop(self):
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()
        self.face_mesh.close()

    def get_current_gaze(self):
        return self.current_gaze_zone

    def get_latest_offsets(self):
        return self.latest_dx, self.latest_dy
