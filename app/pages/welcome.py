from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class WelcomePage(QWidget):
    """
    La pantalla de bienvenida que permite al usuario seleccionar su rol.
    """
    # Señal que se emite cuando un rol es seleccionado. El argumento es el nombre del rol.
    role_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        title = QLabel("Bienvenido a NeuroLink")
        title_font = QFont()
        title_font.setPointSize(36)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #e2e8f0;")

        # Subtítulo
        subtitle = QLabel("Por favor, selecciona tu rol para comenzar")
        subtitle_font = QFont()
        subtitle_font.setPointSize(18)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #94a3b8;")

        # Botones de rol
        self.btn_new_patient = QPushButton("Soy un Paciente Nuevo")
        self.btn_in_room = QPushButton("Estoy en mi Habitación")
        self.btn_staff = QPushButton("Soy Personal Médico")

        # Estilo y tamaño de botones
        button_font = QFont()
        button_font.setPointSize(16)
        for btn in [self.btn_new_patient, self.btn_in_room, self.btn_staff]:
            btn.setFont(button_font)
            btn.setMinimumHeight(80)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Conectar botones a un manejador de clics
        self.btn_new_patient.clicked.connect(lambda: self.on_role_selected("new_patient"))
        self.btn_in_room.clicked.connect(lambda: self.on_role_selected("in_room"))
        self.btn_staff.clicked.connect(lambda: self.on_role_selected("staff"))
        
        # Cambiar el color del botón de personal médico para diferenciarlo
        self.btn_staff.setObjectName("btnSecondary")


        # Añadir widgets al layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(self.btn_new_patient)
        layout.addWidget(self.btn_in_room)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        layout.addWidget(self.btn_staff)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout)

    def on_role_selected(self, role_name):
        """
        Emite la señal con el nombre del rol seleccionado.
        """
        self.role_selected.emit(role_name)
