import cv2
import numpy as np
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve, QThread, QObject
from PyQt6.QtGui import QImage, QPixmap, QCursor, QPainter, QColor, QPen
from app.vision import HandDetector
from app.database import create_patient_table

import configparser
import os
from dotenv import load_dotenv

# ==================== API WORKER ====================
class DniApiWorker(QObject):
    """
    Worker thread to handle DNI API requests without freezing the UI.
    """
    finished = pyqtSignal(dict)

    def __init__(self, dni):
        super().__init__()
        load_dotenv()
        self.dni = dni
        self.api_token = os.getenv("API_TOKEN")
        self.api_url = f"https://miapi.cloud/v1/dni/{self.dni}"

    def run(self):
        try:
            response = requests.get(self.api_url, headers={"Authorization": f"Bearer {self.api_token}"}, timeout=10)
            if response.status_code == 200:
                data = response.json().get("datos", {})
                if data:
                    self.finished.emit({"success": True, "data": data})
                else:
                    self.finished.emit({"success": False, "error": "DNI no encontrado."})
            else:
                self.finished.emit({"success": False, "error": f"Error en la API: {response.status_code}"})
        except requests.RequestException as e:
            self.finished.emit({"success": False, "error": f"Error de red: {e}"})


class VirtualCursor(QWidget):
    """Virtual cursor overlay for visual feedback"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        self.cursor_pos = QPoint(0, 0)
        self.cursor_size = 30
        self.is_clicking = False
        self.click_animation = 0
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(30)
        
    def update_position(self, x, y):
        self.cursor_pos = QPoint(x, y)
        self.update()
        
    def set_clicking(self, clicking):
        self.is_clicking = clicking
        if clicking:
            self.click_animation = 10
        self.update()
        
    def animate(self):
        if self.click_animation > 0:
            self.click_animation -= 1
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw outer ring
        size = self.cursor_size + self.click_animation * 2
        color = QColor(0, 255, 0) if self.is_clicking else QColor(0, 255, 255)
        
        pen = QPen(color, 3)
        painter.setPen(pen)
        painter.setBrush(QColor(color.red(), color.green(), color.blue(), 50))
        painter.drawEllipse(self.cursor_pos, size//2, size//2)
        
        # Draw center dot
        painter.setBrush(color)
        painter.drawEllipse(self.cursor_pos, 5, 5)

class CameraWidget(QWidget):
    gesture_detected = pyqtSignal(str, object)

    def __init__(self):
        super().__init__()

        # Leer configuración
        config = configparser.ConfigParser()
        config.read("config.ini")
        
        max_hands = config.getint("GestureDetection", "MaxHands", fallback=1)
        min_detection_confidence = config.getfloat("GestureDetection", "MinDetectionConfidence", fallback=0.85)
        min_tracking_confidence = config.getfloat("GestureDetection", "MinTrackingConfidence", fallback=0.85)

        # Configuración de la cámara y detector de manos
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(max_hands=max_hands, 
                                     detection_con=min_detection_confidence, 
                                     track_con=min_tracking_confidence)

        # Etiqueta para mostrar el video
        self.camera_label = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.camera_label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Temporizador para actualizar el frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        success, img = self.cap.read()
        if not success:
            return

        img = self.detector.find_hands(img, draw=True)
        lm_list = self.detector.find_position(img)

        if len(lm_list) != 0:
            # Priority order: Check hover first, then other gestures
            hover_pos = self.detector.get_hover_position()
            if hover_pos:
                self.gesture_detected.emit("hover", {"x": hover_pos[0], "y": hover_pos[1]})
            
            # Check for click (fist) - This should work even while hovering
            if self.detector.is_fist():
                self.gesture_detected.emit("fist", {})
            
            # Check for peace sign (back gesture)
            if self.detector.detect_peace_sign():
                self.gesture_detected.emit("peace", {})
            
            
            # Check swipe gestures
            swipe_gesture = self.detector.detect_swipe()
            if swipe_gesture:
                self.gesture_detected.emit("swipe", {"direction": swipe_gesture})
        else:
            self.detector.reset_state()

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
        border: 4px solid #facc15;
        background-color: #2563eb;
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
from app.pages.main_menu import MainMenuPage
from app.pages.triage import TriagePage
from app.pages.assistant import AssistantPage
from app.pages.records import RecordsPage
from app.pages.question import QuestionPage
from app.pages.help import HelpPage
from app.pages.dni_input import DniInputPage
from app.pages.report import ReportPage
from app.pages.natural_query import NaturalQueryPage

from app.database import execute_query

# ==================== VENTANA PRINCIPAL ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroLink - Sistema de Gestión Neurológica")
        self.setGeometry(100, 100, 1400, 750)
        self.setStyleSheet(STYLE_SHEET)

        # Layout principal
        main_layout = QHBoxLayout()
        
        # Stack widget para cambiar entre páginas
        self.stacked_widget = QStackedWidget()
        self.pages = {
            "menu": MainMenuPage(self),
            "dni_input": DniInputPage(self),
            "triage": TriagePage(self),
            "assistant": AssistantPage(self),
            "records": RecordsPage(self),
            "question": QuestionPage(self),
            "help": HelpPage(self),
            "report": ReportPage(self),
            "natural_query": NaturalQueryPage(self),
        }
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        
        # Conectar señal de DNI
        self.pages["dni_input"].dni_submitted.connect(self.start_dni_validation)

        # Widget de la cámara
        self.camera_widget = CameraWidget()
        self.camera_widget.gesture_detected.connect(self.handle_gesture)

        main_layout.addWidget(self.stacked_widget, 7)
        main_layout.addWidget(self.camera_widget, 3)

        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Selected button tracking
        self.selected_button = None
        self.hover_stable_timer = QTimer()
        self.hover_stable_timer.setSingleShot(True)
        self.hover_stable_timer.timeout.connect(self.on_hover_stable)
        
        # Gesture cooldowns
        self.fist_cooldown_timer = QTimer()
        self.fist_cooldown_timer.setSingleShot(True)
        
        self.gesture_cooldown_timer = QTimer()
        self.gesture_cooldown_timer.setSingleShot(True)

        # Feedback label
        self.feedback_label = QLabel(self)
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.8); 
            color: white; 
            font-size: 48px; 
            border-radius: 15px; 
            padding: 20px;
            font-weight: bold;
        """
        )
        self.feedback_label.hide()

        self.feedback_timer = QTimer(self)
        self.feedback_timer.setSingleShot(True)
        self.feedback_timer.timeout.connect(self.feedback_label.hide)
        
        # Virtual cursor for better feedback
        self.virtual_cursor = VirtualCursor(self)
        self.virtual_cursor.setGeometry(0, 0, self.width(), self.height())
        self.virtual_cursor.show()
        self.virtual_cursor.raise_()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.feedback_label.move(
            int((self.width() - self.feedback_label.width()) / 2), 
            int((self.height() - self.feedback_label.height()) / 2)
        )
        self.virtual_cursor.setGeometry(0, 0, self.width(), self.height())
    
    def show_feedback(self, text, duration=800):
        self.feedback_label.setText(text)
        self.feedback_label.adjustSize()
        self.feedback_label.move(
            int((self.width() - self.feedback_label.width()) / 2), 
            int((self.height() - self.feedback_label.height()) / 2)
        )
        self.feedback_label.show()
        self.feedback_label.raise_()
        self.feedback_timer.start(duration)

    def start_dni_validation(self, dni):
        self.show_feedback("Validando DNI...", 20000) # Show until response
        self.thread = QThread()
        self.worker = DniApiWorker(dni)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_dni_validation_complete)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_dni_validation_complete(self, result):
        self.feedback_timer.stop()
        self.feedback_label.hide()

        if result["success"]:
            patient_data = result["data"]
            # Parse name and address
            raw_nombres = patient_data.get("nombres", "")
            paterno = patient_data.get("ape_paterno", "")
            materno = patient_data.get("ape_materno", "")
            
            domiciliado = patient_data.get("domiciliado", {})
            direccion = domiciliado.get("direccion", "")
            distrito = domiciliado.get("distrito", "")
            provincia = domiciliado.get("provincia", "")

            welcome_name = f"{raw_nombres} {paterno} {materno}".strip()
            self.show_feedback(f"Bienvenido(a)\n{welcome_name}", 2500)
            
            # Prepare data for triage page
            patient_info = {
                "dni": patient_data.get("dni", ""),
                "nombres": raw_nombres,
                "apellido_paterno": paterno,
                "apellido_materno": materno,
                "edad": 30, # Placeholder, API doesn't provide age
                "direccion": direccion,
                "distrito": distrito,
                "provincia": provincia
            }
            
            # Proceed to triage after welcome message
            QTimer.singleShot(2600, lambda: self.switch_page("triage", patient_info=patient_info))
        else:
            error_message = result.get("error", "Error desconocido")
            self.show_feedback(f"Error: {error_message}", 3000)
            # Reset DNI page to allow re-entry
            self.pages["dni_input"].reset()

    def handle_gesture(self, gesture_type, data):
        # Hover has no cooldown - it's continuous
        if gesture_type == "hover":
            self.handle_hover_gesture(data["x"], data["y"])
            return
        
        # Other gestures respect cooldown
        if self.gesture_cooldown_timer.isActive() and gesture_type != "fist":
            return

        if gesture_type == "fist":
            self.show_feedback("👊 CLICK", 500)
            self.virtual_cursor.set_clicking(True)
            QTimer.singleShot(200, lambda: self.virtual_cursor.set_clicking(False))
            self.handle_fist_gesture()
            
        elif gesture_type == "swipe":
            direction_emoji = "➡️" if data["direction"] == "right" else "⬅️"
            self.show_feedback(direction_emoji)
            self.handle_swipe_gesture(data["direction"])
            self.gesture_cooldown_timer.start(500)
            
            
        elif gesture_type == "peace":
            self.show_feedback("✌️ ATRÁS")
            self.handle_back_gesture()
            self.gesture_cooldown_timer.start(800)

    def handle_hover_gesture(self, x, y):
        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()
        
        # Map camera coordinates to screen coordinates
        global_x = int(np.interp(x, [0, 640], [0, screen_width]))
        global_y = int(np.interp(y, [0, 480], [0, screen_height]))
        
        # Update virtual cursor position
        self.virtual_cursor.update_position(global_x, global_y)

        widget = QApplication.widgetAt(QPoint(global_x, global_y))

        button = None
        if isinstance(widget, QPushButton):
            button = widget
        elif widget and isinstance(widget.parent(), QPushButton):
            button = widget.parent()

        # Deselect previous button
        if self.selected_button and self.selected_button != button:
            self.selected_button.setProperty("selected", False)
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)

        # Select new button
        self.selected_button = button
        if self.selected_button:
            self.selected_button.setProperty("selected", True)
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)
            
            # Start stable hover timer (for future enhancements)
            self.hover_stable_timer.start(500)
    
    def on_hover_stable(self):
        """Called when hover is stable on a button for a while"""
        # Could add additional feedback here if needed
        pass

    def handle_fist_gesture(self):
        """Handle fist/click gesture - works independently of other cooldowns"""
        if self.selected_button and not self.fist_cooldown_timer.isActive():
            # Visual feedback
            self.selected_button.setProperty("selected", False)
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)
            
            # Trigger click
            self.selected_button.click()
            self.fist_cooldown_timer.start(800)  # Prevent rapid double-clicks

    def handle_swipe_gesture(self, direction):
        current_page = self.stacked_widget.currentWidget()
        if isinstance(current_page, TriagePage):
            if direction == "right":
                current_page.next_question()
            elif direction == "left":
                current_page.previous_question()
        else:
            # Navigate between pages
            current_index = self.stacked_widget.currentIndex()
            if direction == "left":
                new_index = (current_index - 1) % self.stacked_widget.count()
                self.stacked_widget.setCurrentIndex(new_index)
            elif direction == "right":
                new_index = (current_index + 1) % self.stacked_widget.count()
                self.stacked_widget.setCurrentIndex(new_index)


    def handle_back_gesture(self):
        """Handle back gesture - Peace sign is more deliberate than open hand"""
        current_page = self.stacked_widget.currentWidget()
        if isinstance(current_page, DniInputPage):
             self.switch_page("menu")
        elif self.stacked_widget.currentWidget() != self.pages["menu"]:
            self.switch_page("menu")

    def switch_page(self, page_name, **kwargs):
        if page_name == "records":
            self.pages["records"].load_records()
        
        if page_name == "triage":
            self.pages["triage"].reset()
            if "patient_info" in kwargs:
                self.pages["triage"].start_triage(kwargs["patient_info"])

        if page_name == "dni_input":
            self.pages["dni_input"].reset()

        if page_name == "report":
            self.pages["report"].set_report_data(
                kwargs.get("patient_info"),
                kwargs.get("urgency"),
                kwargs.get("symptoms")
            )

        self.stacked_widget.setCurrentWidget(self.pages[page_name])

if __name__ == "__main__":
    create_patient_table()
    app = QApplication([])
    
    main_window = MainWindow()
    main_window.show()
    
    app.exec()    