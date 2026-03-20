"""Integración opcional con la bandeja del sistema."""

from __future__ import annotations

import os
import threading

try:
    from PIL import Image, ImageDraw
    import pystray
except Exception:
    Image = None
    ImageDraw = None
    pystray = None


class SystemTrayController:
    """Gestiona un icono de bandeja con acciones para la aplicación."""

    def __init__(
        self,
        titulo: str,
        icono_path: str,
        on_show,
        on_scan,
        on_open_reports,
        on_exit,
        can_scan=None,
    ):
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
        return pystray is not None and Image is not None

    @property
    def activa(self) -> bool:
        """Indica si el icono está actualmente en ejecución."""
        return self._icon is not None

    def iniciar(self) -> bool:
        """Crea e inicia el icono de bandeja si el entorno lo soporta."""
        if not self.disponible:
            return False

        with self._lock:
            if self._icon is not None:
                return True

            self._icon = pystray.Icon(
                "el-pc-y-sus-cosas",
                self._crear_icono(),
                self.titulo,
                menu=self._crear_menu(),
            )
            self._thread = threading.Thread(target=self._icon.run, daemon=True)
            self._thread.start()
            return True

    def detener(self):
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

    def actualizar_menu(self):
        """Solicita una actualización del menú dinámico del icono."""
        icono = self._icon
        if icono is None:
            return
        try:
            icono.update_menu()
        except Exception:
            pass

    def _crear_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Mostrar ventana", self._accion_mostrar, default=True),
            pystray.MenuItem("Iniciar escaneo", self._accion_escanear, enabled=lambda _: self.can_scan()),
            pystray.MenuItem("Abrir carpeta de informes", self._accion_abrir_informes),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Cerrar programa", self._accion_salir),
        )

    def _accion_mostrar(self, icono, item):
        del icono, item
        self.on_show()

    def _accion_escanear(self, icono, item):
        del icono, item
        self.on_scan()

    def _accion_abrir_informes(self, icono, item):
        del icono, item
        self.on_open_reports()

    def _accion_salir(self, icono, item):
        del icono, item
        self.on_exit()

    def _crear_icono(self):
        if self.icono_path and os.path.isfile(self.icono_path):
            try:
                return Image.open(self.icono_path).convert("RGBA")
            except Exception:
                pass

        imagen = Image.new("RGBA", (64, 64), (30, 30, 46, 255))
        dibujo = ImageDraw.Draw(imagen)
        dibujo.rounded_rectangle((6, 6, 58, 58), radius=12, fill=(49, 49, 80, 255))
        dibujo.rounded_rectangle((14, 14, 50, 50), radius=10, fill=(124, 58, 237, 255))
        dibujo.rectangle((22, 22, 42, 36), fill=(226, 232, 240, 255))
        dibujo.rectangle((20, 40, 44, 44), fill=(226, 232, 240, 255))
        return imagen