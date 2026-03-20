"""Integración opcional con la bandeja del sistema."""

from __future__ import annotations

import importlib
import os
import threading
from typing import Any, Callable

ImageModule = Any
ImageDrawModule = Any
PystrayModule = Any

Image: ImageModule | None = None
ImageDraw: ImageDrawModule | None = None
pystray: PystrayModule | None = None


def _cargar_modulo(nombre: str) -> Any | None:
    """Carga un módulo opcional sin provocar avisos por import estático."""
    try:
        return importlib.import_module(nombre)
    except Exception:
        return None


def _asegurar_dependencias() -> None:
    """Carga bajo demanda las dependencias opcionales de la bandeja."""
    global Image, ImageDraw, pystray

    if Image is None:
        Image = _cargar_modulo("PIL.Image")
    if ImageDraw is None:
        ImageDraw = _cargar_modulo("PIL.ImageDraw")
    if pystray is None:
        pystray = _cargar_modulo("pystray")


def _dependencias_disponibles() -> bool:
    """Indica si los módulos opcionales para la bandeja están disponibles."""
    _asegurar_dependencias()
    return pystray is not None and Image is not None and ImageDraw is not None


def _pystray_mod() -> PystrayModule:
    """Devuelve el módulo pystray ya validado para evitar avisos del analizador."""
    if pystray is None:
        raise RuntimeError("pystray no está disponible")
    return pystray


def _image_mod() -> ImageModule:
    """Devuelve el módulo PIL.Image ya validado para evitar avisos del analizador."""
    if Image is None:
        raise RuntimeError("Pillow no está disponible")
    return Image


def _image_draw_mod() -> ImageDrawModule:
    """Devuelve el módulo PIL.ImageDraw ya validado para evitar avisos del analizador."""
    if ImageDraw is None:
        raise RuntimeError("Pillow no está disponible")
    return ImageDraw


class SystemTrayController:
    """Gestiona un icono de bandeja con acciones para la aplicación."""

    def __init__(
        self,
        titulo: str,
        icono_path: str,
        on_show: Callable[[], None],
        on_scan: Callable[[], None],
        on_open_reports: Callable[[], None],
        on_exit: Callable[[], None],
        can_scan: Callable[[], bool] | None = None,
    ) -> None:
        self.titulo = titulo
        self.icono_path = icono_path
        self.on_show = on_show
        self.on_scan = on_scan
        self.on_open_reports = on_open_reports
        self.on_exit = on_exit
        self.can_scan = can_scan or (lambda: True)

        self._icon = None
        self._thread = None
        self._lock = threading.Lock()

    @property
    def disponible(self) -> bool:
        """Indica si la integración de bandeja está disponible en este entorno."""
        return _dependencias_disponibles()

    @property
    def activa(self) -> bool:
        """Indica si el icono está actualmente en ejecución."""
        return self._icon is not None

    def iniciar(self) -> bool:
        """Crea e inicia el icono de bandeja si el entorno lo soporta."""
        if not self.disponible:
            return False

        pystray_mod = _pystray_mod()

        with self._lock:
            if self._icon is not None:
                return True

            self._icon = pystray_mod.Icon(
                "el-pc-y-sus-cosas",
                self._crear_icono(),
                self.titulo,
                menu=self._crear_menu(),
            )
            self._thread = threading.Thread(target=self._icon.run, daemon=True)
            self._thread.start()
            return True

    def detener(self) -> None:
        """Detiene el icono de bandeja si estaba activo."""
        with self._lock:
            if self._icon is None:
                return

            icono = self._icon
            self._icon = None

        try:
            icono.stop()
        except Exception:
            pass

    def actualizar_menu(self) -> None:
        """Solicita una actualización del menú dinámico del icono."""
        icono = self._icon
        if icono is None:
            return
        try:
            icono.update_menu()
        except Exception:
            pass

    def _crear_menu(self):
        pystray_mod = _pystray_mod()
        return pystray_mod.Menu(
            pystray_mod.MenuItem("Mostrar ventana", self._accion_mostrar, default=True),
            pystray_mod.MenuItem("Iniciar escaneo", self._accion_escanear, enabled=lambda _: self.can_scan()),
            pystray_mod.MenuItem("Abrir carpeta de informes", self._accion_abrir_informes),
            pystray_mod.Menu.SEPARATOR,
            pystray_mod.MenuItem("Cerrar programa", self._accion_salir),
        )

    def _accion_mostrar(self, icono, item) -> None:
        del icono, item
        self.on_show()

    def _accion_escanear(self, icono, item) -> None:
        del icono, item
        self.on_scan()

    def _accion_abrir_informes(self, icono, item) -> None:
        del icono, item
        self.on_open_reports()

    def _accion_salir(self, icono, item) -> None:
        del icono, item
        self.on_exit()

    def _crear_icono(self):
        image_mod = _image_mod()
        image_draw_mod = _image_draw_mod()

        if self.icono_path and os.path.isfile(self.icono_path):
            try:
                return image_mod.open(self.icono_path).convert("RGBA")
            except Exception:
                pass

        imagen = image_mod.new("RGBA", (64, 64), (30, 30, 46, 255))
        dibujo = image_draw_mod.Draw(imagen)
        dibujo.rounded_rectangle((6, 6, 58, 58), radius=12, fill=(49, 49, 80, 255))
        dibujo.rounded_rectangle((14, 14, 50, 50), radius=10, fill=(124, 58, 237, 255))
        dibujo.rectangle((22, 22, 42, 36), fill=(226, 232, 240, 255))
        dibujo.rectangle((20, 40, 44, 44), fill=(226, 232, 240, 255))
        return imagen