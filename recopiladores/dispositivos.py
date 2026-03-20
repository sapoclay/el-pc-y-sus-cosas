"""Recopilador de dispositivos conectados: USB e impresoras."""

from utilidades import ejecutar_comando, obtener_wmic, parsear_wmic, parsear_lista_linux, ES_WINDOWS


def info_dispositivos_usb() -> list[dict]:
    """Dispositivos USB conectados."""
    if ES_WINDOWS:
        salida2 = ejecutar_comando(
            'powershell -Command "Get-PnpDevice -PresentOnly | '
            "Where-Object { $_.InstanceId -like 'USB*' } | "
            "Select-Object Status, Class, FriendlyName, InstanceId | "
            'Format-List"'
        )
        dispositivos = []
        actual = {}
        for linea in salida2.splitlines():
            linea = linea.strip()
            if ":" in linea:
                clave, _, valor = linea.partition(":")
                actual[clave.strip()] = valor.strip()
            elif not linea and actual:
                dispositivos.append(actual)
                actual = {}
        if actual:
            dispositivos.append(actual)
        return dispositivos
    # Linux: lsusb
    salida = ejecutar_comando("lsusb 2>/dev/null")
    dispositivos = []
    for linea in salida.splitlines():
        if linea.strip():
            dispositivos.append({"Dispositivo USB": linea.strip()})
    return dispositivos if dispositivos else [{"Info": "lsusb no disponible"}]


def info_impresoras() -> list[dict]:
    """Impresoras instaladas."""
    if ES_WINDOWS:
        salida = obtener_wmic("printer", "Name,DriverName,PortName,Default,Shared")
        return parsear_wmic(salida)
    # Linux: lpstat (CUPS)
    salida = ejecutar_comando("lpstat -p -d 2>/dev/null")
    if not salida or "No disponible" in salida:
        return [{"Info": "No se detectaron impresoras (CUPS no instalado)"}]
    impresoras = []
    for linea in salida.splitlines():
        if linea.strip():
            impresoras.append({"Impresora": linea.strip()})
    return impresoras
