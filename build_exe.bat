@echo off
echo ==========================================
echo PREPARANDO ENTORNO DE COMPILACION
echo ==========================================

:: 1. Activar el entorno virtual
call venv\Scripts\activate

:: 2. Limpieza de archivos viejos
echo Limpiando archivos antiguos...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /f /q "*.spec"

echo ==========================================
echo INICIANDO COMPILACION (Definitiva v2)
echo ==========================================

:: 3. Compilacion con TODAS las dependencias forzadas
:: Se agrego --collect-all "pyaudio" para arreglar el microfono
pyinstaller --noconsole --clean --name "NeuroLink" ^
 --icon "app/assets/logo.ico" ^
 --add-data "app/assets;app/assets" ^
 --add-data "config.ini;." ^
 --add-data ".env;." ^
 --hidden-import "speech_recognition" ^
 --hidden-import "mediapipe.python._framework_bindings" ^
 --collect-all "mediapipe" ^
 --collect-all "cv2" ^
 --collect-all "numpy" ^
 --collect-all "speech_recognition" ^
 --collect-all "pyttsx3" ^
 --collect-all "pyaudio" ^
 main.py

echo ==========================================
echo FINALIZADO.
echo ==========================================
pause