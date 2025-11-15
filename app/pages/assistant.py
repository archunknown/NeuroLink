from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class AssistantPage(QWidget):
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
        back_btn.clicked.connect(lambda: self.switch_page("welcome"))
        header.addWidget(back_btn)
        header.addStretch()
        layout.addLayout(header)
        
        # Título
        title = QLabel("Asistente de Paciente")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Seleccione una opción para continuar")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Botones de solicitud
        buttons = [
            ("💧 Pedir Agua", self.request_water),
            ("🚽 Pedir Baño", self.request_bathroom),
            ("💊 Pedir Analgésicos", self.ask_for_painkiller),
            ("📞 Llamar Enfermera", self.call_nurse),
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(70)
            btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def request_water(self):
        QMessageBox.information(self, "Solicitud", "Se ha registrado tu solicitud de agua.\n¡Un enfermero llegará pronto!")
    
    def request_bathroom(self):
        QMessageBox.information(self, "Solicitud", "Se ha registrado tu solicitud de baño.\n¡Un enfermero llegará pronto!")
    
    def ask_for_painkiller(self):
        question_page = self.main_window.pages["question"]
        question_page.set_question("¿Está seguro de que desea pedir un analgésico?")
        self.switch_page("question")

    def call_nurse(self):
        QMessageBox.information(self, "Llamada", "Se ha alertado a una enfermera.\n¡Llegará en unos momentos!")
