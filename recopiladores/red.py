"""Recopilador de información de red."""

import socket
import uuid

from utilidades import ejecutar_comando, obtener_wmic, parsear_wmic, ES_WINDOWS


def info_red() -> dict:
    """Información de red: IP, MAC, hostname, FQDN, dominio/grupo de trabajo."""
    datos = {
        "Nombre de host": socket.gethostname(),
        "Dirección MAC": ":".join(
            f"{(uuid.getnode() >> i) & 0xff:02x}" for i in range(0, 48, 8)
        ),
    }
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        datos["IP local"] = s.getsockname()[0]
        s.close()
    except Exception:
        datos["IP local"] = "No disponible"

    try:
        datos["FQDN"] = socket.getfqdn()
    except Exception:
        datos["FQDN"] = "No disponible"

    # Dominio o grupo de trabajo
    if ES_WINDOWS:
        salida = obtener_wmic("computersystem", "Domain,PartOfDomain")
        parsed = parsear_wmic(salida)
        if parsed:
            info = parsed[0]
            dominio = info.get("Domain", "No disponible")
            en_dominio = info.get("PartOfDomain", "").upper() == "TRUE"
            datos["Dominio / Grupo de trabajo"] = dominio
            datos["Tipo de pertenencia"] = "Dominio" if en_dominio else "Grupo de trabajo"
        else:
            datos["Dominio / Grupo de trabajo"] = "No disponible"
            datos["Tipo de pertenencia"] = "No disponible"
    else:
        # Linux: comprobar si está unido a un dominio (realm/samba)
        realm = ejecutar_comando("realm list --name-only 2>/dev/null")
        if realm and realm != "No disponible":
            datos["Dominio / Grupo de trabajo"] = realm
            datos["Tipo de pertenencia"] = "Dominio"
        else:
            wb = ejecutar_comando("cat /etc/samba/smb.conf 2>/dev/null | grep -i 'workgroup' | head -1")
            if wb and "=" in wb:
                datos["Dominio / Grupo de trabajo"] = wb.split("=", 1)[1].strip()
                datos["Tipo de pertenencia"] = "Grupo de trabajo"
            else:
                datos["Dominio / Grupo de trabajo"] = "WORKGROUP"
                datos["Tipo de pertenencia"] = "Grupo de trabajo"

    return datos


def info_adaptadores_red() -> list[dict]:
    """Adaptadores de red activos."""
    if ES_WINDOWS:
        salida = obtener_wmic(
            'nic where "NetEnabled=true"',
            "Name,MACAddress,Speed,NetConnectionID,AdapterType"
        )
        adaptadores = parsear_wmic(salida)
        for a in adaptadores:
            if "Speed" in a and a["Speed"]:
                try:
                    a["Speed"] = f"{int(a['Speed']) / 1_000_000:.0f} Mbps"
                except ValueError:
                    pass
        return adaptadores
    # Linux: ip link
    salida = ejecutar_comando("ip -o link show up")
    adaptadores = []
    for linea in salida.splitlines():
        partes = linea.split(":")
        if len(partes) >= 2:
            nombre = partes[1].strip().split("@")[0]
            mac = ""
            if "link/ether" in linea:
                idx = linea.index("link/ether") + len("link/ether ")
                mac = linea[idx:idx + 17]
            adaptadores.append({"Name": nombre, "MACAddress": mac})
    return adaptadores


def info_ip_config() -> str:
    """Configuración IP completa."""
    if ES_WINDOWS:
        return ejecutar_comando("ipconfig /all")
    return ejecutar_comando("ip addr show")


def info_dispositivos_red_local() -> str:
    """Tabla ARP: dispositivos detectados en la red local."""
    if ES_WINDOWS:
        return ejecutar_comando("arp -a")
    return ejecutar_comando("ip neigh show 2>/dev/null || arp -a")
