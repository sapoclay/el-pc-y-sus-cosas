"""Exportador de informe en formato HTML."""

import datetime
import html as html_mod
import platform
import re
import unicodedata


def _slugify(texto: str) -> str:
    """Genera un identificador HTML legible a partir de un título."""
    texto_normalizado = unicodedata.normalize("NFKD", texto)
    texto_ascii = texto_normalizado.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", texto_ascii.lower()).strip("-")
    return slug or "seccion"


def _resumen_contenido(contenido) -> str:
    """Describe el tipo y el volumen de datos de una sección."""
    if isinstance(contenido, dict):
        total = len(contenido)
        return f"{total} campo{'s' if total != 1 else ''}"
    if isinstance(contenido, list):
        total = len(contenido)
        return f"{total} elemento{'s' if total != 1 else ''}"
    if isinstance(contenido, str):
        lineas = len(contenido.splitlines()) or 1
        return f"{lineas} línea{'s' if lineas != 1 else ''}"
    return "Dato único"


def _contar_bloques(secciones: list[tuple]) -> tuple[int, int]:
    """Cuenta secciones y elementos visibles para mostrar un resumen superior."""
    total_secciones = len(secciones)
    total_bloques = 0
    for _, contenido in secciones:
        if isinstance(contenido, list):
            total_bloques += len(contenido)
        elif isinstance(contenido, dict):
            total_bloques += len(contenido)
        else:
            total_bloques += 1
    return total_secciones, total_bloques


def _valor_html(valor) -> str:
    """Formatea un valor para hacerlo más legible en HTML."""
    texto = html_mod.escape(str(valor))
    if "\n" in str(valor):
        return f'<pre class="valor-multilinea">{texto}</pre>'
    if len(str(valor)) > 140:
        return f'<div class="valor-expandido">{texto}</div>'
    return texto


def _tabla_html(datos: dict) -> str:
    """Renderiza un diccionario como tabla de pares clave/valor."""
    filas = []
    for clave, valor in datos.items():
        filas.append(
            "<tr>"
            f"<th scope=\"row\" class=\"clave\">{html_mod.escape(str(clave))}</th>"
            f"<td>{_valor_html(valor)}</td>"
            "</tr>"
        )
    return (
        '<div class="tabla-wrapper">'
        '<table class="tabla-datos">'
        '<tbody>'
        + "".join(filas)
        + '</tbody></table></div>'
    )


def _lista_html(elementos: list) -> str:
    """Renderiza listas como tarjetas o listas compactas según su contenido."""
    if not elementos:
        return '<p class="vacio"><em>Sin datos</em></p>'

    if all(isinstance(elem, dict) for elem in elementos):
        tarjetas = []
        for indice, elem in enumerate(elementos, 1):
            total_campos = len(elem)
            etiqueta = f'{total_campos} campo' + ('s' if total_campos != 1 else '')
            tarjetas.append(
                '<article class="tarjeta-elemento">'
                '<div class="tarjeta-cabecera">'
                f'<h3>Elemento {indice}</h3>'
                f'<span class="etiqueta">{etiqueta}</span>'
                '</div>'
                f'{_tabla_html(elem)}'
                '</article>'
            )
        return '<div class="rejilla-elementos">' + "".join(tarjetas) + '</div>'

    items = []
    for elem in elementos:
        items.append(f'<li>{_valor_html(elem)}</li>')
    return '<ul class="lista-simple">' + "".join(items) + '</ul>'


def _contenido_html(contenido) -> str:
    """Elige la representación HTML adecuada según el tipo de dato."""
    if isinstance(contenido, dict):
        return _tabla_html(contenido)
    if isinstance(contenido, list):
        return _lista_html(contenido)
    if isinstance(contenido, str):
        if "\n" in contenido:
            return f'<pre>{html_mod.escape(contenido)}</pre>'
        return f'<p class="texto-plano">{html_mod.escape(contenido)}</p>'
    return f'<p class="texto-plano">{html_mod.escape(str(contenido))}</p>'


