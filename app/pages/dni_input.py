from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from app.workers.voice_worker import VoiceWorker

class DniInputPage(QWidget):
    """
    Página para que el usuario ingrese su DNI usando un teclado numérico en pantalla o por voz en modo continuo.
    """
    dni_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dni_string = ""
        self.is_listening = False
        self.thread = None
        self.worker = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Ingrese su DNI para comenzar")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dni_display = QLabel("")
        self.dni_display.setObjectName("subtitle")
        self.dni_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dni_display.setStyleSheet("font-size: 36px; font-weight: bold; border: 2px solid #334155; border-radius: 8px; padding: 10px; min-height: 60px;")

        self.voice_status_label = QLabel("Presione 'Hablar DNI' para iniciar el dictado por voz")
        self.voice_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voice_status_label.setStyleSheet("font-size: 14px; color: #94a3b8;")

        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'BORRAR', '0', 'CONFIRMAR']
        positions = [(i, j) for i in range(4) for j in range(3)]

        for position, text in zip(positions, buttons):
            button = QPushButton(text)
            button.setFixedSize(120, 80)
            button.setStyleSheet("font-size: 16px; font-weight: bold;")
            if text == 'BORRAR':
                button.setObjectName("btnDanger")
                button.clicked.connect(self.delete_char)
            elif text == 'CONFIRMAR':
                button.setObjectName("btnSuccess")
                button.clicked.connect(self.submit_dni)
            else:
                button.clicked.connect(self.add_char)
            grid_layout.addWidget(button, *position)

        self.speak_button = QPushButton("Hablar DNI 🎤")
        self.speak_button.setFixedSize(400, 60)
        self.speak_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.speak_button.clicked.connect(self.toggle_voice_mode)

        main_layout.addWidget(title)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.dni_display)
        main_layout.addWidget(self.voice_status_label)
        main_layout.addSpacing(30)
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addLayout(grid_layout)
        container_layout.addSpacing(15)
        container_layout.addWidget(self.speak_button)
        container.setFixedWidth(420)
        main_layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)

    def toggle_voice_mode(self):
        if not self.is_listening:
            self.is_listening = True
            self.speak_button.setText("Detener Dictado 🛑")
            self.speak_button.setObjectName("btnDanger")
            self.speak_button.style().unpolish(self.speak_button)
            self.speak_button.style().polish(self.speak_button)
            
            # Create and start the single persistent thread
            self.thread = QThread()
            self.worker = VoiceWorker()
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_voice_finished)
            self.worker.error.connect(self.on_voice_error)
            self.worker.listening.connect(lambda: self.voice_status_label.setText("Escuchando..."))
            self.worker.processing.connect(lambda: self.voice_status_label.setText("Procesando..."))
            
            self.thread.start()
        else:
            self.stop_voice_cycle()

    def stop_voice_cycle(self):
        if not self.is_listening:
            return
            
        self.is_listening = False
        if self.thread and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait() # Wait for the thread to finish cleanly

        self.speak_button.setText("Hablar DNI 🎤")
        self.speak_button.setObjectName("")
        self.speak_button.style().unpolish(self.speak_button)
        self.speak_button.style().polish(self.speak_button)
        if len(self.dni_string) < 8:
            self.voice_status_label.setText("Dictado detenido. Presione 'Hablar DNI' para continuar.")

    def on_voice_finished(self, text):
        if not self.is_listening:
            return
            
        self._parse_and_append_dni(text)
        
        if len(self.dni_string) >= 8:
            self.voice_status_label.setText("DNI completo.")
            self.stop_voice_cycle()
        else:
            remaining = 8 - len(self.dni_string)
            self.voice_status_label.setText(f"Reconocido. Faltan {remaining} dígitos.")

    def on_voice_error(self, message):
        if not self.is_listening:
            return
        self.voice_status_label.setText(f"Info: {message}")

    def _parse_and_append_dni(self, text):
        number_map = {
            'cero': '0', 'uno': '1', 'dos': '2', 'tres': '3', 'cuatro': '4',
            'cinco': '5', 'seis': '6', 'siete': '7', 'ocho': '8', 'nueve': '9'
        }
        
        processed_text = text.lower().replace(' ', '')
        
        for word, digit in number_map.items():
            processed_text = processed_text.replace(word, digit)

        for char in processed_text:
            if len(self.dni_string) >= 8:
                break
            if char.isdigit():
                self.dni_string += char

        self.update_display()

    def add_char(self):
        if self.is_listening: self.stop_voice_cycle()
        sender = self.sender()
        if len(self.dni_string) < 8:
            self.dni_string += sender.text()
            self.update_display()

    def delete_char(self):
        if self.is_listening: self.stop_voice_cycle()
        self.dni_string = self.dni_string[:-1]
        self.update_display()

    def submit_dni(self):
        if len(self.dni_string) == 8:
            self.dni_submitted.emit(self.dni_string)

    def update_display(self):
        self.dni_display.setText(self.dni_string)
        
    def reset(self):
        self.dni_string = ""
        self.update_display()
        if self.is_listening:
            self.stop_voice_cycle()
        self.voice_status_label.setText("Presione 'Hablar DNI' para iniciar el dictado por voz")

