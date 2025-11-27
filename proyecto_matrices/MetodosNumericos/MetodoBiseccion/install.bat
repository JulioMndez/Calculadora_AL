@echo off
echo ========================================
echo  Instalador - Metodo de Biseccion
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

echo Python encontrado!
python --version

echo.
echo Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: No se pudieron instalar las dependencias
    echo Intentando con --user...
    pip install --user -r requirements.txt
)

echo.
echo ========================================
echo  Instalacion completada!
echo ========================================
echo.
echo Para ejecutar la aplicacion:
echo   - Interfaz PyQt5 (recomendada): python main.py
echo   - Interfaz Tkinter (clasica):   python main.py --interface tkinter
echo.
pause