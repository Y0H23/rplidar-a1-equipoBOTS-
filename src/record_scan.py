"""
record_scan.py

Propietario: Computación

Formato CSV de salida:
    t, quality, angle_deg, dist_mm

Uso:
    python src/record_scan.py --port /dev/ttyUSB0 --seconds 10 --out data
"""

from __future__ import annotations   # Permite usar anotaciones de tipos modernas
import argparse                      # Para leer argumentos desde la línea de comandos
import csv                           # Para escribir archivos CSV
import time                          # Para manejo de tiempo y timestamps
from pathlib import Path             # Para manejar rutas de archivos de forma segura
from lidar_driver import LidarDriver # Driver personalizado para comunicarse con el LIDAR


def main():
    
    # Creamos el parser para argumentos de línea de comandos
    ap = argparse.ArgumentParser(description='Grabación de escaneo RPLIDAR a CSV')
    
    # Puerto serie obligatorio
    ap.add_argument('--port', required=True, help='Puerto serie')
    
    # Duración de grabación en segundos (por defecto 10)
    ap.add_argument('--seconds', type=int, default=10, help='Duración de la grabación')
    
    # Carpeta donde se guardará el archivo CSV (por defecto "data")
    ap.add_argument('--out', default='data', help='Carpeta de salida')
    
    # Parseamos los argumentos
    args = ap.parse_args()

  
    
    # Creamos la carpeta de salida si no existe
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Creamos un nombre de archivo único usando timestamp
    # Ejemplo: scan_20260219_153012.csv
    filename = out_dir / f"scan_{time.strftime('%Y%m%d_%H%M%S')}.csv"

   
    
    # Creamos el driver del LIDAR indicando el puerto serie
    driver = LidarDriver(args.port)

    # Guardamos el tiempo de inicio
    t0 = time.time()
    
    # Contador total de puntos guardados
    total_pts = 0

    print(f'[INFO] Grabando {args.seconds}s → {filename}')

    try:
        
        # Abrimos el archivo en modo escritura
        with filename.open('w', newline='') as f:
            
            # Creamos el escritor CSV
            writer = csv.writer(f)
            
            # Escribimos la cabecera del archivo
            writer.writerow(['t', 'quality', 'angle_deg', 'dist_mm'])
            
            # driver.frames() genera frames continuamente
            for fr in driver.frames():
                
                # Cada frame contiene múltiples puntos (fr.pts)
                # Cada punto tiene:
                # q = calidad
                # a = ángulo en grados
                # d = distancia en milímetros
                for q, a, d in fr.pts:
                    
                    # TODO [Computación]:
                    # Aquí se podría añadir decimación si hay demasiados puntos.
                    # Por ejemplo: guardar solo 1 de cada N puntos
                    # para reducir tamaño del archivo.

                    # Escribimos una fila en el CSV
                    writer.writerow([
                        f'{fr.t:.4f}',  # tiempo del frame con 4 decimales
                        q,              # calidad de la medición
                        f'{a:.3f}',     # ángulo en grados (3 decimales)
                        f'{d:.1f}'      # distancia en mm (1 decimal)
                    ])
                    
                    total_pts += 1  # Incrementamos contador

                # Si ya pasaron los segundos indicados, salimos del bucle
                if time.time() - t0 >= args.seconds:
                    break

    finally:
       
        # Cerramos el LIDAR correctamente aunque ocurra un error
        driver.shutdown_safe()


    
    print(f'[OK] Guardado: {filename}  ({total_pts} puntos)')


# Punto de entrada del script
if __name__ == '__main__':
    main()
