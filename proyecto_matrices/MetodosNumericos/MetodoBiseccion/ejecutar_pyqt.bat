@echo off
title Metodo de Biseccion - PyQt5
echo Iniciando aplicacion con interfaz PyQt5...
python main.py
if errorlevel 1 (
    echo.
    echo Error al ejecutar la aplicacion.
    echo Verifica que las dependencias esten instaladas:
    echo   pip install -r requirements.txt
    echo.
    pause
)