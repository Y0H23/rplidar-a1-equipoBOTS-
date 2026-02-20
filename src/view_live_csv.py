"""
view_live_csv.py
Visualización del CSV de referencia (scan_720.csv).
Propietario: Visión Artificial (marisa lozano).
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
#importamos el contrato de interfaz del lider 
# is_valid: para separar buenos de malos. polar_to_xy: para proyectar
from lidar_processing import filter_and_project, is_valid, polar_to_xy # contrato interfaz

def main(csv_path: str, animate: bool, step: int, delay: float, polar_mode: bool):
#lectura de todas las muestras en bruto desde el archivo CSV
 samples = read_scan_csv(csv_path)
 n_total = len(samples)
 # Proyectar puntos válidos usando el módulo compartido
 #usamos filter_and_project para obtener los puntos válidos proyectados
 pts_validos = filter_and_project(samples) # lista de (x,y,quality,angle,r)
 n_valid = len(pts)
 pct_valid = n_valid / n_total * 100 if n_total > 0 else 0
#identificamos y separamos los puntos invalidos
#filtramos la lista original y nos quedamos con los que is_valid() marca como False
muestras_invalidas = [s for s in samples if not is_valid(s)]
#configuramos la ventana gráfica Matplotlib
 fig, ax = plt.subplots(figsize=(8, 8))
#configurar el modo de vista Polar vs Cartesiano
if polar_mode:
        #si el usuario pide modo polar creamos ejes especiales polares
        ax = fig.add_subplot(111, projection='polar')
        ax.set_title(f'RPLIDAR CSV (MODO POLAR) | {n_valid}/{n_total} válidos ({pct_valid:.1f}%)', pad=20)
        #el centro del grafico polar es el origen por defecto
    else:
        #modo cartesiano X e Y
        ax.set_title(f'RPLIDAR scan desde CSV | {n_valid}/{n_total} válidos
       ({pct_valid:.1f}%)')
        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.set_aspect('equal', adjustable='box')
        ax.plot(0, 0, 'r^', markersize=10, label='Sensor (origen)')
 ax.grid(True, alpha=0.3)

#dibujo de puntos invalidos
    # Dibujamos los puntos invalidos de fondo en rojo con una x para destacarlos
    if len(muestras_invalidas) > 0:
        if polar_mode:
            #en polar, necesitamos radianes y la distancia en metros
            inv_theta = [np.deg2rad(s.angle) for s in muestras_invalidas]
            inv_r = [s.measure_m for s in muestras_invalidas]
            ax.scatter(inv_theta, inv_r, color='red', marker='x', alpha=0.5, label='Inválidos / Ruido')
        else:
            #en cartesiano, usamos polar_to_xy del líder para proyectarlos
            inv_xs, inv_ys = [], []
            for s in muestras_invalidas:
                x, y = polar_to_xy(s)
                inv_xs.append(x)
                inv_ys.append(y)
            ax.scatter(inv_xs, inv_ys, color='red', marker='x', alpha=0.5, label='Inválidos / Ruido')
#dibujo de puntos validos        
if not animate:
 #modo estático: extraemos todas las coordenadas y pintamos de golpe
        if polar_mode:
            #indice 3 es ángulo en grados, Índice 4 es distancia en metros (según filter_and_project)
            val_theta = [np.deg2rad(p[3]) for p in pts_validos]
            val_r = [p[4] for p in pts_validos]
            ax.scatter(val_theta, val_r, s=6, c='cyan', alpha=0.8, label='Puntos válidos')
        else:
            #indice 0 es X, Índice 1 es Y
            xs = [p[0] for p in pts_validos]
            ys = [p[1] for p in pts_validos]
            ax.scatter(xs, ys, s=6, c='cyan', alpha=0.8, label='Puntos válidos')           
        ax.legend(loc='upper right')
else:
        # Modo animado: activamos el modo interactivo para simular el barrido del láser
        plt.ion()
        # Creamos un scatter vacío para ir rellenándolo poco a poco
        scat = ax.scatter([], [], s=6, c='cyan', alpha=0.8, label='Puntos válidos')
        ax.legend(loc='upper right')
     
        datos_x, datos_y = [], []
#bucle que avanza saltando de step en step puntos
 for i in range(0, len(pts), step):
 chunk = pts[i:i + step]
 if polar_mode:
                datos_x.extend(np.deg2rad(p[3]) for p in chunk) #eje X en polar es el ángulo (theta)
                datos_y.extend(p[4] for p in chunk)             #eje Y en polar es la distancia (radio)
            else:
                datos_x.extend(p[0] for p in chunk) # X cartesiana
                datos_y.extend(p[1] for p in chunk) # Y cartesiana   
            #actualizamos los datos del scatter con los nuevos puntos acumulados
            #np.c_ une las listas en pares de coordenadas esperadas por matplotlib
            scat.set_offsets(np.c_[datos_x, datos_y])
            #refrescamos la ventana y forzamos una pausa para crear la ilusión de animacion
            plt.pause(0.001)
            time.sleep(delay)    
        #apagamos el modo interactivo al terminar la animacion
        plt.ioff()
  
#guardar captura de pantalla automaticamente
    os.makedirs('docs/capturas', exist_ok=True)
    ruta_captura = 'docs/capturas/live_view.png'
    fig.savefig(docs/capturas/live_view.png)
    print(f'\n[INFO] Gráfico generado correctamente.')
    print(f'[INFO] Captura guardada de forma automática en: docs/capturas/live_view.png')
    #mantenemos la ventana abierta hasta que el usuario la cierre manualmente
    plt.show()

if __name__ == '__main__':
 ap = argparse.ArgumentParser(description='Visualizador CSV del RPLIDAR')
 ap.add_argument('--csv', default='data/scan_720.csv')
 ap.add_argument('--animate', action='store_true', help='Animar llegada de
puntos')
 ap.add_argument('--step', type=int, default=20, help='Puntos por
actualización')
  ap.add_argument('--delay', type=float, default=0.02, help='Segundos entre
updates')
 args = ap.parse_args()
main(args.csv, args.animate, args.step, args.delay, args.polar)
