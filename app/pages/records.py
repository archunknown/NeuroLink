from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from ..database import get_all_patients

class RecordsPage(QWidget):
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
        back_btn.clicked.connect(lambda: self.switch_page("menu") )
        header.addWidget(back_btn)
        header.addStretch()
        layout.addLayout(header)
        
        # Título
        title = QLabel("Registros de Pacientes")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Área de registros
        self.records_text = QTextEdit()
        self.records_text.setReadOnly(True)
        self.records_text.setStyleSheet("background-color: #1e293b; color: #e2e8f0; border-radius: 8px; padding: 15px;")
        layout.addWidget(self.records_text)
        
        # Botón refresh
        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.setFixedHeight(40)
        btn_refresh.clicked.connect(self.load_records)
        layout.addWidget(btn_refresh)
        
        self.load_records()
        self.setLayout(layout)
    
    def load_records(self):
        patients = get_all_patients()
        if not patients:
            self.records_text.setText("No hay registros de pacientes aún.")
            return
        
        text = "<b style='color: #3b82f6; font-size: 14px;'>REGISTROS DE PACIENTES</b><br><br>"
        for i, patient in enumerate(patients, 1):
            # Nuevos índices: 1:dni, 2:nombres, 3:paterno, 4:materno, 5:edad, 6:sintomas, 7:urgencia, 8:fecha
            full_name = f"{patient[2]} {patient[3]} {patient[4]}".strip()
            urgency_color = "#ef4444" if patient[7] == "Alta" else "#10b981"
            
            text += "<div style='background-color: #0f172a; padding: 12px; margin: 8px 0; border-left: 4px solid " + urgency_color + "; border-radius: 4px;'>"
            text += f"<b>#{i} - {full_name}</b> (DNI: {patient[1]})<br>"
            text += f"Edad: {patient[5]} | Fecha: {patient[8]}<br>"
            text += f"Síntomas: {patient[6]}<br>"
            text += f"Urgencia: <span style='color: {urgency_color}; font-weight: bold;'>{patient[7]}</span>"
            text += "</div>"
        self.records_text.setHtml(text)
