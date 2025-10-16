import cv2
import mediapipe as mp
import numpy as np

class HandDetector:
    def __init__(self, max_hands=1, detection_con=0.7, track_con=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=max_hands,
                                          min_detection_confidence=detection_con,
                                          min_tracking_confidence=track_con)
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]
        self.prev_hand_pos = None
        self.click_debounce_counter = 0
        self.debounce_threshold = 5  # 5 frames of debouncing
        self.gesture = ""

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                    # Add gesture text
                    cv2.putText(img, self.gesture, (10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                    # Add finger status
                    if self.lm_list:
                        fingers = self.fingers_up()
                        cv2.putText(img, f'Fingers: {fingers}', (10, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                        # Add click distance
                        x1, y1 = self.lm_list[4][1:]
                        x2, y2 = self.lm_list[8][1:]
                        distance = np.hypot(x2 - x1, y2 - y1)
                        cv2.putText(img, f'Click dist: {int(distance)}', (10, 150), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        return img

    def find_position(self, img, hand_no=0):
        self.lm_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(my_hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([id, cx, cy])
        return self.lm_list

    def fingers_up(self):
        fingers = []
        # Thumb
        if self.lm_list[self.tip_ids[0]][1] < self.lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # 4 Fingers
        for id in range(1, 5):
            if self.lm_list[self.tip_ids[id]][2] < self.lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def detect_swipe(self):
        if not self.lm_list or sum(self.fingers_up()) != 5:  # Ensure the hand is open
            self.prev_hand_pos = None
            return None

        current_hand_pos = self.lm_list[9][1]  # Use the center of the palm (landmark 9)
        swipe = None

        if self.prev_hand_pos is not None:
            diff = current_hand_pos - self.prev_hand_pos
            if diff > 80:  # Increased swipe threshold
                self.gesture = "Swipe Right"
                swipe = "right"
            elif diff < -80:  # Increased swipe threshold
                self.gesture = "Swipe Left"
                swipe = "left"
        
        self.prev_hand_pos = current_hand_pos
        return swipe

    def get_hover_position(self):
        if not self.lm_list:
            return None
        self.gesture = "Hover"
        return self.lm_list[9][1:]  # Return x, y of the palm center

    def is_fist(self):
        if not self.lm_list:
            return False
        
        # Calculate distance between thumb tip and index finger tip
        x1, y1 = self.lm_list[4][1:]
        x2, y2 = self.lm_list[8][1:]
        distance = np.hypot(x2 - x1, y2 - y1)

        if distance < 50:
            self.click_debounce_counter += 1
            if self.click_debounce_counter >= self.debounce_threshold:
                self.click_debounce_counter = 0
                self.gesture = "Click"
                return True
        else:
            self.click_debounce_counter = 0
        
        return False
