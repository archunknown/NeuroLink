from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QIcon
from app.ia_client import get_conversational_answer
from app.utils.audio import speak
from app.workers.voice_worker import VoiceWorker
import os

class AIWorker(QObject):
    """Worker para ejecutar la consulta a la IA en un hilo separado."""
    finished = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        response = get_conversational_answer(self.query)
        self.finished.emit(response)

class NaturalQueryPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.voice_thread = None
        self.thread = None
        self.voice_worker = None # Initialize voice_worker here
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title Section
        title = QLabel("Consulta con IA")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #FFFFFF; margin-bottom: 10px;")
        layout.addWidget(title)

        subtitle = QLabel("Presiona el micrófono y habla para consultar los registros.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #AAAAAA; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Main Interaction Area (Card)
        interaction_card = QWidget()
        interaction_card.setStyleSheet("""
            QWidget {
                background-color: #1C1C1C;
                border-radius: 20px;
                border: 1px solid #333333;
            }
        """)
        card_layout = QVBoxLayout(interaction_card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(30)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Microphone Button (Prominent)
        self.mic_button = QPushButton()
        self.mic_button.setFixedSize(100, 100)
        self.mic_button.setIcon(QIcon(os.path.join("app", "assets", "icons", "mic.png")))
        self.mic_button.setIconSize(self.mic_button.size() * 0.5)
        self.mic_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mic_button.clicked.connect(self.start_listening)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: #00A1FF;
                border: none;
                border-radius: 50px; /* Circular */
            }
            QPushButton:hover {
                background-color: #33B4FF;
            }
            QPushButton:pressed {
                background-color: #0080CC;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
        """)
        # Fallback text if icon missing
        if self.mic_button.icon().isNull():
            self.mic_button.setText("🎤")
            self.mic_button.setStyleSheet(self.mic_button.styleSheet() + "font-size: 40px;")

        card_layout.addWidget(self.mic_button, 0, Qt.AlignmentFlag.AlignCenter)

        # Text Input (Subtle)
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("O escribe tu pregunta aquí...")
        self.query_input.returnPressed.connect(self.handle_query)
        self.query_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.query_input.setStyleSheet("""
            QLineEdit {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border: 1px solid #444444;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                min-width: 400px;
            }
            QLineEdit:focus {
                border: 1px solid #00A1FF;
                background-color: #333333;
            }
        """)
        card_layout.addWidget(self.query_input)
        
        # Action Buttons Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.query_button = QPushButton("Enviar Consulta")
        self.query_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.query_button.clicked.connect(self.handle_query)
        self.query_button.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555555;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                border: 1px solid #00A1FF;
            }
        """)
        
        self.back_button = QPushButton("Volver")
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.clicked.connect(lambda: self.main_window.switch_page("staff_dashboard"))
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: 1px solid transparent;
                padding: 10px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #2A2A2A;
            }
        """)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.query_button)
        buttons_layout.addStretch()
        
        card_layout.addLayout(buttons_layout)
        
        layout.addWidget(interaction_card)

        # Response Area
        self.response_label = QLabel("Los resultados aparecerán aquí...")
        self.response_label.setWordWrap(True)
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.response_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 18px;
                font-style: italic;
                padding: 20px;
                min-height: 80px;
            }
        """)
        layout.addWidget(self.response_label, 1)

        self.setLayout(layout)

    def cleanup_threads(self):
        # Cleanup voice thread
        if self.voice_thread:
            if self.voice_worker:
                self.voice_worker.stop()
            try:
                if self.voice_thread.isRunning():
                    self.voice_thread.quit()
                    self.voice_thread.wait()
            except RuntimeError:
                pass
            self.voice_thread = None
            self.voice_worker = None

        # Cleanup AI thread
        if self.thread:
            try:
                if self.thread.isRunning():
                    self.thread.quit()
                    self.thread.wait()
            except RuntimeError:
                pass
            self.thread = None

    def start_listening(self):
        self.cleanup_threads()
        
        self.query_input.setEnabled(False)
        self.mic_button.setEnabled(False)
        self.response_label.setText("Escuchando... 🎤")
        
        self.voice_thread = QThread()
        self.voice_worker = VoiceWorker(phrase_time_limit=10)
        self.voice_worker.moveToThread(self.voice_thread)
        
        self.voice_thread.started.connect(self.voice_worker.run)
        self.voice_worker.finished.connect(self.on_voice_recognized)
        self.voice_worker.error.connect(self.on_voice_error)
        self.voice_worker.listening.connect(lambda: self.response_label.setText("Escuchando... 🎤"))
        self.voice_worker.processing.connect(lambda: self.response_label.setText("Procesando audio... ⏳"))
        
        self.voice_worker.finished.connect(self.voice_thread.quit)
        self.voice_worker.finished.connect(self.voice_worker.deleteLater)
        self.voice_thread.finished.connect(self.voice_thread.deleteLater)
        
        self.voice_thread.start()

    def on_voice_recognized(self, text):
        # Stop listening after one successful recognition
        if self.voice_worker:
            self.voice_worker.stop()
            
        self.query_input.setText(text)
        self.query_input.setEnabled(True)
        self.mic_button.setEnabled(True)
        self.response_label.setText("Voz detectada. Consultando...")
        self.handle_query() # Auto-submit

    def on_voice_error(self, error_msg):
        if self.voice_worker:
            self.voice_worker.stop()
            
        self.query_input.setEnabled(True)
        self.mic_button.setEnabled(True)
        self.response_label.setText(error_msg)
        self.cleanup_threads()

    def handle_query(self):
        user_query = self.query_input.text()
        if not user_query or not self.query_button.isEnabled():
            return

        self.cleanup_threads()

        self.query_button.setEnabled(False)
        self.query_input.setEnabled(False)
        self.mic_button.setEnabled(False)
        self.response_label.setText("Consultando a la IA... (Esto puede tardar un poco)")

        self.thread = QThread()
        self.worker = AIWorker(user_query)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_query_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_query_finished(self, response):
        self.response_label.setText(response)
        self.query_button.setEnabled(True)
        self.query_input.setEnabled(True)
        self.mic_button.setEnabled(True)
        
        # Read the response aloud
        speak(response, self)