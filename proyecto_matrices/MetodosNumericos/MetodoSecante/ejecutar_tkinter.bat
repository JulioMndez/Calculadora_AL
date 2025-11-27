@echo off
title Metodo de la Regla Falsa - Tkinter
echo Iniciando aplicacion con interfaz Tkinter...
python main.py --interface tkinter
if errorlevel 1 (
    echo.
    echo Error al ejecutar la aplicacion.
    pause
)