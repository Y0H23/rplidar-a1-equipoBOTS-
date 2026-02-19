"""
view_live_csv.py
Visualización del CSV de referencia (scan_720.csv).
Propietario: Visión Artificial.
Importa lidar_processing.py (contrato de interfaz — NO modificar).
Modos:
 Sin --animate : dibuja todos los puntos válidos de golpe.
 Con --animate : simula llegada progresiva de puntos (--step y --delay).
Uso:
 python src/view_live_csv.py --csv data/scan_720.csv --animate
"""
from __future__ import annotations
import time
import argparse
import matplotlib.pyplot as plt
from lidar_driver_csv import read_scan_csv
from lidar_processing import filter_and_project # contrato interfaz
def main(csv_path: str, animate: bool, step: int, delay: float):
 samples = read_scan_csv(csv_path)
 n_total = len(samples)
 # Proyectar puntos válidos usando el módulo compartido
 pts = filter_and_project(samples) # lista de (x,y,quality,angle,r)
 n_valid = len(pts)
 pct_valid = n_valid / n_total * 100 if n_total > 0 else 0
 fig, ax = plt.subplots(figsize=(7, 7))
 ax.set_title(f'RPLIDAR scan desde CSV | {n_valid}/{n_total} válidos
({pct_valid:.1f}%)')
 ax.set_xlabel('x (m)')
 ax.set_ylabel('y (m)')
 ax.set_aspect('equal', adjustable='box')
 ax.grid(True, alpha=0.3)
 ax.plot(0, 0, 'r^', markersize=10, label='Sensor (origen)')
 if not animate:
 # Modo estático: dibujar todo de una vez
 xs = [p[0] for p in pts]
 ys = [p[1] for p in pts]
 ax.scatter(xs, ys, s=6, c='cyan', alpha=0.8, label='Puntos válidos')
 ax.legend()
 plt.show()
 return
  # Modo animado: acumular puntos progresivamente
 xs, ys = [], []
 scat = ax.scatter(xs, ys, s=6, c='cyan', alpha=0.8)
 plt.ion()
 for i in range(0, len(pts), step):
 chunk = pts[i:i + step]
 xs.extend(p[0] for p in chunk)
 ys.extend(p[1] for p in chunk)
 scat.set_offsets(list(zip(xs, ys)))
 ax.set_title(
 f'CSV animado | {len(xs)}/{n_valid} puntos | ({pct_valid:.1f}%
válidos del total)'
 )
 plt.pause(0.001)
 time.sleep(delay)
 plt.ioff()
 plt.show()
 # TODO [Visión]: añadir modo polar (r vs theta) como vista alternativa.
 # TODO [Visión]: resaltar con marcador diferente los puntos inválidos.
 # TODO [Visión]: guardar automáticamente captura en
docs/capturas/live_view.png.
if __name__ == '__main__':
 ap = argparse.ArgumentParser()
 ap.add_argument('--csv', default='data/scan_720.csv')
 ap.add_argument('--animate', action='store_true', help='Animar llegada de
puntos')
 ap.add_argument('--step', type=int, default=20, help='Puntos por
actualización')
  ap.add_argument('--delay', type=float, default=0.02, help='Segundos entre
updates')
 args = ap.parse_args()
 main(args.csv, args.animate, args.step, args.delay)
