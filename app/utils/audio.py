import pyttsx3
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import pythoncom

class TTSWorker(QObject):
    """
    Worker que ejecuta la síntesis de voz en un hilo separado.
    """
    finished = pyqtSignal()

    def __init__(self, text_to_speak):
        super().__init__()
        self.text_to_speak = text_to_speak

    def run(self):
        """Inicializa pyttsx3 y habla el texto."""
        try:
            pythoncom.CoInitialize()
            engine = pyttsx3.init()
            
            # Opcional: Configurar propiedades de la voz
            voices = engine.getProperty('voices')
            
            engine.setProperty('rate', 160)  # Velocidad del habla
            engine.setProperty('volume', 0.9) # Volumen (0.0 a 1.0)
            
            engine.say(self.text_to_speak)
            engine.runAndWait()
        except Exception as e:
            print(f"Error en el worker de TTS: {e}")
        finally:
            pythoncom.CoUninitialize()
            self.finished.emit()

def speak(text, parent):
    """
    Función de utilidad para hablar un texto sin bloquear la UI.
    Crea un hilo y un worker para realizar el trabajo.
    
    Args:
        text (str): El texto a ser hablado.
        parent (QWidget): El widget padre, usado para la gestión del hilo.
    """
    # Crear el hilo y el worker
    thread = QThread(parent)
    worker = TTSWorker(text)
    worker.moveToThread(thread)

    # Conectar señales
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    
    # CRITICAL FIX: Keep worker alive!
    thread.worker_ref = worker

    # Iniciar el hilo
    thread.start()
    
    # Guardar una referencia al hilo en el padre para evitar que sea eliminado por el recolector de basura
    parent.tts_thread = thread