def seccion_html(titulo: str, contenido) -> str:
    """Formatea una sección del informe en HTML."""
    ancla = _slugify(titulo)
    resumen = _resumen_contenido(contenido)
    return (
        f'<section id="{ancla}" class="seccion">'
        '<div class="seccion-cabecera">'
        f'<div><h2>{html_mod.escape(titulo)}</h2><p class="seccion-resumen">{html_mod.escape(resumen)}</p></div>'
        f'<a class="ancla" href="#{ancla}" aria-label="Enlace a {html_mod.escape(titulo)}">#</a>'
        '</div>'
        f'{_contenido_html(contenido)}'
        '</section>'
    )


def exportar_html(secciones: list[tuple], ruta: str) -> str:
    """Genera y guarda el informe en HTML. Devuelve la ruta del archivo."""
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_equipo = html_mod.escape(platform.node())
    total_secciones, total_bloques = _contar_bloques(secciones)
    enlaces = []
    for titulo, contenido in secciones:
        ancla = _slugify(titulo)
        resumen = _resumen_contenido(contenido)
        enlaces.append(
            '<a class="indice-item" href="#' + ancla + '">'
            f'<span class="indice-titulo">{html_mod.escape(titulo)}</span>'
            f'<span class="indice-meta">{html_mod.escape(resumen)}</span>'
            '</a>'
        )

    partes = []
    partes.append(f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>El PC y sus cosas — Informe de {nombre_equipo}</title>
<style>
    :root {{
        --fondo: #f3f6fb;
        --panel: #ffffff;
        --panel-secundario: #f8fbff;
        --borde: #d7e3f0;
        --texto: #22313f;
        --texto-suave: #5b6b79;
        --marca: #0b6aa2;
        --marca-suave: #e5f3fb;
        --sombra: 0 12px 30px rgba(33, 65, 98, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
        margin: 0;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        background:
            radial-gradient(circle at top left, rgba(11, 106, 162, 0.08), transparent 18%),
            linear-gradient(180deg, #f7fbff 0%, var(--fondo) 100%);
        color: var(--texto);
        line-height: 1.5;
    }}
    .pagina {{ max-width: 1400px; margin: 0 auto; padding: 32px 20px 48px; }}
    .hero {{
        background: linear-gradient(135deg, #ffffff 0%, #eef7ff 100%);
        border: 1px solid var(--borde);
        border-radius: 20px;
        padding: 28px;
        box-shadow: var(--sombra);
        margin-bottom: 24px;
    }}
    .hero h1 {{ margin: 0 0 10px; color: var(--marca); font-size: clamp(1.8rem, 3vw, 2.7rem); }}
    .meta {{ color: var(--texto-suave); margin: 0 0 18px; }}
    .resumen-superior {{ display: flex; flex-wrap: wrap; gap: 12px; }}
    .dato-resumen {{
        background: var(--panel);
        border: 1px solid var(--borde);
        border-radius: 14px;
        padding: 12px 14px;
        min-width: 180px;
    }}
    .dato-resumen strong {{ display: block; color: var(--marca); font-size: 1.1rem; }}
    .dato-resumen span {{ color: var(--texto-suave); font-size: 0.92rem; }}
    .indice {{
        position: sticky;
        top: 0;
        z-index: 2;
        background: rgba(243, 246, 251, 0.94);
        backdrop-filter: blur(12px);
        padding: 16px 0 18px;
        margin-bottom: 12px;
    }}
    .indice h2 {{ margin: 0 0 12px; font-size: 1rem; color: var(--texto-suave); }}
    .indice-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }}
    .indice-item {{
        display: block;
        text-decoration: none;
        color: inherit;
        background: var(--panel);
        border: 1px solid var(--borde);
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: 0 4px 12px rgba(33, 65, 98, 0.04);
    }}
    .indice-item:hover {{ border-color: #9fc7e2; transform: translateY(-1px); }}
    .indice-titulo {{ display: block; font-weight: 600; color: var(--texto); }}
    .indice-meta {{ display: block; color: var(--texto-suave); font-size: 0.9rem; margin-top: 4px; }}
    .contenido {{ display: grid; gap: 18px; }}
    .seccion {{
        background: var(--panel);
        border: 1px solid var(--borde);
        border-radius: 18px;
        padding: 22px;
        box-shadow: var(--sombra);
    }}
    .seccion-cabecera {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 14px;
        border-bottom: 1px solid #e8eef5;
    }}
    .seccion h2 {{ margin: 0; color: var(--marca); }}
    .seccion-resumen {{ margin: 6px 0 0; color: var(--texto-suave); }}
    .ancla {{ text-decoration: none; color: #8aa6bc; font-weight: 700; font-size: 1.2rem; }}
    .rejilla-elementos {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px; }}
    .tarjeta-elemento {{
        background: var(--panel-secundario);
        border: 1px solid var(--borde);
        border-radius: 16px;
        padding: 16px;
    }}
    .tarjeta-cabecera {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; }}
    .tarjeta-cabecera h3 {{ margin: 0; font-size: 1rem; color: var(--texto); }}
    .etiqueta {{
        background: var(--marca-suave);
        color: var(--marca);
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 0.82rem;
        font-weight: 600;
        white-space: nowrap;
    }}
    .tabla-wrapper {{ overflow-x: auto; }}
    .tabla-datos {{ border-collapse: collapse; width: 100%; }}
    .tabla-datos th,
    .tabla-datos td {{ padding: 9px 12px; border-bottom: 1px solid #e8eef5; vertical-align: top; text-align: left; }}
    .tabla-datos tr:last-child th,
    .tabla-datos tr:last-child td {{ border-bottom: 0; }}
    .clave {{ width: 260px; min-width: 220px; color: #35546d; font-weight: 600; background: rgba(11, 106, 162, 0.03); }}
    .lista-simple {{ margin: 0; padding-left: 22px; }}
    .lista-simple li + li {{ margin-top: 8px; }}
    .texto-plano {{ margin: 0; }}
    .valor-expandido {{ word-break: break-word; color: var(--texto); }}
    pre,
    .valor-multilinea {{
        margin: 0;
        background: #f5f9fd;
        border: 1px solid var(--borde);
        border-radius: 12px;
        padding: 12px 14px;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-word;
        font-size: 0.9rem;
        color: #30485c;
    }}
    .vacio {{ margin: 0; color: var(--texto-suave); }}
    em {{ color: #7a8a98; }}
    @media (max-width: 720px) {{
        .pagina {{ padding: 20px 14px 36px; }}
        .hero {{ padding: 22px 18px; }}
        .seccion {{ padding: 18px; }}
        .seccion-cabecera,
        .tarjeta-cabecera {{ flex-direction: column; align-items: flex-start; }}
        .clave {{ width: 42%; min-width: 160px; }}
    }}
</style>
</head>
<body>
<div class="pagina">
<header class="hero">
<h1>El PC y sus cosas — Informe de Inventario</h1>
<p class="meta">Fecha: {ahora} &mdash; Equipo: <strong>{nombre_equipo}</strong></p>
<div class="resumen-superior">
    <div class="dato-resumen"><strong>{total_secciones}</strong><span>secciones</span></div>
    <div class="dato-resumen"><strong>{total_bloques}</strong><span>bloques de información</span></div>
    <div class="dato-resumen"><strong>{nombre_equipo}</strong><span>equipo analizado</span></div>
</div>
</header>
<nav class="indice" aria-label="Índice del informe">
    <h2>Índice de secciones</h2>
    <div class="indice-grid">
        {''.join(enlaces)}
    </div>
</nav>
<main class="contenido">
""")

    for titulo, contenido in secciones:
        partes.append(seccion_html(titulo, contenido))

    partes.append("</main></div></body></html>")

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(partes))

    return ruta
