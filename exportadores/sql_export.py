"""Exportador de informe en formato SQL para importar en base de datos."""

import platform
import datetime
import re


def _sanitizar_sql(valor: str) -> str:
    """Escapa comillas simples para valores SQL."""
    if valor is None:
        return ""
    return str(valor).replace("'", "''")


def _nombre_tabla(titulo: str) -> str:
    """Convierte un título de sección a nombre válido de tabla SQL."""
    nombre = titulo.lower()
    nombre = re.sub(r'[áà]', 'a', nombre)
    nombre = re.sub(r'[éè]', 'e', nombre)
    nombre = re.sub(r'[íì]', 'i', nombre)
    nombre = re.sub(r'[óò]', 'o', nombre)
    nombre = re.sub(r'[úù]', 'u', nombre)
    nombre = re.sub(r'[ñ]', 'n', nombre)
    nombre = re.sub(r'[^a-z0-9]+', '_', nombre)
    nombre = nombre.strip('_')
    return f"inv_{nombre}"


def _nombre_columna(clave: str) -> str:
    """Convierte una clave a nombre válido de columna SQL."""
    nombre = clave.lower()
    nombre = re.sub(r'[áà]', 'a', nombre)
    nombre = re.sub(r'[éè]', 'e', nombre)
    nombre = re.sub(r'[íì]', 'i', nombre)
    nombre = re.sub(r'[óò]', 'o', nombre)
    nombre = re.sub(r'[úù]', 'u', nombre)
    nombre = re.sub(r'[ñ]', 'n', nombre)
    nombre = re.sub(r'[^a-z0-9]+', '_', nombre)
    nombre = nombre.strip('_')
    return nombre


def exportar_sql(secciones: list[tuple], ruta: str) -> str:
    """Genera y guarda un archivo SQL con CREATE TABLE e INSERT para cada sección."""
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_equipo = _sanitizar_sql(platform.node())

    lineas = []
    lineas.append("-- ============================================================")
    lineas.append("-- EL PC Y SUS COSAS — INFORME DE INVENTARIO - Exportación SQL")
    lineas.append(f"-- Fecha: {ahora}")
    lineas.append(f"-- Equipo: {nombre_equipo}")
    lineas.append("-- ============================================================")
    lineas.append("")

    # Tabla de metadatos del informe
    lineas.append("CREATE TABLE IF NOT EXISTS inv_informe_meta (")
    lineas.append("    id INTEGER PRIMARY KEY AUTO_INCREMENT,")
    lineas.append("    nombre_equipo VARCHAR(255),")
    lineas.append("    fecha_generacion DATETIME")
    lineas.append(");")
    lineas.append("")
    lineas.append(f"INSERT INTO inv_informe_meta (nombre_equipo, fecha_generacion)")
    lineas.append(f"VALUES ('{nombre_equipo}', '{ahora}');")
    lineas.append("")

    for titulo, contenido in secciones:
        tabla = _nombre_tabla(titulo)
        lineas.append(f"-- {'─' * 60}")
        lineas.append(f"-- {titulo}")
        lineas.append(f"-- {'─' * 60}")

        if isinstance(contenido, dict):
            # Sección con un solo diccionario → una tabla clave-valor
            columnas = list(contenido.keys())
            cols_sql = [_nombre_columna(c) for c in columnas]

            lineas.append(f"CREATE TABLE IF NOT EXISTS {tabla} (")
            lineas.append("    id INTEGER PRIMARY KEY AUTO_INCREMENT,")
            lineas.append("    nombre_equipo VARCHAR(255),")
            for col in cols_sql:
                lineas.append(f"    {col} TEXT,")
            # Quitar la última coma
            lineas[-1] = lineas[-1].rstrip(",")
            lineas.append(");")
            lineas.append("")

            valores = [_sanitizar_sql(contenido[c]) for c in columnas]
            cols_str = ", ".join(["nombre_equipo"] + cols_sql)
            vals_str = ", ".join([f"'{nombre_equipo}'"] + [f"'{v}'" for v in valores])
            lineas.append(f"INSERT INTO {tabla} ({cols_str})")
            lineas.append(f"VALUES ({vals_str});")
            lineas.append("")

        elif isinstance(contenido, list) and contenido and isinstance(contenido[0], dict):
            # Lista de diccionarios → una tabla con múltiples filas
            todas_claves = []
            for elem in contenido:
                for k in elem.keys():
                    if k not in todas_claves:
                        todas_claves.append(k)

            cols_sql = [_nombre_columna(c) for c in todas_claves]

            lineas.append(f"CREATE TABLE IF NOT EXISTS {tabla} (")
            lineas.append("    id INTEGER PRIMARY KEY AUTO_INCREMENT,")
            lineas.append("    nombre_equipo VARCHAR(255),")
            for col in cols_sql:
                lineas.append(f"    {col} TEXT,")
            lineas[-1] = lineas[-1].rstrip(",")
            lineas.append(");")
            lineas.append("")

            for elem in contenido:
                valores = [_sanitizar_sql(elem.get(c, "")) for c in todas_claves]
                cols_str = ", ".join(["nombre_equipo"] + cols_sql)
                vals_str = ", ".join([f"'{nombre_equipo}'"] + [f"'{v}'" for v in valores])
                lineas.append(f"INSERT INTO {tabla} ({cols_str})")
                lineas.append(f"VALUES ({vals_str});")
            lineas.append("")

        elif isinstance(contenido, str) and contenido:
            # Texto libre → tabla con una columna de texto
            lineas.append(f"CREATE TABLE IF NOT EXISTS {tabla} (")
            lineas.append("    id INTEGER PRIMARY KEY AUTO_INCREMENT,")
            lineas.append("    nombre_equipo VARCHAR(255),")
            lineas.append("    contenido LONGTEXT")
            lineas.append(");")
            lineas.append("")
            valor = _sanitizar_sql(contenido)
            lineas.append(f"INSERT INTO {tabla} (nombre_equipo, contenido)")
            lineas.append(f"VALUES ('{nombre_equipo}', '{valor}');")
            lineas.append("")

        elif isinstance(contenido, list) and not contenido:
            lineas.append(f"-- (Sin datos para esta sección)")
            lineas.append("")

    lineas.append("-- ============================================================")
    lineas.append("-- FIN DE LA EXPORTACIÓN SQL")
    lineas.append("-- ============================================================")

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))

    return ruta
