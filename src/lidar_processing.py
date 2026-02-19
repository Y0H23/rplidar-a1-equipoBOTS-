"""
lidar_processing.py
Módulo compartido de procesamiento de datos LiDAR.
Propietario: Adolfo Osuna Villanueva.
CONTRATO DE INTERFAZ:
 - is_valid(sample) → bool
 - polar_to_xy(sample) → (float, float) # (x_m, y_m)
 - filter_and_project(samples) → List[(x,y,q,a,r)]
Cualquier cambio en estas firmas debe comunicarse al equipo completo
antes de modificar el archivo.
"""
from __future__ import annotations
import math
from typing import List, Tuple
# ── Umbrales de filtrado (ajustar tras caracterizar el sensor) ──────
QUALITY_MIN = 20 # calidad mínima aceptable [0-255]
DIST_MIN_M = 0.20 # distancia mínima válida en metros
DIST_MAX_M = 10.0 # distancia máxima válida en metros

def is_valid(sample) -> bool:
  """
  Decide si una muestra LiDAR es válida.
  Criterios:
  1. ok == 1 (flag de validez del CSV / driver)
  2. quality >= QUALITY_MIN
  3. DIST_MIN_M < measure_m <= DIST_MAX_M
  Args:
  sample: objeto con atributos ok, quality, measure_m
  (compatible con LidarSample de lidar_driver_csv.py)
  Returns:
  True si la muestra supera todos los filtros, False en caso contrario.
  """
  # 1. Verificación de error de hardware o error de lectura en el CSV
  if sample.ok != 1:
   return False
  # 2. Descarte por baja intensidad de la señal
  if sample.quality < QUALITY_MIN:
   return False
  # 3. Filtrado espacial: nos aseguramos de que el punto esté en la zona útil de trabajo
  # (ni demasiado cerca del centro de rotación, ni más allá de donde el sensor es preciso)
  if not (DIST_MIN_M < sample.measure_m <= DIST_MAX_M):
   return False
  # Si supera todas las comprobaciones anteriores, la medida se considera fiable
  return True
 
def polar_to_xy(sample) -> Tuple[float, float]:
  """
  Convierte una muestra en coordenadas polares a cartesianas.
  El sistema de referencia tiene el sensor en el origen (0, 0).
  El eje X apunta a 0° (frente del sensor).
  El eje Y apunta a 90° (izquierda del sensor).
  Args:
  sample: objeto con atributos angle (grados) y measure_m (metros)
  Returns:
  Tupla (x_m, y_m) en metros.
  """
  # Convertimos los grados a radianes porque las funciones trigonométricas de math lo exigen
  rad = math.radians(sample.angle)
  # Proyección en el eje X (coseno del ángulo por la hipotenusa/distancia)
  x = sample.measure_m * math.cos(rad)
  # Proyección en el eje Y (seno del ángulo por la hipotenusa/distancia)
  y = sample.measure_m * math.sin(rad)
  
  return x, y
 
def filter_and_project(samples) -> List[Tuple]:
  """
  Aplica is_valid() a cada muestra y proyecta las válidas a XY.
  Args:
  samples: lista de LidarSample
  Returns:
  Lista de tuplas (x_m, y_m, quality, angle_deg, measure_m)
  Solo contiene muestras que superaron is_valid().
  """
  # Inicializamos la lista vacía donde acumularemos los puntos ya procesados
  result = []
  # Recorremos todas las muestras del escaneo (un barrido completo de 360 grados)
  for s in samples:
   # Solo procesamos la muestra si cumple los criterios de calidad y rango
   if is_valid(s):
    # Transformamos el punto válido al plano cartesiano
    x, y = polar_to_xy(s)
    # Empaquetamos las coordenadas cartesianas junto con los datos crudos originales
    # Visión Artificial necesitará (x,y) para dibujar, y Computación puede necesitar el resto
    result.append((x, y, s.quality, s.angle, s.measure_m))
    
  return result

# TODO [LiDAR líder]: ampliar con más funciones de procesamiento si el
# equipo las necesita durante la integración. Documentar cada una.
