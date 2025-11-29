import sys
import os
from PyQt6.QtWidgets import QApplication
from dotenv import load_dotenv
from app.ui import MainWindow
from app.database import create_patient_table
from app.utils.paths import resource_path  # Importamos el solucionador

def main():
    # 1. Cargar variables de entorno desde la ruta correcta (sea .exe o código)
    load_dotenv(resource_path(".env"))

    # 2. Inicializar base de datos
    create_patient_table()

    # 3. Iniciar Aplicación
    app = QApplication(sys.argv)
    
    # Opcional: Icono de la ventana principal
    # from PyQt6.QtGui import QIcon
    # app.setWindowIcon(QIcon(resource_path(os.path.join("app", "assets", "logo.ico"))))

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()