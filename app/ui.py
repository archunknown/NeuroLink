import cv2
import numpy as np
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve, QThread, QObject
from PyQt6.QtGui import QImage, QPixmap, QCursor, QPainter, QColor, QPen, QIcon
from app.vision import HandDetector
from app.database import create_patient_table

import configparser
import os
from dotenv import load_dotenv
import sys

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
        
        # Config de gestos
        max_hands = config.getint("GestureDetection", "MaxHands", fallback=1)
        min_detection_confidence = config.getfloat("GestureDetection", "MinDetectionConfidence", fallback=0.85)
        min_tracking_confidence = config.getfloat("GestureDetection", "MinTrackingConfidence", fallback=0.85)
        
        # Config de UI
        self.show_landmarks_only = config.getboolean("UI", "show_landmarks_only", fallback=False)

        # Configuración de la cámara y detector de manos
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.detector = HandDetector(max_hands=max_hands, 
                                     detection_con=min_detection_confidence, 
                                     track_con=min_tracking_confidence)

        # Etiqueta para mostrar el video
        self.camera_label = QLabel()
        self.camera_label.setStyleSheet("border: 2px solid red;")
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

        # Procesar la imagen para encontrar manos, pero no dibujar todavía
        processed_img = self.detector.find_hands(img, draw=False)
        lm_list = self.detector.find_position(processed_img)

        # Lógica de detección de gestos (no cambia)
        if len(lm_list) != 0:
            hover_pos = self.detector.get_hover_position()
            if hover_pos:
                self.gesture_detected.emit("hover", {"x": hover_pos[0], "y": hover_pos[1]})
            if self.detector.is_fist():
                self.gesture_detected.emit("fist", {})
            if self.detector.detect_peace_sign():
                self.gesture_detected.emit("peace", {})
            swipe_gesture = self.detector.detect_swipe()
            if swipe_gesture:
                self.gesture_detected.emit("swipe", {"direction": swipe_gesture})
        else:
            self.detector.reset_state()

        # Preparar la imagen final para mostrar
        display_img = None
        if self.show_landmarks_only:
            # Crear un lienzo negro y dibujar solo los landmarks
            display_img = np.zeros_like(img)
            if self.detector.results.multi_hand_landmarks:
                for hand_lms in self.detector.results.multi_hand_landmarks:
                    self.detector.mp_draw.draw_landmarks(
                        display_img, hand_lms, self.detector.mp_hands.HAND_CONNECTIONS)
        else:
            # Dibujar sobre la imagen original
            display_img = self.detector.find_hands(img, draw=True)

        # Convertir y mostrar la imagen final
        display_img = cv2.flip(display_img, 1)
        img_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()
# ==================== ESTILOS ====================
STYLE_SHEET = """
    QMainWindow, QWidget {
        background-color: #000000;
        color: #FFFFFF;
        font-family: "Segoe UI";
    }
    
    /* Estilo para las nuevas tarjetas de rol */
    QPushButton#RoleCard {
        background-color: #1C1C1C;
        border: 2px solid #888888;
        border-radius: 12px;
        text-align: center;
        padding: 20px;
    }
    
    QPushButton#RoleCard:hover {
        background-color: #2A2A2A;
        border: 2px solid #FFFFFF;
    }

    QPushButton#RoleCard[selected="true"] {
        border: 4px solid #00A1FF;
        background-color: #2A2A2A;
    }
    
    /* Estilo para el botón de ayuda */
    QPushButton#HelpButton {
        background-color: #1C1C1C;
        border: 2px solid #00A1FF;
        border-radius: 30px; /* Mitad del tamaño para hacerlo un círculo */
        font-size: 24px;
        font-weight: bold;
        color: #FFFFFF;
    }

    QPushButton#HelpButton:hover {
        background-color: #00A1FF;
        color: #000000;
    }
    
    /* Estilos de botones genéricos (se mantienen por si se usan en otras partes) */
    QPushButton {
        background-color: #1C1C1C;
        color: #FFFFFF;
        border: 1px solid #888888;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 14px;
    }
    
    QPushButton:hover {
        background-color: #888888;
        color: #000000;
        border: 1px solid #FFFFFF;
    }
    
    QPushButton:pressed {
        background-color: #2A2A2A;
    }

    QPushButton[selected="true"] {
        border: 4px solid #00A1FF;
        background-color: #888888;
    }
    
    QPushButton#btnSecondary {
        background-color: #888888;
        color: #000000;
    }
    
    QPushButton#btnSecondary:hover {
        background-color: #FFFFFF;
        color: #000000;
    }
    
    /* Estilos de texto */
    QLineEdit, QTextEdit {
        background-color: #1C1C1C;
        color: #FFFFFF;
        border: 2px solid #888888;
        border-radius: 6px;
        padding: 10px;
        font-size: 13px;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border: 2px solid #00A1FF;
    }
    
    QLabel {
        color: #FFFFFF;
        background-color: transparent;
    }
    
    QLabel#title {
        font-size: 36px;
        font-weight: bold;
        color: #FFFFFF;
    }
    
    QLabel#subtitle {
        font-size: 18px;
        color: #888888;
    }
"""

