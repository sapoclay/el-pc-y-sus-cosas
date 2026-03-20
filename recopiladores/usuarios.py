"""Recopilador de usuarios del sistema y sus privilegios."""

from utilidades import ejecutar_comando, parsear_wmic, obtener_wmic, ES_WINDOWS


def info_usuarios() -> list[dict]:
    """Lista de usuarios locales con información de cuenta."""
    if ES_WINDOWS:
        salida = obtener_wmic(
            "useraccount where \"LocalAccount=TRUE\"",
            "Name,FullName,Description,Status,Disabled,Lockout,SID"
        )
        usuarios = parsear_wmic(salida)
        for u in usuarios:
            if "Disabled" in u:
                u["Disabled"] = "Sí" if u["Disabled"].upper() == "TRUE" else "No"
            if "Lockout" in u:
                u["Lockout"] = "Sí" if u["Lockout"].upper() == "TRUE" else "No"
        return usuarios
    # Linux: leer /etc/passwd
    salida = ejecutar_comando("cat /etc/passwd")
    usuarios = []
    for linea in salida.splitlines():
        partes = linea.split(":")
        if len(partes) >= 7:
            uid = int(partes[2]) if partes[2].isdigit() else -1
            usuarios.append({
                "Name": partes[0],
                "UID": partes[2],
                "GID": partes[3],
                "Descripción": partes[4],
                "Home": partes[5],
                "Shell": partes[6],
                "Tipo": "Sistema" if uid < 1000 and uid != 0 else ("root" if uid == 0 else "Usuario"),
            })
    return usuarios


def info_grupos_usuario() -> list[dict]:
    """Grupos locales y sus miembros (muestra privilegios)."""
    if ES_WINDOWS:
        salida_grupos = ejecutar_comando(
            'powershell -Command "'
            "Get-LocalGroup | ForEach-Object { "
            "$grupo = $_.Name; "
            "try { $miembros = (Get-LocalGroupMember -Group $grupo -ErrorAction SilentlyContinue | "
            "Select-Object -ExpandProperty Name) -join ', '; } "
            "catch { $miembros = '(sin acceso)'; }; "
            "[PSCustomObject]@{ Grupo = $grupo; Miembros = $miembros } "
            '} | Format-List"'
        )
        grupos = []
        actual = {}
        for linea in salida_grupos.splitlines():
            linea = linea.strip()
            if ":" in linea:
                clave, _, valor = linea.partition(":")
                actual[clave.strip()] = valor.strip()
            elif not linea and actual:
                grupos.append(actual)
                actual = {}
        if actual:
            grupos.append(actual)
        return grupos
    # Linux: leer /etc/group
    salida = ejecutar_comando("cat /etc/group")
    grupos = []
    for linea in salida.splitlines():
        partes = linea.split(":")
        if len(partes) >= 4:
            grupos.append({
                "Grupo": partes[0],
                "GID": partes[2],
                "Miembros": partes[3] if partes[3] else "(ninguno)",
            })
    return grupos


def info_privilegios_usuarios() -> list[dict]:
    """Detalle de cada usuario con sus grupos (privilegios)."""
    if ES_WINDOWS:
        usuarios = info_usuarios()
        for usuario in usuarios:
            nombre = usuario.get("Name", "")
            if nombre:
                salida = ejecutar_comando(
                    f'powershell -Command "'
                    f"try {{ (Get-LocalGroup | Where-Object {{ "
                    f"(Get-LocalGroupMember -Group $_.Name -ErrorAction SilentlyContinue).Name -like '*\\{nombre}' "
                    f"}}).Name -join ', ' }} catch {{ '(sin acceso)' }}"
                    f'"'
                )
                usuario["Grupos / Privilegios"] = salida if salida else "(ninguno)"
                es_admin = "Administrators" in salida or "Administradores" in salida
                usuario["Es Administrador"] = "Sí" if es_admin else "No"
        return usuarios
    # Linux: listar usuarios normales + root con sus grupos
    salida = ejecutar_comando("cat /etc/passwd")
    usuarios = []
    for linea in salida.splitlines():
        partes = linea.split(":")
        if len(partes) >= 7:
            uid = int(partes[2]) if partes[2].isdigit() else -1
            if uid == 0 or uid >= 1000:  # root + usuarios normales
                nombre = partes[0]
                grupos = ejecutar_comando(f"groups {nombre} 2>/dev/null")
                es_sudo = "sudo" in grupos or "wheel" in grupos or "root" in grupos.split(":")[0] if ":" in grupos else nombre == "root"
                usuarios.append({
                    "Name": nombre,
                    "UID": partes[2],
                    "Home": partes[5],
                    "Shell": partes[6],
                    "Grupos / Privilegios": grupos.split(":")[-1].strip() if ":" in grupos else grupos,
                    "Es Administrador": "Sí" if es_sudo else "No",
                })
    return usuarios
