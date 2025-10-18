import cv2
import mediapipe as mp
import numpy as np
from collections import deque

class HandDetector:
    def __init__(self, max_hands=1, detection_con=0.85, track_con=0.85):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]
        
        # Gesture state management
        self.gesture = ""
        self.prev_gesture = ""
        self.gesture_state = "idle"  # idle, hovering, clicking, gesturing
        
        # Hovering state (no cooldown for continuous tracking)
        self.is_hovering = False
        self.hover_stable_frames = 0
        
        # Swipe detection
        self.hand_positions = deque(maxlen=10)
        self.swipe_cooldown = 0
        self.swipe_threshold = 150  # More deliberate
        
        # Four fingers click detection (thumb closed, 4 fingers extended)
        self.four_fingers_frames = 0
        self.four_fingers_threshold = 5  # Reduced for faster response
        self.four_fingers_cooldown = 0  # Separate cooldown for clicks
        
        
        # Peace/V gesture (better for back navigation)
        self.peace_frames = 0
        self.peace_threshold = 10
        self.peace_cooldown = 0
        
        # Pointing gesture (index finger only - alternative to hover)
        self.pointing_frames = 0
        
    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    # Draw landmarks
                    self.mp_draw.draw_landmarks(
                        img, hand_lms, self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Display state and gesture info
                    state_color = {
                        "idle": (180, 180, 180),
                        "hovering": (0, 255, 255),
                        "clicking": (0, 255, 0),
                        "gesturing": (255, 165, 0)
                    }.get(self.gesture_state, (255, 255, 255))
                    
                    cv2.putText(
                        img, f'State: {self.gesture_state}', 
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.8, state_color, 2
                    )
                    
                    cv2.putText(
                        img, f'Gesture: {self.gesture}', 
                        (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.8, (0, 255, 0), 2
                    )
                    
                    if self.lm_list:
                        fingers = self.fingers_up()
                        cv2.putText(
                            img, f'Fingers: {fingers}', 
                            (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                            0.6, (255, 255, 0), 2
                        )
                        
                        # Draw cursor position indicator
                        if self.is_pointing() or self.is_hovering:
                            index_tip = self.lm_list[8]
                            cv2.circle(img, (index_tip[1], index_tip[2]), 15, (0, 255, 255), 3)
                            cv2.circle(img, (index_tip[1], index_tip[2]), 5, (0, 255, 0), -1)
        
        # Decrease cooldowns
        if self.swipe_cooldown > 0:
            self.swipe_cooldown -= 1
        if self.four_fingers_cooldown > 0:
            self.four_fingers_cooldown -= 1
        if self.peace_cooldown > 0:
            self.peace_cooldown -= 1
            
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
        """Detect which fingers are extended"""
        fingers = []
        if not self.lm_list:
            return []

        # Thumb - Check horizontal distance from wrist
        thumb_tip = self.lm_list[self.tip_ids[0]]
        thumb_base = self.lm_list[2]
        wrist = self.lm_list[0]
        
        thumb_distance = abs(thumb_tip[1] - wrist[1])
        thumb_base_distance = abs(thumb_base[1] - wrist[1])
        
        if thumb_distance > thumb_base_distance * 1.3:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other 4 fingers
        for id in range(1, 5):
            tip = self.lm_list[self.tip_ids[id]]
            pip = self.lm_list[self.tip_ids[id] - 2]
            
            if tip[2] < pip[2] - 15:  # More strict
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers

    def is_pointing(self):
        """Check if only index finger is extended (pointing gesture)"""
        if not self.lm_list:
            return False
            
        fingers = self.fingers_up()
        # Index up, all others down
        is_pointing = fingers == [0, 1, 0, 0, 0]
        
        if is_pointing:
            self.pointing_frames += 1
        else:
            self.pointing_frames = 0
            
        return self.pointing_frames > 2  # Stable for 2 frames


    def detect_peace_sign(self):
        """Detect peace/V sign (index and middle up) - Better for back navigation"""
        if not self.lm_list or self.peace_cooldown > 0:
            return False

        fingers = self.fingers_up()
        
        # Peace sign: only index and middle fingers up
        is_peace = fingers == [0, 1, 1, 0, 0]
        
        if is_peace:
            self.peace_frames += 1
            
            if self.peace_frames >= self.peace_threshold:
                self.gesture = "Peace Sign (Back) ✌"
                self.gesture_state = "gesturing"
                self.peace_cooldown = 25
                self.peace_frames = 0
                return True
        else:
            self.peace_frames = 0
            
        return False

    def is_fist(self):
        """Detect four fingers extended (thumb closed) gesture for clicking"""
        if not self.lm_list or self.four_fingers_cooldown > 0:
            return False

        fingers = self.fingers_up()
        
        # Check: thumb closed (0) and all 4 other fingers extended (1)
        is_four_fingers = fingers == [0, 1, 1, 1, 1]
        
        if is_four_fingers:
            self.four_fingers_frames += 1
            
            if self.four_fingers_frames >= self.four_fingers_threshold:
                self.gesture = "Four Fingers Click! 🖐"
                self.gesture_state = "clicking"
                self.four_fingers_cooldown = 15  # Cooldown after click
                self.four_fingers_frames = 0
                return True
        else:
            self.four_fingers_frames = 0
        
        return False

    def detect_swipe(self):
        """Detect swipe gestures with improved filtering"""
        if not self.lm_list or self.swipe_cooldown > 0:
            self.hand_positions.clear()
            return None

        fingers = self.fingers_up()
        
        # Only detect swipe with all 5 fingers extended (open hand)
        if sum(fingers) != 5:
            self.hand_positions.clear()
            return None

        current_pos = self.lm_list[9][1]  # Palm center X
        self.hand_positions.append(current_pos)
        
        if len(self.hand_positions) < 8:
            return None
        
        start_pos = self.hand_positions[0]
        end_pos = self.hand_positions[-1]
        total_movement = end_pos - start_pos
        
        movements = [self.hand_positions[i+1] - self.hand_positions[i] 
                    for i in range(len(self.hand_positions)-1)]
        
        if total_movement > self.swipe_threshold:
            positive_movements = sum(1 for m in movements if m > 0)
            if positive_movements > len(movements) * 0.75:
                self.gesture = "Swipe Right ➡"
                self.gesture_state = "gesturing"
                self.swipe_cooldown = 25
                self.hand_positions.clear()
                return "right"
                
        elif total_movement < -self.swipe_threshold:
            negative_movements = sum(1 for m in movements if m < 0)
            if negative_movements > len(movements) * 0.75:
                self.gesture = "Swipe Left ⬅"
                self.gesture_state = "gesturing"
                self.swipe_cooldown = 25
                self.hand_positions.clear()
                return "left"
        
        return None

    def get_hover_position(self):
        """Get current hover position using index finger tip"""
        if not self.lm_list:
            self.is_hovering = False
            return None
        
        # Only hover when pointing or when hand is relaxed (not gesturing)
        fingers = self.fingers_up()
        
        # Allow hover with pointing gesture or normal hand position
        # Don't hover when making other gestures (four fingers, peace, thumb, swipe)
        is_gesture = (
            fingers == [0, 1, 1, 1, 1] or  # Four fingers (click)
            fingers == [0, 1, 1, 0, 0] or  # Peace
            sum(fingers) == 5  # Open hand (swipe)
        )
        
        if is_gesture and not self.is_pointing():
            self.is_hovering = False
            return None
        
        # Use index finger tip for precise hovering
        index_tip = self.lm_list[8]
        self.gesture = "Hovering..."
        self.gesture_state = "hovering"
        self.is_hovering = True
        self.hover_stable_frames += 1
        
        return index_tip[1:]  # Return x, y coordinates

    def get_state(self):
        """Get current gesture state"""
        return self.gesture_state
    
    def reset_state(self):
        """Reset to idle state"""
        if not self.lm_list:
            self.gesture_state = "idle"
            self.gesture = ""
            self.is_hovering = False