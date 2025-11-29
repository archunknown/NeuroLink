@echo off
echo ==========================================
echo PREPARANDO ENTORNO DE COMPILACION
echo ==========================================

:: 1. Activar el entorno virtual (CRUCIAL)
call venv\Scripts\activate

:: 2. Instalar PyInstaller en el entorno virtual si no existe
pip install pyinstaller

:: 3. Limpiar carpetas de compilaciones anteriores para evitar errores fantasmas
echo Limpiando archivos antiguos...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /f /q "*.spec"

echo ==========================================
echo INICIANDO COMPILACION (Modo Cliente)
echo ==========================================

:: 4. Ejecutar PyInstaller
:: Se agrego --clean para purgar cache
pyinstaller --noconsole --clean --name "NeuroLink" ^
 --icon "app/assets/logo.ico" ^
 --add-data "app/assets;app/assets" ^
 --add-data "config.ini;." ^
 --add-data ".env;." ^
 --hidden-import "speech_recognition" ^
 --collect-all "mediapipe" ^
 --collect-all "speech_recognition" ^
 --collect-all "pyttsx3" ^
 main.py

echo ==========================================
echo FINALIZADO. Verifique la carpeta 'dist'.
echo ==========================================
pause