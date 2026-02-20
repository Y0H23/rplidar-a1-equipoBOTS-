"""
view_live.py
Visualización en tiempo real del RPLIDAR A1M8.
Propietario: Visión Artificial (marisa lozano).
Cómo funciona la visualización en tiempo real con matplotlib:
 - plt.ion() activa el modo interactivo (no bloquea el hilo)
 - fig.canvas.draw() + fig.canvas.flush_events() refresca la ventana
 - Esto funciona bien hasta ~8 Hz (frecuencia de rotación del sensor)
 - Si se necesita mayor fluidez: explorar pyqtgraph o pygame
Uso:
 python src/view_live.py --port /dev/ttyUSB0 --range 6.0
"""
from __future__ import annotations
import argparse
import numpy as np
import matplotlib.pyplot as plt
from lidar_driver import LidarDriver
def polar_to_xy(pts):
 """
 Convierte una lista de ScanPoints a arrays numpy X, Y.
 Args:
 pts: lista de tuplas (quality, angle_deg, dist_mm)
 Returns:
 x, y: arrays numpy en metros
 q: array numpy de calidades (para colorear puntos opcionalmente)
 """
 #extraemos las calidades de todos los puntos y las guardamos en un array como decimales
 q = np.array([p[0] for p in pts], dtype=float)
 #extraemos los ángulos, pero los convertimos de grados a radianes porque numpy usa radianes para seno/coseno
 ang = np.deg2rad([p[1] for p in pts])
 #extraemos las distancias y las dividimos entre 1000 para pasar de milímetros a metros
 r = np.array([p[2] for p in pts], dtype=float) / 1000.0 # mm → m
 # TODO [Visión]: filtrar por rango de distancia y calidad mínima
 # antes de calcular x, y. Puntos fuera de rango distorsionan la vista.
 # Ejemplo:
 # mask = (r > 0.15) & (r < 6.0) & (q >= 10)
 # ang, r, q = ang[mask], r[mask], q[mask]

 #proyección a cartesianas con la coordenada X que es: distancia x coseno del ángulo
 x = r * np.cos(ang)
 #proyección a cartesianas con la coordenada Y que es la distancia por el seno del ángulo
 y = r * np.sin(ang)
 #devolvemos las tres matrices, coordenadas X e Y, y la calidad original
 return x, y, q
 
  def main():
   #leemos los parametros
 ap = argparse.ArgumentParser(description='Visualización en tiempo real
RPLIDAR')
 ap.add_argument('--port', required=True, help='Puerto serie
(/dev/ttyUSB0 o COM5)')
 ap.add_argument('--range', type=float, default=6.0, help='Rango máximo a
mostrar (metros)')
 args = ap.parse_args()
 
 # Inicializar driver y ventana matplotlib
 driver = LidarDriver(args.port)
 plt.ion() # modo interactivo: no bloquea
 #creamos la figura y los ejes con un tamaño cuadrado 7x7
 fig, ax = plt.subplots(figsize=(7, 7))
 #mantenemos proporciones 1:1 para no deformar la vista
 ax.set_aspect('equal', 'box')
 #establecemos los límites de los ejes con en el argumento range
 ax.set_xlim(-args.range, args.range)
 ax.set_ylim(-args.range, args.range)
 #etiquetas de la interfaz grafica
 ax.set_title('RPLIDAR A1M8 — Vista en tiempo real')
 ax.set_xlabel('X (m) → frente del sensor')
 ax.set_ylabel('Y (m) → izquierda del sensor')
 #añadimos una cuadrícula de fondo semitransparente para estimar distancias de manera visual
 ax.grid(True, alpha=0.3)
 #seleccionamos el punto (0,0) con un triángulo rojo para representar la ubicacion física del sensor
 ax.plot(0, 0, 'r^', markersize=10, label='Sensor') # posición del sensor
 ax.legend()
 # Scatter vacío que actualizaremos en cada frame
 scat = ax.scatter([], [], s=4, c='cyan', alpha=0.8)
 # Texto de info en pantalla
 info_text = ax.text(-args.range + 0.1, args.range - 0.3, '',
 fontsize=9, color='white',
 bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
 frame_count = 0
 
 try:
 #driver.frames() es un generador que nos da barridos de 360 grados
 for fr in driver.frames():
 #transforma datos polares del sensor a cartesianos para la pantalla:
 x, y, q = polar_to_xy(fr.pts)
 # Actualizar puntos en el scatter
 scat.set_offsets(np.c_[x, y])
 # Actualizar información en pantalla
 frame_count += 1
 info_text.set_text(
 f'Frame: {frame_count}\n'
 f'Puntos: {len(fr.pts)}\n'
 # TODO [Visión]: mostrar % válidos/inválidos
 )
 # Refrescar la ventana (clave para tiempo real)
 fig.canvas.draw()
 fig.canvas.flush_events()
 # TODO [Visión]: implementar captura automática cada N frames
 except KeyboardInterrupt:
 #detenemos la salida por consola cuando el usuario pulsa Ctrl+C
 print('\n[INFO] Detenido por el usuario (Ctrl+C)')
 finally:
 #parada segura obligatoria para evitar que el motor siga girando
 driver.shutdown_safe() # SIEMPRE parar el sensor al salir
 #ejecuta script:
 if __name__ == '__main__':
 main()
