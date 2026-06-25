@echo off
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)
echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Descargando binario de whisper.cpp y modelo...
python setup_whisper.py

echo.
echo Listo. Para activar el entorno manualmente:
echo   venv\Scripts\activate.bat
echo Para arrancar la app:
echo   python app.py
echo.
pause
