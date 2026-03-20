# El PC y sus cosas

Aplicación de escritorio en Python para generar informes de inventario del equipo en formato texto, HTML y SQL.

El objetivo del proyecto es recopilar información relevante del sistema operativo, hardware, red, usuarios y software instalado, y exportarla de forma sencilla para consulta, soporte técnico o documentación.

## Características

- Interfaz gráfica desarrollada con Tkinter.
- Generación de informes en formato TXT, HTML y SQL.
- Recopilación de información de sistema, BIOS, placa base, CPU, RAM, discos y particiones.
- Obtención de datos de red, adaptadores, configuración IP y dispositivos detectados en la red local.
- Consulta de dispositivos USB, impresoras, batería y otros periféricos.
- Inventario de software instalado, usuarios y grupos del sistema.
- Apertura rápida de la carpeta de informes generados.
- Reexportación de los informes a otra carpeta.
- Integración con bandeja del sistema para iniciar un escaneo, mostrar la ventana, abrir la carpeta de informes y cerrar la aplicación.
- Compatibilidad prevista para Windows y Linux.

## Estructura del proyecto

```text
.
├── exportadores/
├── img/
├── recopiladores/
├── gui.py
├── informe_equipo.py
├── menu_bar.py
├── requirements.txt
├── run_app.py
└── utilidades.py
```

## Requisitos

- Python 3.10 o superior recomendado.
- Windows o Linux.
- En Linux, algunas funciones de recopilación pueden depender de utilidades del sistema disponibles en la distribución.
- Para la bandeja del sistema en Linux, el escritorio debe ofrecer soporte para iconos de bandeja o AppIndicator equivalente.

Dependencias Python actuales:

- Pillow
- pystray
- python-xlib

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/tu-usuario/obtener-informe-equipo.git
cd obtener-informe-equipo
```

## Ejecución rápida

La forma recomendada de iniciar la aplicación es usando el lanzador incluido:

```bash
python3 run_app.py
```

En Windows:

```bash
python run_app.py
```

El script [run_app.py](run_app.py) se encarga de:

- crear o reparar el entorno virtual `.venv`
- instalar las dependencias definidas en `requirements.txt`
- arrancar la aplicación principal

## Ejecución manual

Si prefieres preparar el entorno manualmente:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python informe_equipo.py
```

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python informe_equipo.py
```

## Uso

1. Inicia la aplicación.
2. Selecciona los formatos de exportación deseados.
3. Pulsa en "Generar informe".
4. Espera a que finalice la recopilación.
5. Abre la carpeta de salida o reexporta los archivos si lo necesitas.

Si la bandeja del sistema está disponible en el sistema operativo:

- puedes ocultar la ventana principal a la bandeja
- iniciar un escaneo desde el icono
- abrir la carpeta de informes desde el menú contextual
- cerrar la aplicación completamente desde la bandeja

## Informes generados

Los informes se guardan por defecto en la carpeta raíz del proyecto con nombres como:

```text
informe_NOMBRE-EQUIPO_YYYYMMDD_HHMMSS.txt
informe_NOMBRE-EQUIPO_YYYYMMDD_HHMMSS.html
informe_NOMBRE-EQUIPO_YYYYMMDD_HHMMSS.sql
```

## Compatibilidad

### Linux

- Usa utilidades del sistema como fuente de información para varios recopiladores.
- La apertura de archivos y carpetas se realiza mediante `xdg-open`.
- La bandeja del sistema depende del soporte real del entorno gráfico.

### Windows

- Usa consultas específicas del sistema cuando corresponde.
- La apertura de archivos y carpetas utiliza la aplicación predeterminada del sistema.
- La bandeja del sistema está preparada para funcionar mediante `pystray`.

## Posibles usos

- Inventario rápido de equipos.
- Soporte técnico y diagnóstico.
- Documentación de estaciones de trabajo.
- Exportación de datos para revisión o almacenamiento.

## Mejoras futuras sugeridas

- Configuración de carpeta de salida desde la interfaz.
- Filtros para seleccionar qué bloques del inventario generar.
- Notificaciones cuando finalice el escaneo.
- Firma o sellado de informes exportados.
- Empaquetado binario para distribución directa en Windows y Linux.

## Licencia

Este programa se distribuye bajo licencia MIT

Este programa selo ha creado entreunosyceros.net con mucho ☕ y 🚬