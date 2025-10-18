
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout
from PyQt6.QtCore import pyqtSignal, Qt

class DniInputPage(QWidget):
    """
    Página para que el usuario ingrese su DNI usando un teclado numérico en pantalla.
    """
    dni_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dni_string = ""
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        title = QLabel("Ingrese su DNI para comenzar")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Display para el DNI ingresado
        self.dni_display = QLabel("")
        self.dni_display.setObjectName("subtitle") # Reutilizamos estilo
        self.dni_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dni_display.setStyleSheet("font-size: 36px; font-weight: bold; border: 2px solid #334155; border-radius: 8px; padding: 10px; min-height: 60px;")

        # Teclado numérico
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        buttons = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            'BORRAR', '0', 'CONFIRMAR'
        ]

        positions = [(i, j) for i in range(4) for j in range(3)]

        for position, text in zip(positions, buttons):
            button = QPushButton(text)
            button.setFixedSize(120, 80)
            button.setStyleSheet("font-size: 16px; font-weight: bold;")
            
            if text == 'BORRAR':
                button.setObjectName("btnDanger")
                button.clicked.connect(self.delete_char)
            elif text == 'CONFIRMAR':
                button.setObjectName("btnSuccess")
                button.clicked.connect(self.submit_dni)
            else:
                button.clicked.connect(self.add_char)
            
            grid_layout.addWidget(button, *position)

        # Layout principal
        main_layout.addWidget(title)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.dni_display)
        main_layout.addSpacing(30)
        
        container = QWidget()
        container.setLayout(grid_layout)
        container.setFixedWidth(420)
        main_layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)

    def add_char(self):
        """Añade un número al DNI si no se ha alcanzado el límite."""
        sender = self.sender()
        if len(self.dni_string) < 8:
            self.dni_string += sender.text()
            self.update_display()

    def delete_char(self):
        """Borra el último número del DNI."""
        self.dni_string = self.dni_string[:-1]
        self.update_display()

    def submit_dni(self):
        """Emite la señal con el DNI si es válido."""
        if len(self.dni_string) == 8:
            self.dni_submitted.emit(self.dni_string)

    def update_display(self):
        """Actualiza el texto del display del DNI."""
        self.dni_display.setText(self.dni_string)
        
    def reset(self):
        """Resetea la página a su estado inicial."""
        self.dni_string = ""
        self.update_display()