# ==================== PÁGINAS ====================
from app.pages.shared_widgets import RoleCard
from app.pages.welcome import WelcomePage
from app.pages.triage import TriagePage
from app.pages.assistant import AssistantPage
from app.pages.records import RecordsPage
from app.pages.question import QuestionPage
from app.pages.help import HelpPage
from app.pages.dni_input import DniInputPage
from app.pages.report import ReportPage
from app.pages.natural_query import NaturalQueryPage

from app.database import execute_query

# Placeholder for Staff Dashboard
class StaffDashboardPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        title = QLabel("Panel de Personal Médico")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtítulo
        subtitle = QLabel("Seleccione una herramienta")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout para las tarjetas
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(40)

        icon_base_path = os.path.join("app", "assets", "icons")
        
        card_records = RoleCard(
            os.path.join(icon_base_path, "records.png"),
            "Ver Registros",
            "Visualiza, busca y gestiona la lista de pacientes registrados."
        )
        card_ai_query = RoleCard(
            os.path.join(icon_base_path, "ai_query.png"),
            "Consulta con IA",
            "Realiza preguntas en lenguaje natural sobre los datos de los pacientes."
        )

        cards_layout.addWidget(card_records)
        cards_layout.addWidget(card_ai_query)

        # Conectar señales
        card_records.clicked.connect(lambda: self.main_window.switch_page("records"))
        card_ai_query.clicked.connect(lambda: self.main_window.switch_page("natural_query"))

        # Botón para volver
        back_button = QPushButton("← Volver a la Selección de Rol")
        back_button.setObjectName("btnSecondary")
        back_button.setFixedWidth(300)
        back_button.clicked.connect(lambda: self.main_window.switch_page("welcome"))

        # Añadir widgets al layout principal
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addStretch(1)
        main_layout.addLayout(cards_layout)
        main_layout.addStretch(1)
        main_layout.addWidget(back_button, 0, Qt.AlignmentFlag.AlignCenter)
