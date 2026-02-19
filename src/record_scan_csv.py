"""
record_scan_csv.py

Procesa un CSV de escaneo (grabado previamente), filtra los puntos según un
criterio definido en lidar_processing.py (contrato: NO modificar), y genera:

Salidas generadas en --out:
  - filtered_points.csv  → nube de puntos válidos proyectados a XY
  - report_scan.md       → informe markdown con métricas

Propietario: Computación

Uso:
    python src/record_scan_csv.py --csv data/scan_720.csv --out docs
"""

from __future__ import annotations  # Permite anotaciones modernas de tipos
import argparse                      # Para leer argumentos desde la CLI
from pathlib import Path             # Para manejar rutas de forma robusta

# Lee el CSV grabado por el script de adquisición (record_scan.py u otro similar)
from lidar_driver_csv import read_scan_csv

# Funciones del módulo compartido (CONTRATO: no modificar)
# - is_valid(s): decide si una muestra/punto es válida según el criterio oficial
# - polar_to_xy(s): convierte coordenadas polares (r, ángulo) a cartesianas (x,y)
from lidar_processing import is_valid, polar_to_xy


def main(csv_in: str, out_dir_str: str):
    """
    Procesa el archivo CSV de entrada, filtra puntos válidos, guarda los puntos
    proyectados a XY en un CSV y genera un informe en Markdown.

    Args:
        csv_in: ruta al archivo CSV de escaneo (entrada)
        out_dir_str: carpeta donde se escribirán los resultados (salida)
    """

    out = Path(out_dir_str)
    out.mkdir(parents=True, exist_ok=True)  # crea la carpeta si no existe

    
    # read_scan_csv() devuelve una lista de "samples" (objetos/estructuras)
    # que contienen campos como: ok, quality, angle, measure_m (según tu driver)
    samples = read_scan_csv(csv_in)
    n = len(samples)  # total de lecturas

   
    # Usamos is_valid(s) del módulo compartido (criterio oficial).
    valid = [s for s in samples if is_valid(s)]
    invalid = [s for s in samples if not is_valid(s)]

    filtered_csv = out / 'filtered_points.csv' # GUARDAR PUNTOS FILTRADOS (VÁLIDOS) A CSV

    # Abrimos el archivo para escribirlo (modo texto UTF-8)
    with filtered_csv.open('w', encoding='utf-8') as f:
        # Cabecera del CSV de salida
        # x_m,y_m: coordenadas cartesianas en metros
        # quality: calidad original
        # angle_deg: ángulo original en grados
        # measure_m: distancia/radio original en metros
        f.write('x_m,y_m,quality,angle_deg,measure_m\n')

        # Para cada punto válido:
        for s in valid:
            # Convertimos de polar a cartesiano
            x, y = polar_to_xy(s)

            # Guardamos con formato:
            # x,y con 6 decimales
            # angle con 3 decimales
            # measure_m con 4 decimales
         
            f.write(f'{x:.6f},{y:.6f},{s.quality},{s.angle:.3f},{s.measure_m:.4f} \n')

   
    # ok_ratio: porcentaje de muestras con s.ok == 1
    # si n==0, evitar división por cero
    ok_ratio = sum(1 for s in samples if s.ok == 1) / n if n else 0

    # valid_ratio: porcentaje que pasa el filtro is_valid
    valid_ratio = len(valid) / n if n else 0

    
    report = out / 'report_scan.md'

    # Escribimos un markdown con:
    # nombre de archivo de entrada
    # total de lecturas
    # ratio de ok==1
    # ratio de válidas
    # conteo de inválidas
    #
    # Además incluye el criterio de filtrado documentado (según lidar_processing.py)
    report.write_text(
        f"""# Informe de scan CSV

**Archivo de entrada:** `{csv_in}`
**Total de lecturas:** {n}
**ok == 1:** {ok_ratio:.2%}
**Válidas tras filtro (lidar_processing):** {valid_ratio:.2%}  ({len(valid)} puntos)
**Inválidas:** {len(invalid)} puntos

## Criterio de filtrado (lidar_processing.py)
- ok == 1
- quality >= 20
- 0.20 m < measure_m <= 10.0 m

## Archivos generados
- `{filtered_csv.name}`: nube de puntos válidos (x, y, quality, angle, r)

## TODO [Computación]
- Añadir CLI para ajustar umbrales de filtro sin editar el código.
- Exportar también las inválidas con el motivo de descarte.
- Añadir logging y control de errores (CSV malformado, rutas inexistentes).
""",
        encoding='utf-8'
    )

    # MENSAJES POR CONSOLA
    print(f'[OK] Generados:')
    print(f'     {filtered_csv}')
    print(f'     {report}')


if __name__ == '__main__':
    # Parser simple para usar el script desde consola
    ap = argparse.ArgumentParser()

    # Ruta del CSV de entrada (por defecto data/scan_720.csv)
    ap.add_argument('--csv', default='data/scan_720.csv')

    # Directorio de salida (por defecto docs)
    ap.add_argument('--out', default='docs')

    # Parsear argumentos y ejecutar
    args = ap.parse_args()
    main(args.csv, args.out)
