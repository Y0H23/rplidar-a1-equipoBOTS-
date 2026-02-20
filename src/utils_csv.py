"""
utils_csv.py
FSM para el pipeline CSV completo (sin sensor físico).
Propietario: Actuadores.
Estados FSM (pipeline CSV):
 INIT → LOAD → PROCESS → SAVE → SHUTDOWN
 (fallo) → ERROR en cualquier punto ↘
La parada segura aquí es simbólica (no hay motor real).
En la integración con hardware real se llama a shutdown_safe() del driver.
"""
from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass

class State(Enum):
 INIT = auto() # esperando validación del checklist
 LOAD = auto() # cargando y validando el CSV
 PROCESS = auto() # aplicando filtros y proyección XY
 SAVE = auto() # guardando archivos de salida
 SHUTDOWN = auto() # parada segura completada
 ERROR = auto() # fallo en algún paso


@dataclass
class Checklist:
 """Checklist de validación previa al pipeline CSV."""
 csv_exists: bool = False # el archivo CSV existe en disco
 header_ok: bool = False # el header del CSV es válido
 scan_length_ok: bool = False # el CSV tiene el nº esperado de filas (≥720)
 processed_ok: bool = False # el filtrado/proyección completó sin errores
 files_saved_ok: bool = False # los archivos de salida se guardaron
 
def shutdown_safe(driver=None) -> bool:
 """
 Parada segura simbólica para el pipeline CSV.
 En la versión con hardware real: llamar a LidarDriver.shutdown_safe().
 Returns:
 True si la parada fue limpia.
 """
 if driver is no None: 
  try:
   # Integración real: llamamos a la función del módulo lidar_diver.py
   driver.shutdown_safe()
   print('Parada segura ejecutado')
  except Exceptio as e: 
   print('Error al intentar detener el motor')
   return False
 else: 
  print('[FSM] Parada segura ejecutada (modo CSV).')
 return True


def run_fsm(check: Checklist) -> State:
 """
 Ejecuta la FSM del pipeline CSV.
 Avanza por los estados comprobando el checklist en cada transición.
 Si algún check falla, va a ERROR y ejecuta shutdown_safe().
 """
 st = State.INIT
 try:
  # INIT → LOAD
  st = State.LOAD
  if not (check.csv_exists and check.header_ok and check.scan_length_ok):
   raise ValueError('Fallo en LOAD: CSV no válido o incompleto.')
   
  # LOAD → PROCESS
  st = State.PROCESS
  if not check.processed_ok:
   raise ValueError('Fallo en PROCESS: error en filtrado/proyección.')
 
  # PROCESS → SAVE
  st = State.SAVE
  if not check.files_saved_ok:
   raise ValueError('Fallo en SAVE: no se pudieron guardar los archivos.')
  
  # SAVE → SHUTDOWN
  st = State.SHUTDOWN
  shutdown_safe()
  return State.SHUTDOWN
 except Exception as e:
  print(f'[FSM] ERROR en estado {st.name}: {e}')
  shutdown_safe()
  return State.ERROR



"""
 Documentación de la FSM:

 1. Anclaje: el sensor RPLIDAR debe estar fijado a la base antes de iniciar el programa
 2. Calbeado: el cable de alimentación y datos no debe entorpear el cabezal rotario
 3. Desconexión: prohibido desconectar el cable USB bruscamente mientras el estado sea SCAN. Siepre debe pasar por la secuencia 'stop'
 4. Ruidos anómalos: garantizar que la excepción capture el error y llame a 'shutdown_safe()'
"""

if __name__ == '__main__':
 # Demo: simular un pipeline exitoso
 check = Checklist(
  csv_exists=True, header_ok=True, scan_length_ok=True,
  processed_ok=True, files_saved_ok=True
 )
 final = run_fsm(check)
 print(f'Estado final: {final.name}')

