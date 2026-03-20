"""Exportador de informe en formato texto plano (.txt)."""

import platform
import datetime


def seccion_txt(titulo: str, contenido) -> str:
    """Formatea una sección del informe en texto plano."""
    lineas = []
    lineas.append("")
    lineas.append("=" * 70)
    lineas.append(f"  {titulo}")
    lineas.append("=" * 70)

    if isinstance(contenido, dict):
        for k, v in contenido.items():
            lineas.append(f"  {k}: {v}")
    elif isinstance(contenido, list):
        if not contenido:
            lineas.append("  (Sin datos)")
        for i, elem in enumerate(contenido, 1):
            if isinstance(elem, dict):
                lineas.append(f"  --- Elemento {i} ---")
                for k, v in elem.items():
                    lineas.append(f"    {k}: {v}")
            else:
                lineas.append(f"  {elem}")
    elif isinstance(contenido, str):
        for linea in contenido.splitlines():
            lineas.append(f"  {linea}")
    else:
        lineas.append(f"  {contenido}")

    return "\n".join(lineas)


def exportar_txt(secciones: list[tuple], ruta: str) -> str:
    """Genera y guarda el informe en texto plano. Devuelve la ruta del archivo."""
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_equipo = platform.node()

    txt = []
    txt.append("*" * 70)
    txt.append("  EL PC Y SUS COSAS — INFORME DE INVENTARIO")
    txt.append(f"  Fecha de generación: {ahora}")
    txt.append(f"  Equipo: {nombre_equipo}")
    txt.append("*" * 70)

    for titulo, contenido in secciones:
        txt.append(seccion_txt(titulo, contenido))

    txt.append("\n" + "=" * 70)
    txt.append("  FIN DEL INFORME")
    txt.append("=" * 70)

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(txt))

    return ruta
