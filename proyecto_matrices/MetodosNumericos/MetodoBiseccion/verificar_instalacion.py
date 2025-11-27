#!/usr/bin/env python3
"""
Script de verificación de instalación
"""

import sys

def verificar_instalacion():
    print("="*60)
    print("VERIFICACIÓN DE INSTALACIÓN")
    print("="*60)
    print()
    
    # Verificar versión de Python
    print(f"Python: {sys.version}")
    if sys.version_info < (3, 7):
        print("  [ERROR] Se requiere Python 3.7 o superior")
        return False
    else:
        print("  [OK] Versión correcta")
    print()
    
    # Verificar dependencias
    dependencias = [
        ("PyQt5", "PyQt5"),
        ("matplotlib", "matplotlib"),
        ("numpy", "numpy")
    ]
    
    todas_ok = True
    
    for nombre, modulo in dependencias:
        try:
            __import__(modulo)
            print(f"{nombre}: [OK] Instalado")
        except ImportError:
            print(f"{nombre}: [ERROR] NO instalado")
            print(f"  Instalar con: pip install {modulo}")
            todas_ok = False
    
    print()
    print("="*60)
    
    if todas_ok:
        print("RESULTADO: Todas las dependencias están instaladas")
        print("Puedes ejecutar la aplicación con: python main.py")
    else:
        print("RESULTADO: Faltan dependencias")
        print("Ejecuta: pip install -r requirements.txt")
    
    print("="*60)
    
    return todas_ok

if __name__ == "__main__":
    verificar_instalacion()
