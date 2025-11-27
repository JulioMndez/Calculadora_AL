#!/usr/bin/env python3
"""
Método de NewtonRaphson
Autor: Grupo 4
Versión: 2.0

Módulos:
- matematicas.py: Funciones matemáticas y validación
- grafico.py: Funciones de graficación
- interfaz.py: Interfaz Tkinter (original)
- interfaz_pyqt.py: Interfaz PyQt5 (moderna)
"""

import sys
import argparse

def main():
    """Función principal de la aplicación"""
    parser = argparse.ArgumentParser(description='Método de la Regla Falsa')
    parser.add_argument('--interface', '-i', choices=['tkinter', 'pyqt'], default='pyqt',
                       help='Seleccionar interfaz: tkinter (original) o pyqt (moderna)')
    
    args = parser.parse_args()
    
    try:
        if args.interface == 'tkinter':
            from interfaz_pyqt import InterfazReglaFalsaPyQt as InterfazReglaFalsa
            app = InterfazReglaFalsa()
            app.ejecutar()
        else:  # pyqt
            from interfaz_pyqt import main as pyqt_main
            pyqt_main()
            
    except ImportError as e:
        print(f"Error: No se pudo importar la interfaz {args.interface}")
        print(f"Detalles: {e}")
        if args.interface == 'pyqt':
            print("Instala PyQt5 con: pip install PyQt5")
        sys.exit(1)
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()