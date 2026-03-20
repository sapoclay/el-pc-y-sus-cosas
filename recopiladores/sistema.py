"""Recopilador de información del sistema operativo, BIOS y placa base."""

import platform
import os

from utilidades import obtener_wmic, parsear_wmic, ejecutar_comando, parsear_lista_linux, ES_WINDOWS


def info_sistema() -> dict:
    """Información general del sistema operativo y equipo."""
    datos = {
        "Nombre del equipo": platform.node(),
        "Sistema operativo": f"{platform.system()} {platform.release()}",
        "Versión SO": platform.version(),
        "Arquitectura": platform.machine(),
        "Procesador (platform)": platform.processor(),
        "Usuario actual": os.getlogin(),
    }
    if not ES_WINDOWS:
        # Añadir info de distribución Linux
        distro = ejecutar_comando("cat /etc/os-release")
        for linea in distro.splitlines():
            if linea.startswith("PRETTY_NAME="):
                datos["Distribución"] = linea.split("=", 1)[1].strip('"')
                break
        datos["Kernel"] = ejecutar_comando("uname -r")
    return datos


def info_bios() -> list[dict]:
    """Información de la BIOS."""
    if ES_WINDOWS:
        salida = obtener_wmic("bios", "Manufacturer,Name,SerialNumber,Version,ReleaseDate")
        return parsear_wmic(salida)
    # Linux: dmidecode requiere root, intentar con sudo
    salida = ejecutar_comando("sudo dmidecode -t bios 2>/dev/null || echo 'Requiere permisos de root'")
    if "Requiere permisos" in salida or not salida:
        return [{"Info": "Ejecutar con sudo para obtener datos de BIOS"}]
    return parsear_lista_linux(salida)


def info_placa_base() -> list[dict]:
    """Información de la placa base."""
    if ES_WINDOWS:
        salida = obtener_wmic("baseboard", "Manufacturer,Product,SerialNumber,Version")
        return parsear_wmic(salida)
    salida = ejecutar_comando("sudo dmidecode -t baseboard 2>/dev/null || echo 'Requiere permisos de root'")
    if "Requiere permisos" in salida or not salida:
        return [{"Info": "Ejecutar con sudo para obtener datos de placa base"}]
    return parsear_lista_linux(salida)
