@echo off
if not exist venv (
    echo No se encontro el entorno virtual.
    echo Ejecuta primero instalar.bat
    echo.
    pause
    exit /b 1
)
echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Iniciando Supertonic... Abre http://127.0.0.1:7860 en tu navegador.
echo (Cierra esta ventana o pulsa Ctrl+C para detener la app.)
echo.
python app.py

pause
