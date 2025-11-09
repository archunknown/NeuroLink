import os
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

class RoleCard(QPushButton):
    """
    Un widget de tarjeta clickeable que muestra un icono, título y descripción.
    Hereda de QPushButton para ser fácilmente clickeable y seleccionable.
    """
    def __init__(self, icon_path, title_text, description_text, parent=None):
        super().__init__(parent)
        self.setObjectName("RoleCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(300)
        self.setMinimumWidth(250)

        card_layout = QVBoxLayout(self)
        card_layout.setSpacing(15)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono
        icon_label = QLabel()
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(
                128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        else:
            # Si el icono no existe, muestra un texto de placeholder
            icon_label.setText("[ICONO]")
            
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)

        # Título
        title_label = QLabel(title_text)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #96a9a5;")
        card_layout.addWidget(title_label)

        # Descripción
        description_label = QLabel(description_text)
        description_font = QFont()
        description_font.setPointSize(11)
        description_label.setFont(description_font)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #525e68;")
        card_layout.addWidget(description_label)

        self.setLayout(card_layout)
