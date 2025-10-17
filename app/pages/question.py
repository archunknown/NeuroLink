from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt

class QuestionPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.switch_page = self.main_window.switch_page
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.question_label = QLabel("¿Pregunta de ejemplo?")
        self.question_label.setObjectName("subtitle")
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.question_label)

        layout.addSpacing(30)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)

        self.yes_button = QPushButton("👍 Sí")
        self.yes_button.setObjectName("btnSuccess")
        self.yes_button.setFixedHeight(80)
        self.yes_button.clicked.connect(self.answer_yes)
        button_layout.addWidget(self.yes_button)

        self.no_button = QPushButton("👎 No")
        self.no_button.setObjectName("btnDanger")
        self.no_button.setFixedHeight(80)
        self.no_button.clicked.connect(self.answer_no)
        button_layout.addWidget(self.no_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def set_question(self, question):
        self.question_label.setText(question)

    def answer_yes(self):
        QMessageBox.information(self, "Respuesta", "Has respondido que SÍ.")
        self.switch_page("menu")

    def answer_no(self):
        QMessageBox.warning(self, "Respuesta", "Has respondido que NO.")
        self.switch_page("menu")
