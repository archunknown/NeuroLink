from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea
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
        
        subtitle = QLabel("Usa estos gestos para controlar NeuroLink")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Scroll area para los gestos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)

        # Lista de gestos actualizada
        gestures = [
            ("☝️", "Apuntar (Navegar)", 
             "Solo el dedo índice extendido. Mueve el cursor virtual por la pantalla.",
             "#3b82f6"),
            
            ("👊", "Puño (Clic)", 
             "Cierra todos los dedos. Hace clic en el botón seleccionado.",
             "#10b981"),
            
            ("✌️", "Paz / Victory (Atrás)", 
             "Solo índice y medio extendidos. Regresa al menú principal.",
             "#f59e0b"),
            
            ("👍", "Pulgar Arriba (Sí)", 
             "Solo el pulgar extendido hacia arriba. Responde afirmativamente.",
             "#10b981"),
            
            ("👎", "Pulgar Abajo (No)", 
             "Solo el pulgar extendido hacia abajo. Responde negativamente.",
             "#ef4444"),
            
            ("🖐️", "Mano Abierta + Deslizar (Swipe)", 
             "4-5 dedos extendidos, desliza la mano hacia la izquierda o derecha. Navega entre páginas o preguntas.",
             "#8b5cf6"),
        ]

        for icon, name, description, color in gestures:
            gesture_widget = self.create_gesture_card(icon, name, description, color)
            scroll_layout.addWidget(gesture_widget)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.setLayout(layout)
    
    def create_gesture_card(self, icon, name, description, color):
        """Crear una tarjeta visual para cada gesto"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: #1e293b;
                border-left: 5px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        icon_label.setFixedWidth(60)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Texto
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {color};")
        
        desc_label = QLabel(description)
        desc_label.setObjectName("subtitle")
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Segoe UI", 12))
        
        text_layout.addWidget(name_label)
        text_layout.addWidget(desc_label)
        
        card_layout.addWidget(icon_label)
        card_layout.addLayout(text_layout, 1)
        
        return card