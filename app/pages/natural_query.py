from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from app.ia_client import get_conversational_answer

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
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Consulta de Datos con Lenguaje Natural")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Realiza preguntas en español sobre los registros de pacientes.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Ej: ¿Cuántos pacientes son de Grocio Prado y tienen más de 30 años?")
        self.query_input.returnPressed.connect(self.handle_query)
        layout.addWidget(self.query_input)

        self.query_button = QPushButton("Consultar a la IA")
        self.query_button.clicked.connect(self.handle_query)
        layout.addWidget(self.query_button)
        
        self.back_button = QPushButton("Volver al Menú")
        self.back_button.setObjectName("btnSecondary")
        self.back_button.clicked.connect(lambda: self.main_window.switch_page("staff_dashboard"))
        layout.addWidget(self.back_button)

        self.response_label = QLabel("Los resultados de tu consulta aparecerán aquí.")
        self.response_label.setWordWrap(True)
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.response_label.setStyleSheet("""
            QLabel {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 15px;
                font-size: 16px;
                min-height: 100px;
            }
        """)
        layout.addWidget(self.response_label, 1)

        self.setLayout(layout)

    def handle_query(self):
        user_query = self.query_input.text()
        if not user_query:
            return

        self.query_button.setEnabled(False)
        self.query_input.setEnabled(False)
        self.response_label.setText("Consultando a la IA... (Esto puede tardar un poco)")

        self.thread = QThread()
        self.worker = AIWorker(user_query)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_ai_finish)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_ai_finish(self, response):
        self.response_label.setText(response)
        self.query_button.setEnabled(True)
        self.query_input.setEnabled(True)

    def reset(self):
        self.query_input.clear()
        self.response_label.setText("Los resultados de tu consulta aparecerán aquí.")