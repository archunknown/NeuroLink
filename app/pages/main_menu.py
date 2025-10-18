from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class MainMenuPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.switch_page = self.main_window.switch_page
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 60, 40, 60)
        
        # Logo/Título
        title = QLabel("NeuroLink")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        layout.addWidget(title)
        
        subtitle = QLabel("Sistema Integrado de Gestión Neurológica")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(40)
        
        # Botones principales
        btn_register = QPushButton("📋 Auto-Registro y Triaje")
        btn_register.setFixedHeight(60)
        btn_register.setFont(QFont("Segoe UI", 12))
        btn_register.clicked.connect(lambda: self.switch_page("dni_input"))
        layout.addWidget(btn_register)
        
        btn_assistant = QPushButton("🏥 Asistente de Paciente")
        btn_assistant.setFixedHeight(60)
        btn_assistant.setFont(QFont("Segoe UI", 12))
        btn_assistant.clicked.connect(lambda: self.switch_page("assistant"))
        layout.addWidget(btn_assistant)
        
        btn_records = QPushButton("📊 Registros de Pacientes")
        btn_records.setFixedHeight(60)
        btn_records.setFont(QFont("Segoe UI", 12))
        btn_records.clicked.connect(lambda: self.switch_page("records"))
        layout.addWidget(btn_records)

        btn_help = QPushButton("❔ Ayuda")
        btn_help.setFixedHeight(60)
        btn_help.setFont(QFont("Segoe UI", 12))
        btn_help.clicked.connect(lambda: self.switch_page("help"))
        layout.addWidget(btn_help)
        
        layout.addStretch()
        
        self.setLayout(layout)
