from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class HelpPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.switch_page = self.main_window.switch_page
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
        back_btn.clicked.connect(lambda: self.switch_page("menu"))
        header.addWidget(back_btn)
        header.addStretch()
        layout.addLayout(header)

        # Título
        title = QLabel("Ayuda: Gestos Disponibles")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(20)

        # Lista de gestos
        gestures = [
            ("🖐️", "Hover (Mover)", "Mueve el cursor por la pantalla."),
            ("👊", "Fist (Clic)", "Hace clic en el botón seleccionado."),
            ("⬅️ / ➡️", "Swipe (Deslizar)", "Navega entre preguntas o páginas."),
            ("👍", "Thumbs Up (Sí)", "Responde afirmativamente."),
            ("👎", "Thumbs Down (No)", "Responde negativamente."),
            ("🤚", "Open Hand (Atrás)", "Vuelve al menú principal.")
        ]

        for icon, name, description in gestures:
            gesture_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI Emoji", 24))
            
            text_layout = QVBoxLayout()
            name_label = QLabel(name)
            name_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            desc_label = QLabel(description)
            desc_label.setObjectName("subtitle")

            text_layout.addWidget(name_label)
            text_layout.addWidget(desc_label)

            gesture_layout.addWidget(icon_label)
            gesture_layout.addLayout(text_layout)
            gesture_layout.setStretch(1, 1)

            layout.addLayout(gesture_layout)
            layout.addSpacing(10)

        layout.addStretch()
        self.setLayout(layout)
