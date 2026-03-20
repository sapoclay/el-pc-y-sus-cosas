"""Funciones de utilidad compartidas por todos los módulos."""

import subprocess
import platform

ES_WINDOWS = platform.system().lower() == "windows"
ES_LINUX = platform.system().lower() == "linux"


def ejecutar_comando(comando: str, timeout: int = 30) -> str:
    """Ejecuta un comando del sistema y devuelve la salida como texto."""
    try:
        resultado = subprocess.run(
            comando, capture_output=True, text=True,
            shell=True, timeout=timeout,
            encoding="oem" if ES_WINDOWS else "utf-8",
            errors="replace"
        )
        return resultado.stdout.strip()
    except Exception:
        return "No disponible"


def obtener_wmic(clase: str, campos: str) -> str:
    """Consulta WMI a través de wmic (solo Windows)."""
    if not ES_WINDOWS:
        return ""
    return ejecutar_comando(f'wmic {clase} get {campos} /format:list')


def parsear_wmic(salida: str) -> list[dict]:
    """Parsea la salida de wmic /format:list en una lista de diccionarios."""
    elementos = []
    actual = {}
    for linea in salida.splitlines():
        linea = linea.strip()
        if "=" in linea:
            clave, _, valor = linea.partition("=")
            clave = clave.strip()
            if clave in actual:
                elementos.append(actual)
                actual = {}
            actual[clave] = valor.strip()
    if actual:
        elementos.append(actual)
    return elementos


def parsear_lista_linux(salida: str) -> list[dict]:
    """Parsea salidas tipo 'clave: valor' separadas por líneas en blanco."""
    elementos = []
    actual = {}
    for linea in salida.splitlines():
        linea = linea.strip()
        if ":" in linea:
            clave, _, valor = linea.partition(":")
            actual[clave.strip()] = valor.strip()
        elif not linea and actual:
            elementos.append(actual)
            actual = {}
    if actual:
        elementos.append(actual)
    return elementos


def bytes_a_gb(valor: str) -> str:
    """Convierte bytes (string) a GB con 2 decimales."""
    try:
        return f"{int(valor) / (1024**3):.2f} GB"
    except (ValueError, TypeError):
        return valor


def abrir_ruta(ruta: str):
    """Abre un archivo o carpeta con la aplicación predeterminada del SO."""
    import webbrowser
    if ES_WINDOWS:
        import os
        os.startfile(ruta)
    else:
        subprocess.Popen(["xdg-open", ruta], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
