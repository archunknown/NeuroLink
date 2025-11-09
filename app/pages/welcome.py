import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from .shared_widgets import RoleCard

class WelcomePage(QWidget):
    """
    La pantalla de bienvenida que permite al usuario seleccionar su rol usando tarjetas visuales.
    """
    role_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        title = QLabel("Bienvenido a NeuroLink")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtítulo
        subtitle = QLabel("Por favor, selecciona tu rol para comenzar")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout para las tarjetas
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(40)

        # Crear y añadir las tarjetas
        icon_base_path = os.path.join("app", "assets", "icons")
        
        card_new_patient = RoleCard(
            os.path.join(icon_base_path, "new_patient.png"),
            "Paciente Nuevo",
            "Inicia tu proceso de auto-registro y triaje de síntomas."
        )
        card_in_room = RoleCard(
            os.path.join(icon_base_path, "in_room.png"),
            "Paciente en Habitación",
            "Accede al asistente para solicitar ayuda y comunicarte."
        )
        card_staff = RoleCard(
            os.path.join(icon_base_path, "medical_staff.png"),
            "Personal Médico",
            "Accede a los registros de pacientes y herramientas de consulta."
        )

        cards_layout.addWidget(card_new_patient)
        cards_layout.addWidget(card_in_room)
        cards_layout.addWidget(card_staff)

        # Conectar señales
        card_new_patient.clicked.connect(lambda: self.on_role_selected("new_patient"))
        card_in_room.clicked.connect(lambda: self.on_role_selected("in_room"))
        card_staff.clicked.connect(lambda: self.on_role_selected("staff"))

        # Añadir widgets al layout principal
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addLayout(cards_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(main_layout)

    def on_role_selected(self, role_name):
        """
        Emite la señal con el nombre del rol seleccionado.
        """
        self.role_selected.emit(role_name)
