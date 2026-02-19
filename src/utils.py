"""
utils.py - Gestión de la Máquina de Estados (FSM) y Seguridad del Sistema LiDAR.
Este módulo define la lógica de control para el arranque, operación y parada 
segura del sensor, garantizando la integridad del motor y la calidad de los datos.

Propietario: Equipo de Actuadores.
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass


class State(Enum): 
 """
 Estados posibles del sistema LiDAR.
    
    Attributes:
        INIT: Estado inicial. El sistema espera la verificación del checklist físico.
        DIAG: Fase de diagnóstico. Se verifican comunicaciones y revoluciones del motor.
        SCAN: Estado operativo. Captura y procesamiento de nubes de puntos activa.
        STOP: Parada controlada. Desaceleración del motor y cierre de puertos.
        DONE: Finalización exitosa. El sistema puede ser desconectado.
        ERROR: Estado de fallo crítico. Requiere intervención manual.
 """
 
 INIT = auto() 
 DIAG = auto() 
 SCAN = auto() 
 STOP = auto() 
 DONE = auto() 
 ERROR = auto() 
 
@dataclass
class Checklist:
 """
 Checklist de arranque. Todos los campos deben ser True
 antes de permitir la transición INIT → DIAG.
 """
 lidar_fijo: bool = False # sensor físicamente fijo/estable
 cable_ok: bool = False # cable USB sin tensión excesiva
 parada_probada: bool = False # se ha verificado shutdown_safe()
 puerto_correcto: bool = False # puerto serie identificado y accesible


def transition(state: State, event: str) -> State:
 """
 Función pura de transición de estado (FSM).
    
    Controla el flujo del sistema basándose en eventos de hardware o software.
    
    Args:
        state (State): El estado actual de la máquina.
        event (str): El evento disparador ('diag_ok', 'diag_fail', 'start', 'stop', 'error').
        
    Returns:
        State: El nuevo estado resultante de la transición.
 """
 # El evento 'error' es una interrupción global que prioriza la seguridad.
 if event == 'error':
  return State.ERROR

 # Diccionario de transiciones definidas por el equipo de Actuadores
 transitions = {
   (State.INIT, 'diag_ok'): State.DIAG,
   (State.INIT, 'diag_fail'): State.ERROR,
 # TODO [Actuadores]: añadir el resto de transiciones
 }
 return transitions.get((state, event), state) 
 
if __name__ == '__main__':
 # Demo de la FSM
 check = Checklist(lidar_fijo=True, cable_ok=True,
 parada_probada=True, puerto_correcto=True)
 print('Checklist OK:', all([check.lidar_fijo, check.cable_ok,
 check.parada_probada, check.puerto_correcto]))
 st = State.INIT
 for evento in ['diag_ok', 'start', 'stop']:
 st = transition(st, evento)
 print(f' Evento: {evento!r:12} → Estado: {st.name}')
