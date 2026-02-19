"""
record_scan.py
Graba escaneos en tiempo real a un CSV con timestamp.
Propietario: Computación.
Formato CSV de salida:
 t, quality, angle_deg, dist_mm
Uso:
 python src/record_scan.py --port /dev/ttyUSB0 --seconds 10 --out data
"""
from __future__ import annotations
import argparse, csv, time
from pathlib import Path
from lidar_driver import LidarDriver
def main():
 ap = argparse.ArgumentParser(description='Grabación de escaneo RPLIDAR a CSV')
 ap.add_argument('--port', required=True, help='Puerto serie')
 ap.add_argument('--seconds', type=int, default=10, help='Duración de la
grabación')
 ap.add_argument('--out', default='data', help='Carpeta de salida')
 args = ap.parse_args()
 # Crear carpeta de salida si no existe
 out_dir = Path(args.out)
 out_dir.mkdir(parents=True, exist_ok=True)
 # Nombre de archivo con timestamp para no sobrescribir
 filename = out_dir / f"scan_{time.strftime('%Y%m%d_%H%M%S')}.csv"
 driver = LidarDriver(args.port)
 t0 = time.time()
 total_pts = 0
  print(f'[INFO] Grabando {args.seconds}s → {filename}')
 try:
 with filename.open('w', newline='') as f:
 writer = csv.writer(f)
 writer.writerow(['t', 'quality', 'angle_deg', 'dist_mm']) # header
 for fr in driver.frames():
 for q, a, d in fr.pts:
 # TODO [Computación]: añadir decimación si hay demasiados
puntos
 # Ejemplo: grabar solo 1 de cada N puntos para reducir tamaño.
 writer.writerow([f'{fr.t:.4f}', q, f'{a:.3f}', f'{d:.1f}'])
 total_pts += 1
 if time.time() - t0 >= args.seconds:
 break
 finally:
 driver.shutdown_safe()
 print(f'[OK] Guardado: {filename} ({total_pts} puntos)')
if __name__ == '__main__':
 main()
