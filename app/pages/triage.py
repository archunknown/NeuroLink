
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from ..database import insert_patient, get_patient_by_dni

class TriagePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.switch_page = self.main_window.switch_page
        self.current_patient = None # Almacenará la info del paciente
        self.questions = [
            "¿Tiene fiebre alta (más de 38°C)?",
            "¿Tiene dificultad para respirar?",
            "¿Siente dolor en el pecho?",
            "¿Ha perdido el conocimiento en las últimas 24 horas?",
            "¿Tiene algún sangrado inusual?"
        ]
        self.answers = []
        self.current_question_index = 0
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.question_label = QLabel()
        self.question_label.setObjectName("subtitle")
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.question_label)

        self.layout.addSpacing(30)

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(40)

        self.yes_button = QPushButton("👍 Sí")
        self.yes_button.setObjectName("btnSuccess")
        self.yes_button.setFixedHeight(80)
        self.yes_button.clicked.connect(self.answer_yes)
        self.button_layout.addWidget(self.yes_button)

        self.no_button = QPushButton("👎 No")
        self.no_button.setObjectName("btnDanger")
        self.no_button.setFixedHeight(80)
        self.no_button.clicked.connect(self.answer_no)
        self.button_layout.addWidget(self.no_button)

        self.layout.addLayout(self.button_layout)
        
        self.confirm_button = QPushButton("✓ Finalizar y Guardar")
        self.confirm_button.setObjectName("btnSuccess")
        self.confirm_button.setFixedHeight(60)
        self.confirm_button.clicked.connect(self.save_triage_results)
        self.confirm_button.hide()
        self.layout.addWidget(self.confirm_button)

        self.setLayout(self.layout)
        self.show_question()

    def start_triage(self, patient_info):
        """Recibe la información del paciente desde la ventana principal."""
        self.current_patient = patient_info
        self.reset()

    def show_question(self):
        if self.current_question_index < len(self.questions):
            self.question_label.setText(self.questions[self.current_question_index])
            self.yes_button.show()
            self.no_button.show()
            self.confirm_button.hide()
        else:
            self.question_label.setText("Cuestionario completado. Confirme para guardar el registro.")
            self.yes_button.hide()
            self.no_button.hide()
            self.confirm_button.show()

    def answer(self, answer):
        if self.current_question_index < len(self.questions):
            self.answers.append(answer)
            self.next_question()

    def answer_yes(self):
        self.answer(True)

    def answer_no(self):
        self.answer(False)

    def next_question(self):
        self.current_question_index += 1
        self.show_question()

    def previous_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            if self.answers:
                self.answers.pop()
            self.show_question()

    def save_triage_results(self):
        if not self.current_patient:
            QMessageBox.critical(self, "Error", "No hay información del paciente para guardar.")
            return

        patient = self.current_patient
        if get_patient_by_dni(patient['dni']):
            QMessageBox.warning(self, "Registro Duplicado", f"El DNI {patient['dni']} ya se encuentra registrado.")
            self.reset()
            self.switch_page("welcome")
            return

        urgency = "Alta" if any(self.answers) else "Normal"
        
        sintomas_list = [self.questions[i] for i, ans in enumerate(self.answers) if ans]
        symptoms_str = ", ".join(sintomas_list) if sintomas_list else "Ningún síntoma reportado"

        # Usar los datos del paciente recibidos
        if insert_patient(
            dni=patient['dni'],
            nombres=patient['nombres'],
            apellido_paterno=patient['apellido_paterno'],
            apellido_materno=patient['apellido_materno'],
            age=patient['edad'],
            symptoms=symptoms_str,
            urgency=urgency,
            direccion=patient['direccion'],
            distrito=patient['distrito'],
            provincia=patient['provincia']
        ):
            self.reset()
            self.switch_page(
                "report",
                patient_info=patient,
                urgency=urgency,
                symptoms=symptoms_str
            )
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar el registro en la base de datos.")

    def reset(self):
        self.answers = []
        self.current_question_index = 0
        # No reseteamos self.current_patient aquí, se asigna en start_triage
        self.show_question()

