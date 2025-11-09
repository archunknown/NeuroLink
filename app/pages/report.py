from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer

class ReportPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.switch_page = self.main_window.switch_page
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel("Reporte de Registro")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        self.report_text = QLabel()
        self.report_text.setObjectName("subtitle")
        self.report_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.report_text.setWordWrap(True)
        self.layout.addWidget(self.report_text)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.switch_page("welcome"))

    def set_report_data(self, patient_info, urgency, symptoms):
        full_name = f"{patient_info['nombres']} {patient_info['apellido_paterno']} {patient_info['apellido_materno']}".strip()
        
        report = f"""
        <b>DNI:</b> {patient_info['dni']}<br>
        <b>Nombre Completo:</b> {full_name}<br>
        <b>Edad:</b> {patient_info['edad']}<br>
        <b>Dirección:</b> {patient_info['direccion']}<br>
        <b>Distrito:</b> {patient_info['distrito']}<br>
        <b>Provincia:</b> {patient_info['provincia']}<br>
        <hr>
        <b>Síntomas Reportados:</b> {symptoms}<br>
        <b>Nivel de Urgencia:</b> {urgency}<br>
        """
        self.report_text.setText(report)
        
        # Start the timer to go back to the main menu
        self.timer.start(10000) # 10 seconds
