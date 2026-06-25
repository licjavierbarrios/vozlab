@echo off
setlocal

rem --- Detectar venv roto o de otra carpeta (los venv guardan rutas absolutas) ---
if exist venv (
    venv\Scripts\python.exe -c "import sys" >nul 2>&1
    if errorlevel 1 (
        echo El entorno virtual esta roto o fue creado en otra ruta. Recreando...
        rmdir /s /q venv
    )
)

if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias...
rem Usar "python -m pip" en vez de "pip" para no depender del PATH
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

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
