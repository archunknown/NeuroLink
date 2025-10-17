import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from app.vision import HandDetector
from .database import create_patient_table

import configparser

class CameraWidget(QWidget):
    gesture_detected = pyqtSignal(str, object)

    def __init__(self):
        super().__init__()

        # Leer configuración
        config = configparser.ConfigParser()
        config.read("config.ini")
        
        max_hands = config.getint("GestureDetection", "MaxHands", fallback=1)
        min_detection_confidence = config.getfloat("GestureDetection", "MinDetectionConfidence", fallback=0.8)
        min_tracking_confidence = config.getfloat("GestureDetection", "MinTrackingConfidence", fallback=0.8)

        # Configuración de la cámara y detector de manos
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(max_hands=max_hands, 
                                     detection_con=min_detection_confidence, 
                                     track_con=min_tracking_confidence)

        # Etiqueta para mostrar el video
        self.camera_label = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.camera_label)
        self.setLayout(layout)

        # Temporizador para actualizar el frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        success, img = self.cap.read()
        if not success:
            return

        img = self.detector.find_hands(img, draw=False)
        lm_list = self.detector.find_position(img)

        if len(lm_list) != 0:
            thumb_gesture = self.detector.detect_thumb_gesture()
            if thumb_gesture:
                self.gesture_detected.emit(thumb_gesture, {})
            elif self.detector.is_open_hand():
                self.gesture_detected.emit("back", {})
            elif self.detector.is_fist():
                self.gesture_detected.emit("fist", {})
            else:
                hover_pos = self.detector.get_hover_position()
                if hover_pos:
                    self.gesture_detected.emit("hover", {"x": hover_pos[0], "y": hover_pos[1]})

            swipe_gesture = self.detector.detect_swipe()
            if swipe_gesture:
                self.gesture_detected.emit("swipe", {"direction": swipe_gesture})

        img = self.detector.find_hands(img, draw=True)

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

# ==================== ESTILOS ====================
STYLE_SHEET = """
    QMainWindow {
        background-color: #0f172a;
    }
    
    QWidget {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    QPushButton {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 14px;
    }
    
    QPushButton:hover {
        background-color: #2563eb;
    }
    
    QPushButton:pressed {
        background-color: #1d4ed8;
    }

    QPushButton[selected="true"] {
        border: 4px solid #facc15; /* Yellow-400 */
    }
    
    QPushButton#btnSecondary {
        background-color: #64748b;
    }
    
    QPushButton#btnSecondary:hover {
        background-color: #475569;
    }
    
    QPushButton#btnDanger {
        background-color: #ef4444;
    }
    
    QPushButton#btnDanger:hover {
        background-color: #dc2626;
    }
    
    QPushButton#btnSuccess {
        background-color: #10b981;
    }
    
    QPushButton#btnSuccess:hover {
        background-color: #059669;
    }
    
    QLineEdit, QTextEdit {
        background-color: #1e293b;
        color: #e2e8f0;
        border: 2px solid #334155;
        border-radius: 6px;
        padding: 10px;
        font-size: 13px;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border: 2px solid #3b82f6;
    }
    
    QLabel {
        color: #e2e8f0;
    }
    
    QLabel#title {
        font-size: 28px;
        font-weight: bold;
        color: #3b82f6;
    }
    
    QLabel#subtitle {
        font-size: 16px;
        color: #94a3b8;
    }
"""

# ==================== PÁGINAS ====================
from .pages.main_menu import MainMenuPage
from .pages.triage import TriagePage
from .pages.assistant import AssistantPage
from .pages.records import RecordsPage
from .pages.question import QuestionPage
from .pages.help import HelpPage

