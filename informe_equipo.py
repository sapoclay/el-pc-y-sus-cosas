"""
El PC y sus cosas
Punto de entrada principal — lanza la interfaz gráfica.
"""

import os
import sys

# Asegurar que el directorio del proyecto esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import iniciar_gui


if __name__ == "__main__":
    iniciar_gui()
