from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QFont
from ..utils.audio import speak
from ..workers.voice_worker import VoiceWorker

class AssistantPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.switch_page = self.main_window.switch_page
        
        # Estado del worker de voz
        self.is_listening = False
        self.thread = None
        self.worker = None

        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QHBoxLayout()
        back_btn = QPushButton("← Atrás")
        back_btn.setObjectName("btnSecondary")
        back_btn.setMaximumWidth(100)
        back_btn.clicked.connect(self.go_back)
        header.addWidget(back_btn)
        header.addStretch()
        layout.addLayout(header)
        
        # Título
        title = QLabel("Asistente de Paciente")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Seleccione una opción o use el micrófono para hablar")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Botones de solicitud
        self.buttons = {
            "agua": ("💧 Pedir Agua", self.request_water),
            "baño": ("🚽 Pedir Baño", self.request_bathroom),
            "analgesicos": ("💊 Pedir Analgésicos", self.ask_for_painkiller),
            "enfermera": ("📞 Llamar Enfermera", self.call_nurse),
        }
        
        for text, callback in self.buttons.values():
            btn = QPushButton(text)
            btn.setFixedHeight(70)
            btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        layout.addStretch()

        # Sección de control por voz
        voice_control_layout = QVBoxLayout()
        voice_control_layout.setSpacing(10)
        
        self.voice_status_label = QLabel("Presione el micrófono para dar una orden por voz")
        self.voice_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        voice_control_layout.addWidget(self.voice_status_label)

        self.speak_button = QPushButton("🎤 Activar Micrófono")
        self.speak_button.setFixedHeight(60)
        self.speak_button.clicked.connect(self.toggle_voice_mode)
        voice_control_layout.addWidget(self.speak_button)

        layout.addLayout(voice_control_layout)
        self.setLayout(layout)

    def go_back(self):
        self.stop_voice_mode() # Asegurarse de detener el worker al salir
        self.switch_page("welcome")

    def toggle_voice_mode(self):
        if not self.is_listening:
            self.is_listening = True
            self.speak_button.setText("🛑 Detener Micrófono")
            self.speak_button.setObjectName("btnDanger")
            self.speak_button.style().unpolish(self.speak_button)
            self.speak_button.style().polish(self.speak_button)
            
            self.thread = QThread()
            self.worker = VoiceWorker()
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.handle_command)
            self.worker.error.connect(lambda msg: self.voice_status_label.setText(f"Info: {msg}"))
            self.worker.listening.connect(lambda: self.voice_status_label.setText("Escuchando..."))
            self.worker.processing.connect(lambda: self.voice_status_label.setText("Procesando comando..."))
            
            self.thread.start()
        else:
            self.stop_voice_mode()

    def stop_voice_mode(self):
        if not self.is_listening:
            return
            
        self.is_listening = False
        if self.thread and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()

        self.speak_button.setText("🎤 Activar Micrófono")
        self.speak_button.setObjectName("")
        self.speak_button.style().unpolish(self.speak_button)
        self.speak_button.style().polish(self.speak_button)
        self.voice_status_label.setText("Presione el micrófono para dar una orden por voz")

    def handle_command(self, text):
        command = text.lower()
        self.voice_status_label.setText(f"Comando reconocido: '{text}'")

        if "agua" in command:
            self.request_water()
        elif "baño" in command:
            self.request_bathroom()
        elif "analgésico" in command or "dolor" in command:
            self.ask_for_painkiller()
        elif "enfermera" in command or "ayuda" in command:
            self.call_nurse()
        else:
            speak("Comando no reconocido.", self)
            self.voice_status_label.setText(f"Comando no reconocido: '{text}'")

        # Detener el modo de escucha después de un comando para esperar la siguiente activación
        self.stop_voice_mode()

    def request_water(self):
        QMessageBox.information(self, "Solicitud", "Se ha registrado tu solicitud de agua.\n¡Un enfermero llegará pronto!")
        speak("Solicitud de agua registrada.", self)
    
    def request_bathroom(self):
        QMessageBox.information(self, "Solicitud", "Se ha registrado tu solicitud de baño.\n¡Un enfermero llegará pronto!")
        speak("Solicitud de baño registrada.", self)
    
    def ask_for_painkiller(self):
        question_page = self.main_window.pages["question"]
        question_page.set_question("¿Está seguro de que desea pedir un analgésico?")
        self.switch_page("question")

    def call_nurse(self):
        QMessageBox.information(self, "Llamada", "Se ha alertado a una enfermera.\n¡Llegará en unos momentos!")
        speak("Alerta a enfermería enviada.", self)
