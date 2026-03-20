"""Recopilador de información de hardware: CPU, RAM, discos, GPU, monitor, sonido, batería."""

from utilidades import obtener_wmic, parsear_wmic, bytes_a_gb, ejecutar_comando, parsear_lista_linux, ES_WINDOWS


def info_procesador() -> list[dict]:
    """Información del procesador."""
    if ES_WINDOWS:
        salida = obtener_wmic(
            "cpu",
            "Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,Manufacturer,Architecture"
        )
        return parsear_wmic(salida)
    salida = ejecutar_comando("lscpu")
    datos = {}
    for linea in salida.splitlines():
        if ":" in linea:
            clave, _, valor = linea.partition(":")
            datos[clave.strip()] = valor.strip()
    return [datos] if datos else []


def info_memoria_ram() -> list[dict]:
    """Módulos de memoria RAM instalados."""
    if ES_WINDOWS:
        salida = obtener_wmic(
            "memorychip",
            "BankLabel,Capacity,Speed,Manufacturer,PartNumber,SerialNumber,DeviceLocator"
        )
        modulos = parsear_wmic(salida)
        for m in modulos:
            if "Capacity" in m:
                m["Capacity"] = bytes_a_gb(m["Capacity"])
        return modulos
    # Linux: leer desde /proc/meminfo + dmidecode
    salida = ejecutar_comando("cat /proc/meminfo")
    datos = {}
    for linea in salida.splitlines():
        if linea.startswith("MemTotal:"):
            datos["MemTotal"] = linea.split(":")[1].strip()
        elif linea.startswith("MemAvailable:"):
            datos["MemAvailable"] = linea.split(":")[1].strip()
        elif linea.startswith("SwapTotal:"):
            datos["SwapTotal"] = linea.split(":")[1].strip()
    # Intentar dmidecode para detalles de módulos
    detalle = ejecutar_comando("sudo dmidecode -t memory 2>/dev/null | grep -A6 'Memory Device' | head -40")
    if detalle and "Requiere" not in detalle:
        datos["Detalle módulos"] = detalle
    return [datos] if datos else []


def info_discos() -> list[dict]:
    """Discos duros físicos."""
    if ES_WINDOWS:
        salida = obtener_wmic(
            "diskdrive",
            "Model,Size,InterfaceType,MediaType,SerialNumber,Partitions,Status"
        )
        discos = parsear_wmic(salida)
        for d in discos:
            if "Size" in d:
                d["Size"] = bytes_a_gb(d["Size"])
        return discos
    salida = ejecutar_comando("lsblk -d -o NAME,SIZE,MODEL,ROTA,TYPE,TRAN -n")
    discos = []
    for linea in salida.splitlines():
        partes = linea.split(None, 5)
        if len(partes) >= 2:
            disco = {"Name": partes[0], "Size": partes[1]}
            if len(partes) >= 3:
                disco["Model"] = partes[2]
            if len(partes) >= 4:
                disco["Rotacional"] = "HDD" if partes[3] == "1" else "SSD"
            if len(partes) >= 5:
                disco["Type"] = partes[4]
            if len(partes) >= 6:
                disco["Transport"] = partes[5]
            discos.append(disco)
    return discos


def info_particiones() -> list[dict]:
    """Particiones / unidades lógicas."""
    if ES_WINDOWS:
        salida = obtener_wmic(
            "logicaldisk",
            "DeviceID,FileSystem,Size,FreeSpace,VolumeName,DriveType"
        )
        particiones = parsear_wmic(salida)
        tipos_disco = {
            "0": "Desconocido", "1": "Sin raíz", "2": "Extraíble",
            "3": "Disco local", "4": "Red", "5": "CD/DVD", "6": "RAM"
        }
        for p in particiones:
            if "Size" in p:
                p["Size"] = bytes_a_gb(p["Size"])
            if "FreeSpace" in p:
                p["FreeSpace"] = bytes_a_gb(p["FreeSpace"])
            if "DriveType" in p:
                p["DriveType"] = tipos_disco.get(p["DriveType"], p["DriveType"])
        return particiones
    salida = ejecutar_comando("df -hT --output=source,fstype,size,used,avail,pcent,target 2>/dev/null || df -hT")
    particiones = []
    for linea in salida.splitlines()[1:]:  # Saltar cabecera
        partes = linea.split(None, 6)
        if len(partes) >= 7:
            particiones.append({
                "Dispositivo": partes[0], "Sistema archivos": partes[1],
                "Tamaño": partes[2], "Usado": partes[3],
                "Disponible": partes[4], "Uso %": partes[5],
                "Montaje": partes[6],
            })
    return particiones


def info_gpu() -> list[dict]:
    """Tarjetas gráficas."""
    if ES_WINDOWS:
        salida = obtener_wmic(
            "path win32_videocontroller",
            "Name,AdapterRAM,DriverVersion,VideoProcessor,CurrentHorizontalResolution,CurrentVerticalResolution"
        )
        gpus = parsear_wmic(salida)
        for g in gpus:
            if "AdapterRAM" in g:
                g["AdapterRAM"] = bytes_a_gb(g["AdapterRAM"])
        return gpus
    salida = ejecutar_comando("lspci 2>/dev/null | grep -iE 'vga|3d|display'")
    gpus = []
    for linea in salida.splitlines():
        if linea.strip():
            gpus.append({"GPU": linea.strip()})
    if not gpus:
        gpus = [{"GPU": "No detectada (lspci no disponible)"}]
    return gpus


def info_monitor() -> list[dict]:
    """Monitores conectados."""
    if ES_WINDOWS:
        salida = obtener_wmic(
            "desktopmonitor",
            "Name,MonitorManufacturer,ScreenHeight,ScreenWidth"
        )
        return parsear_wmic(salida)
    salida = ejecutar_comando("xrandr --query 2>/dev/null | grep ' connected'")
    monitores = []
    for linea in salida.splitlines():
        if linea.strip():
            monitores.append({"Monitor": linea.strip()})
    return monitores if monitores else [{"Monitor": "No detectado (sin servidor X)"}]


def info_sonido() -> list[dict]:
    """Dispositivos de sonido."""
    if ES_WINDOWS:
        salida = obtener_wmic("sounddev", "Name,Manufacturer,Status")
        return parsear_wmic(salida)
    salida = ejecutar_comando("cat /proc/asound/cards 2>/dev/null")
    if not salida or "No disponible" in salida:
        salida = ejecutar_comando("aplay -l 2>/dev/null")
    dispositivos = []
    for linea in salida.splitlines():
        if linea.strip():
            dispositivos.append({"Dispositivo": linea.strip()})
    return dispositivos if dispositivos else [{"Info": "No se detectaron dispositivos de sonido"}]


def info_bateria() -> list[dict]:
    """Información de batería (portátiles)."""
    if ES_WINDOWS:
        salida = obtener_wmic(
            "path Win32_Battery",
            "Name,EstimatedChargeRemaining,BatteryStatus,DesignVoltage"
        )
        return parsear_wmic(salida)
    ruta_bat = "/sys/class/power_supply/BAT0"
    salida_check = ejecutar_comando(f"test -d {ruta_bat} && echo SI || echo NO")
    if "SI" not in salida_check:
        return [{"Info": "No se detectó batería"}]
    datos = {}
    for campo, archivo in [("Estado", "status"), ("Capacidad %", "capacity"),
                           ("Tipo", "type"), ("Tecnología", "technology")]:
        val = ejecutar_comando(f"cat {ruta_bat}/{archivo} 2>/dev/null")
        if val and "No disponible" not in val:
            datos[campo] = val
    return [datos] if datos else []