# ==================== VENTANA PRINCIPAL ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroLink - Sistema de Gestión Neurológica")
        self.setWindowIcon(QIcon(os.path.join("app", "assets", "logo.png")))
        self.setGeometry(100, 100, 1400, 750)
        self.setStyleSheet(STYLE_SHEET)

        # Layout principal
        main_layout = QHBoxLayout()
        
        # Stack widget para cambiar entre páginas
        self.stacked_widget = QStackedWidget()
        self.pages = {
            "welcome": WelcomePage(self),
            "staff_dashboard": StaffDashboardPage(self),
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
        
        # Conectar señales de las páginas
        self.pages["welcome"].role_selected.connect(self.handle_role_selection)
        self.pages["dni_input"].dni_submitted.connect(self.start_dni_validation)

        # Iniciar en la página de bienvenida
        self.stacked_widget.setCurrentWidget(self.pages["welcome"])

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
        """)
        self.feedback_label.hide()

        self.feedback_timer = QTimer(self)
        self.feedback_timer.setSingleShot(True)
        self.feedback_timer.timeout.connect(self.feedback_label.hide)
        
        # Virtual cursor for better feedback
        self.virtual_cursor = None
        if sys.platform == 'win32':
            self.virtual_cursor = VirtualCursor(self)
            self.virtual_cursor.setGeometry(0, 0, self.width(), self.height())
            self.virtual_cursor.show()
            self.virtual_cursor.raise_()

        # Botón de Ayuda Contextual
        self.help_button = QPushButton(self)
        self.help_button.setObjectName("HelpButton")
        self.help_button.setFixedSize(60, 60)
        self.help_button.setIcon(QIcon(os.path.join("app", "assets", "icons", "help.png")))
        self.help_button.setIconSize(self.help_button.size() * 0.6)
        self.help_button.setToolTip("Obtener ayuda contextual")
        self.help_button.clicked.connect(self.show_contextual_help)
        self.help_button.show()

        # Toast Notification Container
        self.toast_widget = None
        self.toast_timer = QTimer()
        self.toast_timer.setSingleShot(True)
        self.toast_timer.timeout.connect(self.hide_toast)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Mover el label de feedback
        self.feedback_label.move(
            int((self.width() - self.feedback_label.width()) / 2), 
            int((self.height() - self.feedback_label.height()) / 2)
        )
        # Mover el cursor virtual
        if self.virtual_cursor:
            self.virtual_cursor.setGeometry(0, 0, self.width(), self.height())
        
        # Mover el botón de ayuda a la esquina inferior derecha
        margin = 20
        self.help_button.move(
            self.width() - self.help_button.width() - margin,
            self.height() - self.help_button.height() - margin
        )
        self.help_button.raise_()
    def show_toast(self, message, duration=3000):
        if self.toast_widget:
            self.toast_widget.close()
        
        self.toast_widget = QLabel(message, self)
        self.toast_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast_widget.setStyleSheet("""
            background-color: #333333;
            color: #FFFFFF;
            border-radius: 10px;
            padding: 15px 25px;
            font-size: 16px;
            border: 1px solid #555555;
        """)
        self.toast_widget.adjustSize()
        
        margin = 30
        x = self.width() - self.toast_widget.width() - margin
        y = margin + 50 
        
        self.toast_widget.move(x, y)
        self.toast_widget.show()
        self.toast_widget.raise_()
        
        self.toast_opacity = QPropertyAnimation(self.toast_widget, b"windowOpacity")
        self.toast_opacity.setDuration(300)
        self.toast_opacity.setStartValue(0.0)
        self.toast_opacity.setEndValue(1.0)
        self.toast_opacity.start()

        self.toast_timer.start(duration)

    def hide_toast(self):
        if self.toast_widget:
            self.toast_opacity = QPropertyAnimation(self.toast_widget, b"windowOpacity")
            self.toast_opacity.setDuration(300)
            self.toast_opacity.setStartValue(1.0)
            self.toast_opacity.setEndValue(0.0)
            self.toast_opacity.finished.connect(self.toast_widget.close)
            self.toast_opacity.start()

    def show_contextual_help(self):
        current_page = self.stacked_widget.currentWidget()
        title = "Ayuda Contextual"
        text = "No hay ayuda disponible para esta página."

        if isinstance(current_page, WelcomePage):
            title = "Ayuda: Selección de Rol"
            text = ("Usa tu mano para apuntar a una de las tarjetas y mantenla sobre ella para seleccionarla.\n\n"
                    "Cierra el puño (gesto de 4 dedos) para confirmar tu selección.")
        
        elif isinstance(current_page, DniInputPage):
            title = "Ayuda: Ingreso de DNI"
            text = ("Puedes ingresar tu DNI usando el teclado numérico en pantalla o activando el modo de voz.\n\n"
                    "Para usar los gestos, apunta a un número y cierra el puño para añadirlo.")

        elif isinstance(current_page, TriagePage):
            title = "Ayuda: Cuestionario de Triaje"
            text = ("Responde a las preguntas con 'Sí' o 'No'.\n\n"
                    "Puedes deslizar tu mano hacia la derecha para avanzar a la siguiente pregunta o hacia la izquierda para retroceder.")

        elif isinstance(current_page, AssistantPage):
            title = "Ayuda: Asistente de Paciente"
            text = "Apunta a una de las opciones y cierra el puño para realizar una solicitud al personal de enfermería."

        elif isinstance(current_page, StaffDashboardPage):
            title = "Ayuda: Panel de Personal"
            text = "Selecciona una de las herramientas para gestionar los datos de la clínica."

        elif isinstance(current_page, RecordsPage):
            title = "Ayuda: Registros de Pacientes"
            text = "Aquí puedes visualizar la lista de todos los pacientes registrados. Usa el botón 'Actualizar' para recargar los datos."
        
        elif isinstance(current_page, NaturalQueryPage):
            title = "Ayuda: Consulta con IA"
            text = "Escribe una pregunta en español sobre los datos de los pacientes y presiona 'Consultar'.\n\nEj: ¿Cuál es el promedio de edad de los pacientes con urgencia alta?"

        QMessageBox.information(self, title, text)
    
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
            if self.virtual_cursor:
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
        if self.virtual_cursor:
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


    def handle_role_selection(self, role):
        if role == "new_patient":
            self.switch_page("dni_input")
        elif role == "in_room":
            self.switch_page("assistant")
        elif role == "staff":
            # Aquí se podría añadir una lógica de contraseña en el futuro
            self.switch_page("staff_dashboard")

    def handle_back_gesture(self):
        """Handle back gesture - Peace sign is more deliberate than open hand"""
        # Siempre regresa a la página de bienvenida, a menos que ya estemos ahí.
        if self.stacked_widget.currentWidget() != self.pages["welcome"]:
            self.switch_page("welcome")

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
