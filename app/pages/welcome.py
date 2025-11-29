import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from .shared_widgets import RoleCard
from app.utils.paths import resource_path  # <--- IMPORTANTE: El "GPS" de archivos

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

        # --- CORRECCIÓN DE RUTAS AQUI ---
        # Usamos resource_path para encontrar la carpeta assets correctamente ya sea en codigo o exe
        icon_base_path = resource_path(os.path.join("app", "assets", "icons"))
        
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

        # Botón de Salir
        exit_button = QPushButton("Salir")
        exit_button.setObjectName("btnSecondary")
        exit_button.setFixedWidth(150)
        
        # CORRECCIÓN ICONO SALIR
        exit_icon_path = resource_path(os.path.join("app", "assets", "icons", "close.png"))
        if os.path.exists(exit_icon_path): 
             exit_button.setIcon(QIcon(exit_icon_path))
        
        exit_button.clicked.connect(lambda: parent.close() if parent else self.window().close())
        
        main_layout.addWidget(exit_button, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        self.setLayout(main_layout)

    def on_role_selected(self, role_name):
        """
        Emite la señal con el nombre del rol seleccionado.
        """
        self.role_selected.emit(role_name)