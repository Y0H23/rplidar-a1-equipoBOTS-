RPLIDAR A1M8 — Equipo BOTS

Sistema de adquisición y procesamiento de datos del sensor RPLIDAR A1M8.

Permite:

- Visualización en tiempo real.
- Grabación de escaneos a CSV.
- Procesamiento de CSV sin hardware.
- Generación de métricas e informe reproducible.




1. Requisitos

- Python 3.10+
- RPLIDAR A1M8
Puerto serie:
Linux/Mac → /dev/ttyUSB0
Windows → COM5




2. Instalación

Crear entorno virtual:
Linux / Mac: python -m venv .venv
source .venv/bin/activate

Windows: python -m venv .venv
.venv\Scripts\activate

Instalar dependencias:
pip install -r requirements.txt

requirements.txt:
rplidar
numpy
matplotlib




3. Uso con sensor
   
Visualización en tiempo real

Linux: python src/view_live.py --port /dev/ttyUSB0

Windows: python src/view_live.py --port COM5

Grabar escaneo: python src/record_scan.py --port /dev/ttyUSB0 --seconds 10

Con decimación opcional: python src/record_scan.py --port /dev/ttyUSB0 --seconds 10 --decimation 5

Se genera: data/scan_YYYYMMDD_HHMMSS.csv

Formato: t, quality, angle_deg, dist_mm




4. Uso sin sensor 

Visualizar CSV: python src/view_live_csv.py --csv data/scan_720.csv --animate
Visualizar modo polar: python src/view_live_csv.py --csv data/scan_720.csv --animate --polar
Procesar CSV y generar informe: python src/record_scan_csv.py --csv data/scan_720.csv --out docs

Se generan:
docs/filtered_points.csv, docs/invalid_points.csv, docs/report_scan.md




5. Formato del CSV de referencia

Header obligatorio: quality,angle,measure_m,ok




6. Parada segura

El sistema siempre ejecuta: driver.shutdown_safe()

Orden interno:
stop()
stop_motor()
disconnect()
Esto evita daños en el motor del sensor.




7. Reproducibilidad

El proyecto puede ejecutarse desde cero:

1 - Crear entorno virtual.
2 - Instalar dependencias.
3 - Ejecutar con o sin sensor.

Todos los módulos funcionan tras: pip install -r requirements.txt

Equipo BOTS — SAR 2026
Especialidad Computación: grabación CSV y reproducibilidad.
