"""Recopilador de software instalado y servicios."""

from utilidades import obtener_wmic, parsear_wmic, ejecutar_comando, ES_WINDOWS


def info_software_instalado() -> list[dict]:
    """Lista completa de programas instalados."""
    if ES_WINDOWS:
        salida = obtener_wmic("product", "Name,Version,Vendor,InstallDate")
        return parsear_wmic(salida)
    # Linux: dpkg (Debian/Ubuntu) o rpm (RHEL/Fedora)
    salida = ejecutar_comando("dpkg-query -W -f='${Package} ${Version} ${Status}\\n' 2>/dev/null")
    if not salida or "No disponible" in salida:
        salida = ejecutar_comando("rpm -qa --queryformat '%{NAME} %{VERSION}-%{RELEASE}\\n' 2>/dev/null")
    programas = []
    for linea in salida.splitlines():
        partes = linea.strip().split(None, 2)
        if len(partes) >= 2:
            prog = {"Name": partes[0], "Version": partes[1]}
            if len(partes) >= 3:
                prog["Status"] = partes[2]
            programas.append(prog)
    return programas


def info_servicios_inicio() -> list[dict]:
    """Servicios configurados para inicio automático."""
    if ES_WINDOWS:
        salida = obtener_wmic(
            'service where "StartMode=\'Auto\'"',
            "Name,DisplayName,State,StartMode"
        )
        return parsear_wmic(salida)
    # Linux: systemctl
    salida = ejecutar_comando("systemctl list-unit-files --type=service --state=enabled --no-pager 2>/dev/null")
    servicios = []
    for linea in salida.splitlines()[1:]:  # Saltar cabecera
        partes = linea.split()
        if len(partes) >= 2 and partes[0].endswith(".service"):
            servicios.append({"Name": partes[0], "State": partes[1]})
    return servicios
