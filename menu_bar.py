"""Barra de menú superior para la aplicación El PC y sus cosas."""

import tkinter as tk
from tkinter import ttk
import os
import webbrowser

# Directorio raíz del proyecto
_DIR_PROYECTO = os.path.dirname(os.path.abspath(__file__))

# Colores consistentes con el tema de la GUI
_COLOR_BG = "#1e1e2e"
_COLOR_BG_SECONDARY = "#282840"
_COLOR_CARD = "#313150"
_COLOR_ACCENT = "#7c3aed"
_COLOR_TEXT = "#e2e8f0"
_COLOR_TEXT_DIM = "#94a3b8"

URL_PROYECTO = "http://github.com/sapoclay/el-pc-y-sus-cosas"
_REFERENCIAS_IMAGENES: dict[str, list[tk.PhotoImage]] = {}

FUNCIONALIDADES = [
    ("Sistema operativo", "Nombre del equipo, SO, versión, arquitectura, usuario actual."),
    ("BIOS", "Fabricante, nombre, número de serie, versión, fecha."),
    ("Placa base", "Fabricante, producto, número de serie, versión."),
    ("Procesador (CPU)", "Modelo, núcleos, hilos, velocidad máxima, fabricante."),
    ("Memoria RAM", "Módulos instalados: capacidad, velocidad, fabricante, serial."),
    ("Discos duros", "Modelo, tamaño, interfaz, tipo, serial, particiones, estado."),
    ("Particiones", "Letra, sistema de archivos, tamaño total/libre, tipo de unidad."),
    ("Tarjeta gráfica (GPU)", "Nombre, VRAM, driver, resolución actual."),
    ("Monitor", "Nombre, fabricante, resolución."),
    ("Dispositivos de sonido", "Nombre, fabricante, estado."),
    ("Información de red", "IP local, MAC, hostname, FQDN."),
    ("Adaptadores de red", "Nombre, MAC, velocidad, tipo de conexión."),
    ("Configuración IP", "Salida completa de ipconfig /all."),
    ("Dispositivos USB", "Dispositivos USB conectados con clase y estado."),
    ("Impresoras", "Nombre, driver, puerto, predeterminada, compartida."),
    ("Red local (ARP)", "Dispositivos detectados en la red local."),
    ("Batería", "Nombre, carga restante, estado, voltaje."),
    ("Software instalado", "Lista completa de programas: nombre, versión, fabricante, fecha."),
    ("Usuarios del sistema", "Usuarios locales con grupos, privilegios y estado de cuenta."),
    ("Grupos y privilegios", "Grupos locales del sistema y sus miembros."),
]


def crear_menu(root: tk.Tk, on_exit=None):
    """Crea y configura la barra de menú superior."""
    accion_salir = on_exit or root.quit

    barra_menu = tk.Menu(root, bg=_COLOR_BG_SECONDARY, fg=_COLOR_TEXT,
                         activebackground=_COLOR_ACCENT, activeforeground="white",
                         font=("Segoe UI", 10), relief=tk.FLAT, borderwidth=0)

    # ── Menú Archivo ──
    menu_archivo = tk.Menu(barra_menu, tearoff=0, bg=_COLOR_BG_SECONDARY,
                           fg=_COLOR_TEXT, activebackground=_COLOR_ACCENT,
                           activeforeground="white", font=("Segoe UI", 10))
    menu_archivo.add_command(label="Salir", command=accion_salir, accelerator="Alt+F4")
    barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

    # ── Menú Ayuda ──
    menu_ayuda = tk.Menu(barra_menu, tearoff=0, bg=_COLOR_BG_SECONDARY,
                         fg=_COLOR_TEXT, activebackground=_COLOR_ACCENT,
                         activeforeground="white", font=("Segoe UI", 10))
    menu_ayuda.add_command(label="About", command=lambda: _mostrar_about(root))
    barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

    root.config(menu=barra_menu)


