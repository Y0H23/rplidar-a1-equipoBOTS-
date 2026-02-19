"""
lidar_driver.py
Driver principal del RPLIDAR A1M8.
Propietarios: Sensores (diag/checklist) + LiDAR líder (frames/shutdown).

Uso:
 driver = LidarDriver('/dev/ttyUSB0')
 print(driver.diag())
 for frame in driver.frames():
     procesar(frame) # cada frame es un barrido completo 360°
 driver.shutdown_safe()
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Iterable, List, Tuple
from rplidar import RPLidar

# Tipo para cada punto: (quality, angle_deg, dist_mm)
# Se define un alias de tipo para que el código sea más legible y el IDE ayude.
ScanPoint = Tuple[int, float, float]

@dataclass
class ScanFrame:
    """
    Un barrido completo del sensor (aprox. 360°).
    Usamos un dataclass para agrupar fácilmente el momento exacto de la captura 
    junto con todos los puntos recogidos en esa vuelta.
    """
    t: float             # timestamp Unix (time.time()) para sincronización
    pts: List[ScanPoint] # lista de puntos, cada uno con (quality, angle_deg, dist_mm)

# ── Umbrales de filtrado (Sensores ajusta estos valores) ─────────────
# Parámetros físicos del RPLIDAR A1M8. Se declaran globales para fácil ajuste.
QUALITY_MIN = 10      # descartar puntos con calidad menor (evita ruido en los datos)
DIST_MIN_MM = 150.0   # 15 cm → mínimo físico del sensor (puntos más cercanos suelen ser errores ópticos)
DIST_MAX_MM = 12000.0 # 12 m → máximo especificado por el fabricante en interiores

class LidarDriver:
    """Interfaz de alto nivel para el RPLIDAR A1M8."""
    
    def __init__(self, port: str) -> None:
        """
        Inicializa la conexión con el sensor.
        
        Args:
            port: puerto serie (ej. '/dev/ttyUSB0' en Linux/Mac o 'COM5' en Windows)
        """
        self.port = port
        # Inicializamos la librería oficial que abstrae la comunicación serie
        self.lidar = RPLidar(port) 
        
    def diag(self) -> dict:
        """
        Lee info y health del sensor y devuelve un dict normalizado.
        Esto es crítico para que el estado de la FSM decida si es seguro arrancar.
        
        Returns:
            dict con claves: model, firmware, hardware, status, error_code
        """
        # Solicitamos datos directamente al hardware
        info = self.lidar.get_info()
        health = self.lidar.get_health()
        
        # TODO [Sensores]: extraer y normalizar los campos del dict 'info'
        # y de la tupla 'health'. Ejemplo de estructura esperada:
        # info → {'model': X, 'firmware': (M,m), 'hardware': X, ...}
        # health → (status_str, error_code_int)
        
        return {
            'model': None,      # TODO [Sensores]: info.get('model')
            'firmware': None,   # TODO [Sensores]: info.get('firmware')
            'hardware': None,   # TODO [Sensores]: info.get('hardware')
            'status': None,     # TODO [Sensores]: health[0]
            'error_code': None, # TODO [Sensores]: health[1]
            '_raw_info': info,  # mantener raw para depuración por si falla la normalización
            '_raw_health': health,
        }
        
    def frames(self, max_buf_meas: int = 500) -> Iterable[ScanFrame]:
        """
        Generador que produce ScanFrames en tiempo real.
        Se usa `yield` para entregar los datos frame a frame sin bloquear la memoria.
        
        Args:
            max_buf_meas: máximo de medidas en buffer interno (evita lag)
        
        Yields:
            ScanFrame con timestamp y lista de puntos filtrados.
        """
        # iter_scans() ya nos agrupa los puntos por vueltas completas
        for scan in self.lidar.iter_scans(max_buf_meas=max_buf_meas):
            pts: List[ScanPoint] = []
            
            for q, a, d in scan:
                # TODO [LiDAR líder]: añadir todos los filtros necesarios
                # Filtro básico de distancia y calidad para limpiar la nube de puntos:
                if d <= 0 or q < QUALITY_MIN:
                    continue  # Ignoramos medidas de distancia 0 o mala calidad
                    
                if not (DIST_MIN_MM <= d <= DIST_MAX_MM):
                    continue  # Ignoramos medidas fuera del rango físico del hardware
                    
                # Si pasa los filtros, añadimos el punto (convertido a los tipos correctos)
                pts.append((int(q), float(a), float(d)))
                
            if pts: # Solo emitimos el frame si quedaron puntos válidos tras el filtrado
                yield ScanFrame(t=time.time(), pts=pts)
                
    def shutdown_safe(self) -> None:
        """
        Parada segura del sensor.
        SIEMPRE llamar antes de cerrar el programa para evitar quemar el motor.
        Orden obligatorio de la librería: stop() → stop_motor() → disconnect()
        """
        try:
            # 1. Detenemos la emisión del láser y el envío de datos
            self.lidar.stop() 
            # 2. Cortamos la alimentación del motor rotativo
            self.lidar.stop_motor() 
        except Exception as e:
            # Capturamos excepciones para no crashear, pero avisamos del problema
            print(f'[WARN] shutdown_safe: {e}')
        finally:
            # 3. Este paso es CRÍTICO: liberamos el puerto serie. 
            # Si no se hace, el sensor quedará bloqueado para la próxima ejecución.
            self.lidar.disconnect() 

# ── Ejecución directa: diagnóstico rápido ────────────────────────────
# Este bloque solo se ejecuta si lanzamos este archivo directamente (no si se importa)
if __name__ == '__main__':
    import argparse
    
    # Configuramos los argumentos de línea de comandos para facilitar las pruebas
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', required=True, help='Puerto serie del sensor')
    args = ap.parse_args()
    
    # Instanciamos el driver usando el puerto proporcionado
    d = LidarDriver(args.port)
    print('Diagnóstico:', d.diag())
    print('Leyendo 3 frames...')
    
    count = 0
    # Probamos la lectura en vivo
    for fr in d.frames():
        print(f' Frame {count}: {len(fr.pts)} puntos, t={fr.t:.2f}')
        count += 1
        if count >= 3:
            break # Paramos tras 3 vueltas para probar que funciona
            
    # Garantizamos que el hardware se apaga correctamente al terminar el test
    d.shutdown_safe()