# ==================== VENTANA PRINCIPAL ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroLink - Sistema de Gestión Neurológica")
        self.setGeometry(100, 100, 1300, 700) # Adjusted width for the camera view
        self.setStyleSheet(STYLE_SHEET)

        # Layout principal
        main_layout = QHBoxLayout()
        
        # Stack widget para cambiar entre páginas (ocupa el 70% del espacio)
        self.stacked_widget = QStackedWidget()
        self.pages = {
            "menu": MainMenuPage(self),
            "triage": TriagePage(self),
            "assistant": AssistantPage(self),
            "records": RecordsPage(self),
            "question": QuestionPage(self),
            "help": HelpPage(self),
        }
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        
        # Widget de la cámara (ocupa el 30% del espacio)
        self.camera_widget = CameraWidget()
        self.camera_widget.gesture_detected.connect(self.handle_gesture)

        main_layout.addWidget(self.stacked_widget, 7) # 70%
        main_layout.addWidget(self.camera_widget, 3) # 30%

        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.selected_button = None
        self.fist_cooldown_timer = QTimer()
        self.fist_cooldown_timer.setSingleShot(True)
        self.gesture_cooldown_timer = QTimer()
        self.gesture_cooldown_timer.setSingleShot(True)

        # Feedback label for gestures
        self.feedback_label = QLabel(self)
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.6); color: white; font-size: 48px; border-radius: 10px; padding: 10px;")
        self.feedback_label.hide()

        self.feedback_timer = QTimer(self)
        self.feedback_timer.setSingleShot(True)
        self.feedback_timer.timeout.connect(self.feedback_label.hide)
    
    def show_feedback(self, text):
        self.feedback_label.setText(text)
        self.feedback_label.adjustSize()
        # Center it
        self.feedback_label.move(int((self.width() - self.feedback_label.width()) / 2), int((self.height() - self.feedback_label.height()) / 2))
        self.feedback_label.show()
        self.feedback_label.raise_()
        self.feedback_timer.start(500) # Hide after 500ms

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.feedback_label.move(int((self.width() - self.feedback_label.width()) / 2), int((self.height() - self.feedback_label.height()) / 2))
    
    def handle_gesture(self, gesture_type, data):
        if self.gesture_cooldown_timer.isActive():
            return

        if gesture_type == "hover":
            # No feedback for hover as it's continuous
            self.handle_hover_gesture(data["x"], data["y"])
        elif gesture_type == "fist":
            self.show_feedback("👊")
            self.handle_fist_gesture()
        elif gesture_type == "swipe":
            if data["direction"] == "left":
                self.show_feedback("⬅️")
            else:
                self.show_feedback("➡️")
            self.handle_swipe_gesture(data["direction"])
        elif gesture_type == "thumbs_up":
            self.show_feedback("👍")
            self.handle_thumbs_up_gesture()
        elif gesture_type == "thumbs_down":
            self.show_feedback("👎")
            self.handle_thumbs_down_gesture()
        elif gesture_type == "back":
            self.show_feedback("🤚")
            self.handle_back_gesture()
        
        self.gesture_cooldown_timer.start(500)

    def handle_hover_gesture(self, x, y):
        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()
        
        global_x = int(np.interp(x, [0, 640], [0, screen_width]))
        global_y = int(np.interp(y, [0, 480], [0, screen_height]))

        widget = QApplication.widgetAt(QPoint(global_x, global_y))

        button = None
        if isinstance(widget, QPushButton):
            button = widget
        elif widget and isinstance(widget.parent(), QPushButton):
            button = widget.parent()

        if self.selected_button and self.selected_button != button:
            self.selected_button.setProperty("selected", False)
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)

        self.selected_button = button
        if self.selected_button:
            self.selected_button.setProperty("selected", True)
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)

    def handle_fist_gesture(self):
        if self.selected_button and not self.fist_cooldown_timer.isActive():
            self.selected_button.click()
            self.fist_cooldown_timer.start(1000)  # 1 second cooldown

    def handle_swipe_gesture(self, direction):
        current_page = self.stacked_widget.currentWidget()
        if isinstance(current_page, TriagePage):
            if direction == "right":
                current_page.next_question()
            elif direction == "left":
                current_page.previous_question()
        else:
            current_index = self.stacked_widget.currentIndex()
            if direction == "left":
                new_index = (current_index - 1) % self.stacked_widget.count()
                self.stacked_widget.setCurrentIndex(new_index)
            elif direction == "right":
                new_index = (current_index + 1) % self.stacked_widget.count()
                self.stacked_widget.setCurrentIndex(new_index)

    def handle_thumbs_up_gesture(self):
        current_page = self.stacked_widget.currentWidget()
        if isinstance(current_page, (TriagePage, QuestionPage)):
            current_page.answer_yes()

    def handle_thumbs_down_gesture(self):
        current_page = self.stacked_widget.currentWidget()
        if isinstance(current_page, (TriagePage, QuestionPage)):
            current_page.answer_no()

    def handle_back_gesture(self):
        if self.stacked_widget.currentWidget() != self.pages["menu"]:
            self.switch_page("menu")

    def switch_page(self, page_name):
        if page_name == "records":
            self.pages["records"].load_records()
        
        if page_name == "triage":
            self.pages["triage"].reset()

        self.stacked_widget.setCurrentWidget(self.pages[page_name])

if __name__ == "__main__":
    create_patient_table()
    app = QApplication([])
    
    main_window = MainWindow()
    main_window.show()
    
    app.exec()
