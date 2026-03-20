"""Interfaz gráfica para el generador de informe de inventario."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import datetime
import platform
import os
import sys

# Asegurar que el directorio raíz del proyecto esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recopiladores.sistema import info_sistema, info_bios, info_placa_base
from recopiladores.hardware import (
    info_procesador, info_memoria_ram, info_discos, info_particiones,
    info_gpu, info_monitor, info_sonido, info_bateria,
)
from recopiladores.red import info_red, info_adaptadores_red, info_ip_config, info_dispositivos_red_local
from recopiladores.dispositivos import info_dispositivos_usb, info_impresoras
from recopiladores.software import info_software_instalado, info_servicios_inicio
from recopiladores.usuarios import info_usuarios, info_grupos_usuario, info_privilegios_usuarios
from exportadores.texto import exportar_txt
from exportadores.html_export import exportar_html
from exportadores.sql_export import exportar_sql
from menu_bar import crear_menu
from system_tray import SystemTrayController
from utilidades import abrir_ruta, obtener_usuario_actual


# ── Colores del tema ──────────────────────────────────────────────────────────
COLOR_BG = "#1e1e2e"
COLOR_BG_SECONDARY = "#282840"
COLOR_CARD = "#313150"
COLOR_ACCENT = "#7c3aed"
COLOR_ACCENT_HOVER = "#6d28d9"
COLOR_SUCCESS = "#22c55e"
COLOR_TEXT = "#e2e8f0"
COLOR_TEXT_DIM = "#94a3b8"
COLOR_BORDER = "#3b3b5c"
COLOR_PROGRESS_BG = "#1e1e2e"
COLOR_PROGRESS_FG = "#7c3aed"


class AplicacionInventario:
    """Ventana principal de la aplicación."""

    PASOS_RECOPILACION = [
        ("Sistema operativo", info_sistema),
        ("BIOS", info_bios),
        ("Placa base", info_placa_base),
        ("Procesador (CPU)", info_procesador),
        ("Memoria RAM", info_memoria_ram),
        ("Discos duros", info_discos),
        ("Particiones / Unidades lógicas", info_particiones),
        ("Tarjeta gráfica (GPU)", info_gpu),
        ("Monitor", info_monitor),
        ("Dispositivos de sonido", info_sonido),
        ("Información de red", info_red),
        ("Adaptadores de red activos", info_adaptadores_red),
        ("Configuración IP completa", info_ip_config),
        ("Dispositivos USB conectados", info_dispositivos_usb),
        ("Impresoras", info_impresoras),
        ("Dispositivos en la red local (ARP)", info_dispositivos_red_local),
        ("Batería", info_bateria),
        ("Software instalado", info_software_instalado),
        ("Usuarios del sistema", info_privilegios_usuarios),
        ("Grupos y privilegios", info_grupos_usuario),
    ]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("El PC y sus cosas")
        self.root.geometry("960x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLOR_BG)

        # Intentar poner icono
        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        self.secciones: list[tuple] = []
        self.recopilando = False
        self.cerrando = False
        self.directorio_informes = os.path.dirname(os.path.abspath(__file__))
        self.bandeja = None

        self._crear_estilos()
        crear_menu(self.root, on_exit=self._cerrar_aplicacion)
        self._construir_interfaz()
        self._configurar_bandeja_sistema()
        self.root.protocol("WM_DELETE_WINDOW", self._al_cerrar_ventana)
        self.root.mainloop()

    # ── Estilos ───────────────────────────────────────────────────────────

    def _crear_estilos(self):
        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")

        self.estilo.configure(".", background=COLOR_BG, foreground=COLOR_TEXT,
                              font=("Segoe UI", 10))

        self.estilo.configure("TFrame", background=COLOR_BG)
        self.estilo.configure("Card.TFrame", background=COLOR_CARD)
        self.estilo.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT,
                              font=("Segoe UI", 10))
        self.estilo.configure("Title.TLabel", background=COLOR_BG, foreground=COLOR_TEXT,
                              font=("Segoe UI", 22, "bold"))
        self.estilo.configure("Subtitle.TLabel", background=COLOR_BG, foreground=COLOR_TEXT_DIM,
                              font=("Segoe UI", 10))
        self.estilo.configure("CardTitle.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT,
                              font=("Segoe UI", 11, "bold"))
        self.estilo.configure("CardText.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT_DIM,
                              font=("Segoe UI", 9))
        self.estilo.configure("Status.TLabel", background=COLOR_BG, foreground=COLOR_TEXT_DIM,
                              font=("Segoe UI", 9))
        self.estilo.configure("Success.TLabel", background=COLOR_BG, foreground=COLOR_SUCCESS,
                              font=("Segoe UI", 10, "bold"))

        # Botones
        self.estilo.configure("Accent.TButton", background=COLOR_ACCENT,
                              foreground="white", font=("Segoe UI", 11, "bold"),
                              padding=(20, 12), borderwidth=0)
        self.estilo.map("Accent.TButton",
                        background=[("active", COLOR_ACCENT_HOVER), ("disabled", COLOR_BORDER)])

        self.estilo.configure("Export.TButton", background=COLOR_BG_SECONDARY,
                              foreground=COLOR_TEXT, font=("Segoe UI", 10),
                              padding=(16, 10), borderwidth=1)
        self.estilo.map("Export.TButton",
                        background=[("active", COLOR_CARD), ("disabled", COLOR_BG)])

        # Checkbutton
        self.estilo.configure("TCheckbutton", background=COLOR_CARD, foreground=COLOR_TEXT,
                              font=("Segoe UI", 10))
        self.estilo.map("TCheckbutton", background=[("active", COLOR_CARD)])

        # Barra de progreso
        self.estilo.configure("Custom.Horizontal.TProgressbar",
                              troughcolor=COLOR_PROGRESS_BG,
                              background=COLOR_PROGRESS_FG,
                              thickness=6)

    # ── Construcción de la interfaz ───────────────────────────────────────

    def _construir_interfaz(self):
        # Contenedor principal con padding
        main = ttk.Frame(self.root, padding=30)
        main.pack(fill=tk.BOTH, expand=True)

        # ── Encabezado ──
        header = ttk.Frame(main)
        header.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(header, text="⚙  El PC y sus cosas",
                  style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(header, text="Genera un informe completo con todos los componentes, "
                  "red, usuarios y software de este equipo.",
                  style="Subtitle.TLabel", wraplength=700).pack(anchor=tk.W, pady=(4, 0))

        # ── Información rápida del equipo ──
        info_frame = ttk.Frame(main, style="Card.TFrame", padding=16)
        info_frame.pack(fill=tk.X, pady=(0, 20))

        cols = ttk.Frame(info_frame, style="Card.TFrame")
        cols.pack(fill=tk.X)

        datos_rapidos = [
            ("Equipo", platform.node()),
            ("SO", f"{platform.system()} {platform.release()}"),
            ("Arquitectura", platform.machine()),
            ("Usuario", obtener_usuario_actual()),
        ]
        for i, (etiq, val) in enumerate(datos_rapidos):
            col = ttk.Frame(cols, style="Card.TFrame")
            col.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0 if i == 0 else 10, 0))
            ttk.Label(col, text=etiq, style="CardText.TLabel").pack(anchor=tk.W)
            ttk.Label(col, text=val, style="CardTitle.TLabel").pack(anchor=tk.W)

        # ── Opciones de exportación ──
        opciones_frame = ttk.Frame(main, style="Card.TFrame", padding=16)
        opciones_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(opciones_frame, text="Formatos de exportación",
                  style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))

        checks_frame = ttk.Frame(opciones_frame, style="Card.TFrame")
        checks_frame.pack(fill=tk.X)

        self.var_txt = tk.BooleanVar(value=True)
        self.var_html = tk.BooleanVar(value=True)
        self.var_sql = tk.BooleanVar(value=False)

        ttk.Checkbutton(checks_frame, text="  Texto plano (.txt)",
                        variable=self.var_txt).pack(side=tk.LEFT, padx=(0, 24))
        ttk.Checkbutton(checks_frame, text="  HTML (.html)",
                        variable=self.var_html).pack(side=tk.LEFT, padx=(0, 24))
        ttk.Checkbutton(checks_frame, text="  SQL (.sql)",
                        variable=self.var_sql).pack(side=tk.LEFT)

        # ── Botón de generar ──
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(0, 16))

        self.btn_generar = ttk.Button(btn_frame, text="▶  Generar informe",
                                      style="Accent.TButton",
                                      command=self._iniciar_recopilacion)
        self.btn_generar.pack(side=tk.LEFT)

        # ── Barra de progreso ──
        self.progreso = ttk.Progressbar(main, style="Custom.Horizontal.TProgressbar",
                                        mode="determinate", maximum=len(self.PASOS_RECOPILACION))
        self.progreso.pack(fill=tk.X, pady=(0, 6))

        self.lbl_estado = ttk.Label(main, text="Listo para generar.", style="Status.TLabel")
        self.lbl_estado.pack(anchor=tk.W, pady=(0, 12))

        # ── Registro (log) ──
        log_frame = ttk.Frame(main, style="Card.TFrame", padding=2)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.txt_log = tk.Text(log_frame, bg=COLOR_BG_SECONDARY, fg=COLOR_TEXT_DIM,
                               font=("Consolas", 9), relief=tk.FLAT,
                               insertbackground=COLOR_TEXT, selectbackground=COLOR_ACCENT,
                               padx=12, pady=10, wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.txt_log.yview)
        self.txt_log.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # ── Barra inferior con botones de exportación ──
        self.footer = ttk.Frame(main)
        self.footer.pack(fill=tk.X, pady=(12, 0))

        self.btn_abrir_carpeta = ttk.Button(self.footer, text="📁 Abrir carpeta",
                                            style="Export.TButton",
                                            command=self._abrir_carpeta, state=tk.DISABLED)
        self.btn_abrir_carpeta.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_reexportar = ttk.Button(self.footer, text="💾 Exportar de nuevo",
                                         style="Export.TButton",
                                         command=self._reexportar, state=tk.DISABLED)
        self.btn_reexportar.pack(side=tk.LEFT)

        self.ultima_carpeta = None

    def _configurar_bandeja_sistema(self):
        """Inicializa el icono de bandeja si el sistema lo soporta."""
        icono_path = os.path.join(self.directorio_informes, "img", "logo.png")
        self.bandeja = SystemTrayController(
            titulo="El PC y sus cosas",
            icono_path=icono_path,
            on_show=lambda: self._ejecutar_en_ui(self._mostrar_ventana),
            on_scan=lambda: self._ejecutar_en_ui(self._iniciar_recopilacion),
            on_open_reports=lambda: self._ejecutar_en_ui(self._abrir_carpeta),
            on_exit=lambda: self._ejecutar_en_ui(self._cerrar_aplicacion),
            can_scan=lambda: not self.recopilando,
        )

        if self.bandeja.iniciar():
            self._log("Bandeja del sistema activada.")
        else:
            self._log("Bandeja del sistema no disponible en este entorno.")

    # ── Funciones de log ──────────────────────────────────────────────────

    def _log(self, mensaje: str):
        self.txt_log.configure(state=tk.NORMAL)
        ahora = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert(tk.END, f"[{ahora}]  {mensaje}\n")
        self.txt_log.see(tk.END)
        self.txt_log.configure(state=tk.DISABLED)

    def _actualizar_estado(self, texto: str):
        self.lbl_estado.configure(text=texto)

    def _ejecutar_en_ui(self, callback):
        """Programa una función en el hilo de Tk sin devolver el id de after."""
        self.root.after(0, callback)

    # ── Recopilación ──────────────────────────────────────────────────────

    def _iniciar_recopilacion(self):
        if self.recopilando:
            return

        if not (self.var_txt.get() or self.var_html.get() or self.var_sql.get()):
            messagebox.showwarning("Sin formato", "Selecciona al menos un formato de exportación.")
            return

        self.recopilando = True
        self.secciones = []
        self.btn_generar.configure(state=tk.DISABLED)
        self.btn_abrir_carpeta.configure(state=tk.DISABLED)
        self.btn_reexportar.configure(state=tk.DISABLED)
        self.progreso["value"] = 0

        # Limpiar log
        self.txt_log.configure(state=tk.NORMAL)
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.configure(state=tk.DISABLED)

        self._log("Iniciando recopilación de datos del sistema...")
        self._actualizar_menu_bandeja()
        hilo = threading.Thread(target=self._recopilar_datos, daemon=True)
        hilo.start()

    def _recopilar_datos(self):
        total = len(self.PASOS_RECOPILACION)

        for i, (nombre, funcion) in enumerate(self.PASOS_RECOPILACION):
            self.root.after(0, self._actualizar_estado, f"Recopilando: {nombre}...")
            self.root.after(0, self._log, f"Recopilando: {nombre}...")

            try:
                datos = funcion()
            except Exception as e:
                datos = f"Error: {e}"
                self.root.after(0, self._log, f"  ⚠ Error en {nombre}: {e}")

            self.secciones.append((nombre, datos))
            self.root.after(0, self._progreso_set, i + 1)

        self.root.after(0, self._exportar_resultados)

    def _progreso_set(self, valor):
        self.progreso["value"] = valor

    def _exportar_resultados(self):
        self._log("Recopilación completa. Exportando archivos...")
        self._actualizar_estado("Exportando archivos...")

        directorio = self.directorio_informes
        nombre_equipo = platform.node()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"informe_{nombre_equipo}_{ts}"

        archivos_generados = []

        try:
            if self.var_txt.get():
                ruta = os.path.join(directorio, f"{base}.txt")
                exportar_txt(self.secciones, ruta)
                archivos_generados.append(ruta)
                self._log(f"✔ TXT guardado: {os.path.basename(ruta)}")

            if self.var_html.get():
                ruta = os.path.join(directorio, f"{base}.html")
                exportar_html(self.secciones, ruta)
                archivos_generados.append(ruta)
                self._log(f"✔ HTML guardado: {os.path.basename(ruta)}")

            if self.var_sql.get():
                ruta = os.path.join(directorio, f"{base}.sql")
                exportar_sql(self.secciones, ruta)
                archivos_generados.append(ruta)
                self._log(f"✔ SQL guardado: {os.path.basename(ruta)}")

        except Exception as e:
            self._log(f"⚠ Error al exportar: {e}")
            messagebox.showerror("Error", f"Error al exportar: {e}")

        self.ultima_carpeta = directorio
        n = len(archivos_generados)
        self._actualizar_estado(f"Informe generado correctamente — {n} archivo(s) exportado(s).")
        self.lbl_estado.configure(style="Success.TLabel")
        self._log(f"Proceso finalizado. {n} archivo(s) generado(s) en: {directorio}")

        self.btn_generar.configure(state=tk.NORMAL)
        self.btn_abrir_carpeta.configure(state=tk.NORMAL)
        self.btn_reexportar.configure(state=tk.NORMAL)
        self.recopilando = False
        self._actualizar_menu_bandeja()

        # Abrir el HTML automáticamente si se generó
        if self.var_html.get():
            ruta_html = os.path.join(directorio, f"{base}.html")
            try:
                abrir_ruta(ruta_html)
            except Exception:
                pass

    # ── Acciones de botones ───────────────────────────────────────────────

    def _abrir_carpeta(self):
        abrir_ruta(self._obtener_carpeta_informes())

    def _reexportar(self):
        """Permite elegir una carpeta distinta y re-exportar los datos ya recopilados."""
        if not self.secciones:
            messagebox.showinfo("Sin datos", "Primero genera un informe.")
            return

        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if not carpeta:
            return

        nombre_equipo = platform.node()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"informe_{nombre_equipo}_{ts}"
        n = 0

        try:
            if self.var_txt.get():
                exportar_txt(self.secciones, os.path.join(carpeta, f"{base}.txt"))
                n += 1
            if self.var_html.get():
                exportar_html(self.secciones, os.path.join(carpeta, f"{base}.html"))
                n += 1
            if self.var_sql.get():
                exportar_sql(self.secciones, os.path.join(carpeta, f"{base}.sql"))
                n += 1
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")
            return

        self.ultima_carpeta = carpeta
        self._actualizar_menu_bandeja()
        self._log(f"Re-exportado: {n} archivo(s) en {carpeta}")
        messagebox.showinfo("Exportación completa", f"{n} archivo(s) exportado(s) en:\n{carpeta}")

    def _obtener_carpeta_informes(self) -> str:
        """Devuelve la carpeta por defecto donde se guardan los informes."""
        return self.ultima_carpeta or self.directorio_informes

    def _mostrar_ventana(self):
        """Restaura la ventana principal desde la bandeja del sistema."""
        self.root.deiconify()
        self.root.lift()
        try:
            self.root.focus_force()
        except Exception:
            pass

    def _al_cerrar_ventana(self):
        """Oculta la ventana en lugar de cerrar la aplicación si la bandeja está activa."""
        if self.cerrando:
            return

        if self.bandeja and self.bandeja.activa:
            self.root.withdraw()
            self._log("Ventana ocultada en la bandeja del sistema.")
            return

        self._cerrar_aplicacion()

    def _cerrar_aplicacion(self):
        """Cierra completamente la aplicación y libera la bandeja del sistema."""
        if self.cerrando:
            return

        self.cerrando = True
        try:
            if self.bandeja:
                self.bandeja.detener()
        finally:
            try:
                self.root.quit()
            finally:
                self.root.destroy()

    def _actualizar_menu_bandeja(self):
        """Refresca el menú de la bandeja para reflejar el estado actual."""
        if self.bandeja:
            self.bandeja.actualizar_menu()


def iniciar_gui():
    """Punto de entrada para la GUI."""
    AplicacionInventario()
