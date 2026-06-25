@echo off
setlocal

if not exist venv (
    echo No se encontro el entorno virtual.
    echo Ejecuta primero instalar.bat
    echo.
    pause
    exit /b 1
)

rem --- Verificar que el venv no este roto (p. ej. tras renombrar la carpeta) ---
venv\Scripts\python.exe -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo El entorno virtual esta roto o le faltan dependencias.
    echo Vuelve a ejecutar instalar.bat
    echo.
    pause
    exit /b 1
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Iniciando VozLab... Abre http://127.0.0.1:7860 en tu navegador.
echo (Cierra esta ventana o pulsa Ctrl+C para detener la app.)
echo.
python app.py

pause