def _mostrar_about(parent: tk.Tk):
    """Abre la ventana 'About' con logo, funcionalidades y enlace al repositorio."""
    about = tk.Toplevel(parent)
    about.title("About — El PC y sus cosas")
    about.geometry("620x680")
    about.resizable(False, False)
    about.configure(bg=_COLOR_BG)
    about.transient(parent)
    about.grab_set()

    # Contenedor con scroll
    canvas = tk.Canvas(about, bg=_COLOR_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(about, orient=tk.VERTICAL, command=canvas.yview)
    contenedor = tk.Frame(canvas, bg=_COLOR_BG)

    contenedor.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=contenedor, anchor=tk.NW, width=600)
    canvas.configure(yscrollcommand=scrollbar.set)

    referencias_imagenes: list[tk.PhotoImage] = []
    _REFERENCIAS_IMAGENES[str(about)] = referencias_imagenes

    # Habilitar scroll con la rueda del ratón
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _cerrar_about():
        _unbind_mousewheel(canvas)
        _REFERENCIAS_IMAGENES.pop(str(about), None)
        about.destroy()

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    about.protocol("WM_DELETE_WINDOW", _cerrar_about)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    pad = 24

    # ── Logo (redimensionado a ~300x300) ──
    ruta_logo = os.path.join(_DIR_PROYECTO, "img", "logo.png")
    logo_img = None
    if os.path.isfile(ruta_logo):
        try:
            img_original = tk.PhotoImage(file=ruta_logo)
            ancho_orig = img_original.width()
            alto_orig = img_original.height()
            # Calcular factor de reducción para que quepa en 300x300
            factor = max(ancho_orig // 300, alto_orig // 300, 1)
            if factor > 1:
                logo_img = img_original.subsample(factor, factor)
            else:
                logo_img = img_original
            # Mantener referencia para que no sea recolectado por el GC
            referencias_imagenes.extend([logo_img, img_original])
            lbl_logo = tk.Label(contenedor, image=logo_img, bg=_COLOR_BG)
            lbl_logo.pack(pady=(pad, 10))
        except Exception:
            pass

    # ── Título ──
    tk.Label(contenedor, text="El PC y sus cosas", bg=_COLOR_BG, fg=_COLOR_TEXT,
             font=("Segoe UI", 20, "bold")).pack(pady=(8 if logo_img else pad, 4))

    tk.Label(contenedor, text="Generador de informes de inventario del equipo",
             bg=_COLOR_BG, fg=_COLOR_TEXT_DIM, font=("Segoe UI", 10)).pack(pady=(0, 16))

    # ── Separador ──
    tk.Frame(contenedor, bg=_COLOR_ACCENT, height=2).pack(fill=tk.X, padx=pad, pady=(0, 16))

    # ── Lista de funcionalidades ──
    tk.Label(contenedor, text="Datos recopilados por el programa:",
             bg=_COLOR_BG, fg=_COLOR_TEXT, font=("Segoe UI", 12, "bold"),
             anchor=tk.W).pack(fill=tk.X, padx=pad, pady=(0, 10))

    for nombre, descripcion in FUNCIONALIDADES:
        fila = tk.Frame(contenedor, bg=_COLOR_CARD, padx=12, pady=8)
        fila.pack(fill=tk.X, padx=pad, pady=2)

        tk.Label(fila, text=f"▸  {nombre}", bg=_COLOR_CARD, fg=_COLOR_TEXT,
                 font=("Segoe UI", 10, "bold"), anchor=tk.W).pack(anchor=tk.W)
        tk.Label(fila, text=descripcion, bg=_COLOR_CARD, fg=_COLOR_TEXT_DIM,
                 font=("Segoe UI", 9), anchor=tk.W, wraplength=540).pack(anchor=tk.W)

    # ── Separador ──
    tk.Frame(contenedor, bg=_COLOR_ACCENT, height=2).pack(fill=tk.X, padx=pad, pady=(16, 16))

    # ── Botón para abrir el repositorio ──
    btn_frame = tk.Frame(contenedor, bg=_COLOR_BG)
    btn_frame.pack(pady=(0, pad))

    btn_repo = tk.Button(
        btn_frame, text="🌐  Visitar repositorio en GitHub",
        bg=_COLOR_ACCENT, fg="white", font=("Segoe UI", 11, "bold"),
        activebackground="#6d28d9", activeforeground="white",
        relief=tk.FLAT, padx=20, pady=10, cursor="hand2",
        command=lambda: webbrowser.open(URL_PROYECTO)
    )
    btn_repo.pack()

    tk.Label(contenedor, text="Creado por entreunosyceros", bg=_COLOR_BG, fg=_COLOR_TEXT_DIM,
             font=("Segoe UI", 9)).pack(pady=(4, pad))


def _unbind_mousewheel(canvas: tk.Canvas):
    """Desvincula el evento de la rueda del ratón al cerrar la ventana About."""
    try:
        canvas.unbind_all("<MouseWheel>")
    except Exception:
        pass
