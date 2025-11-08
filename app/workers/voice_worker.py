import speech_recognition as sr
from PyQt6.QtCore import QObject, pyqtSignal

class VoiceWorker(QObject):
    """
    Worker that listens for voice input in a continuous loop and emits recognized text.
    Runs in a separate thread to avoid freezing the UI.
    """
    listening = pyqtSignal()
    processing = pyqtSignal()
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.mic_available = False
        self._is_running = True
        try:
            self.microphone = sr.Microphone()
            self.mic_available = True
        except (OSError, Exception):
            self.mic_available = False

    def run(self):
        """
        Listens for utterances in a loop until stopped.
        """
        if not self.mic_available:
            self.error.emit("No se encontró un micrófono.")
            return

        while self._is_running:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.listening.emit()
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                self.processing.emit()
                text = self.recognizer.recognize_google(audio, language="es-ES")
                if self._is_running: # Check again in case stop was called during recognition
                    self.finished.emit(text)

            except sr.WaitTimeoutError:
                # This is not a critical error, just means no speech was detected.
                # The loop will simply continue listening.
                if self._is_running:
                    self.error.emit("No se detectó voz. Vuelve a intentarlo.")
                continue
            except (sr.UnknownValueError, sr.RequestError) as e:
                if self._is_running:
                    self.error.emit(f"Error de reconocimiento: {e}")
                continue
            except Exception as e:
                if self._is_running:
                    self.error.emit(f"Error inesperado: {e}")
                break # Break on unexpected errors

    def stop(self):
        """Stops the listening loop."""
        self._is_running = False
