from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database import create_patient_table, insert_patient, get_all_patients, update_patient_urgency

# ==================== ESTILOS ====================
STYLE_SHEET = """
    QMainWindow {
        background-color: #0f172a;
    }
    
    QWidget {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    QPushButton {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 14px;
    }
    
    QPushButton:hover {
        background-color: #2563eb;
    }
    
    QPushButton:pressed {
        background-color: #1d4ed8;
    }
    
    QPushButton#btnSecondary {
        background-color: #64748b;
    }
    
    QPushButton#btnSecondary:hover {
        background-color: #475569;
    }
    
    QPushButton#btnDanger {
        background-color: #ef4444;
    }
    
    QPushButton#btnDanger:hover {
        background-color: #dc2626;
    }
    
    QPushButton#btnSuccess {
        background-color: #10b981;
    }
    
    QPushButton#btnSuccess:hover {
        background-color: #059669;
    }
    
    QLineEdit, QTextEdit {
        background-color: #1e293b;
        color: #e2e8f0;
        border: 2px solid #334155;
        border-radius: 6px;
        padding: 10px;
        font-size: 13px;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border: 2px solid #3b82f6;
    }
    
    QLabel {
        color: #e2e8f0;
    }
    
    QLabel#title {
        font-size: 28px;
        font-weight: bold;
        color: #3b82f6;
    }
    
    QLabel#subtitle {
        font-size: 16px;
        color: #94a3b8;
    }
"""

# ==================== PÁGINA PRINCIPAL ====================
class MainMenuPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page = switch_page_callback
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
        btn_register.setFont(QFont("Segoe UI", 14))
        btn_register.clicked.connect(lambda: self.switch_page("register"))
        layout.addWidget(btn_register)
        
        btn_assistant = QPushButton("🏥 Asistente de Paciente")
        btn_assistant.setFixedHeight(60)
        btn_assistant.setFont(QFont("Segoe UI", 14))
        btn_assistant.clicked.connect(lambda: self.switch_page("assistant"))
        layout.addWidget(btn_assistant)
        
        btn_records = QPushButton("📊 Registros de Pacientes")
        btn_records.setFixedHeight(60)
        btn_records.setFont(QFont("Segoe UI", 14))
        btn_records.clicked.connect(lambda: self.switch_page("records"))
        layout.addWidget(btn_records)
        
        layout.addStretch()
        
        self.setLayout(layout)

# ==================== PÁGINA DE REGISTRO ====================
class RegisterPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page = switch_page_callback
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
        title = QLabel("Auto-Registro y Triaje")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Campos
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)
        
        # Nombre
        label_name = QLabel("Nombre Completo")
        label_name.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ingrese su nombre...")
        self.input_name.setFixedHeight(40)
        form_layout.addWidget(label_name)
        form_layout.addWidget(self.input_name)
        
        # Edad
        label_age = QLabel("Edad")
        label_age.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.input_age = QLineEdit()
        self.input_age.setPlaceholderText("Ingrese su edad...")
        self.input_age.setFixedHeight(40)
        form_layout.addWidget(label_age)
        form_layout.addWidget(self.input_age)
        
        # Síntomas
        label_symptoms = QLabel("Descripción de Síntomas")
        label_symptoms.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.input_symptoms = QTextEdit()
        self.input_symptoms.setPlaceholderText("Describa sus síntomas en detalle...")
        self.input_symptoms.setFixedHeight(120)
        form_layout.addWidget(label_symptoms)
        form_layout.addWidget(self.input_symptoms)
        
        layout.addLayout(form_layout)
        layout.addSpacing(10)
        
        # Botón de envío
        btn_submit = QPushButton("✓ Registrar Paciente")
        btn_submit.setObjectName("btnSuccess")
        btn_submit.setFixedHeight(50)
        btn_submit.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        btn_submit.clicked.connect(self.submit_form)
        layout.addWidget(btn_submit)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def submit_form(self):
        name = self.input_name.text().strip()
        age = self.input_age.text().strip()
        symptoms = self.input_symptoms.toPlainText().strip()
        
        if not name or not age or not symptoms:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos.")
            return
        
        try:
            age_int = int(age)
        except ValueError:
            QMessageBox.warning(self, "Error", "La edad debe ser un número.")
            return
        
        urgency = "No Urgente"
        if insert_patient(name, age_int, symptoms, urgency):
            QMessageBox.information(self, "Éxito", f"¡Paciente {name} registrado correctamente!")
            self.input_name.clear()
            self.input_age.clear()
            self.input_symptoms.clear()
            self.switch_page("menu")
        else:
            QMessageBox.critical(self, "Error", "No se pudo registrar el paciente.")

# ==================== PÁGINA ASISTENTE ====================
class AssistantPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page = switch_page_callback
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
            ("💊 Pedir Analgésicos", self.request_painkiller),
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
    
    def request_painkiller(self):
        QMessageBox.information(self, "Solicitud", "Se ha registrado tu solicitud de analgésicos.\n¡Un enfermero llegará pronto!")
    
    def call_nurse(self):
        QMessageBox.information(self, "Llamada", "Se ha alertado a una enfermera.\n¡Llegará en unos momentos!")

# ==================== PÁGINA DE REGISTROS ====================
class RecordsPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page = switch_page_callback
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
            urgency_color = "#ef4444" if patient[4] == "Urgente" else "#10b981"
            text += f"""
            <div style='background-color: #0f172a; padding: 12px; margin: 8px 0; border-left: 4px solid {urgency_color}; border-radius: 4px;'>
                <b>#{i} - {patient[1]}</b> | Edad: {patient[2]} | {patient[5]}<br>
                Síntomas: {patient[3]}<br>
                Urgencia: <span style='color: {urgency_color}; font-weight: bold;'>{patient[4]}</span>
            </div>
            """
        self.records_text.setHtml(text)

# ==================== VENTANA PRINCIPAL ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroLink - Sistema de Gestión Neurológica")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(STYLE_SHEET)
        
        # Stack widget para cambiar entre páginas
        self.stacked_widget = QStackedWidget()
        
        self.pages = {
            "menu": MainMenuPage(self.switch_page),
            "register": RegisterPage(self.switch_page),
            "assistant": AssistantPage(self.switch_page),
            "records": RecordsPage(self.switch_page),
        }
        
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        
        self.setCentralWidget(self.stacked_widget)
    
    def switch_page(self, page_name):
        if page_name == "records":
            self.pages["records"].load_records()
        self.stacked_widget.setCurrentWidget(self.pages[page_name])

if __name__ == "__main__":
    create_patient_table()
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()