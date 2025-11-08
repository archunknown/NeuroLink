import sys
from PyQt6.QtWidgets import QApplication
from app.ui import MainWindow
from app.database import create_patient_table

def main():
    create_patient_table()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
