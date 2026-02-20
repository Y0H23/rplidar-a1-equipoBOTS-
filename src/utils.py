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
 Estados posibles del sistema (Máquina de Estados Finitos).
    
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
 Evalúa el estado actual y el evento recibido para determinar el siguiente estado lógico.
    
    Args:
        state (State): El estado actual de la máquina.
        event (str): El evento disparador ('diag_ok', 'diag_fail', 'start', 'stop', 'error').
        
    Returns:
        State: El nuevo estado estado tras aplicar la regla, o el mismo si no hay transición válido.
 """
 # Regla de seguridad prioritaria: "error" siempre nos lleva a ERROR desde cualquier estado
 if event == 'error':
  return State.ERROR

 # Nuevo...
 # Regla de finalización: si ya estamos en STOP, cualquier evento concluye en DONE
 if state == State.STOP:
   return State.DONE

 # Tabla completa de transiciones válidas según los requisitos del sistema
 transitions = {
   (State.INIT, 'diag_ok'): State.DIAG, # El checklist pasó, inciamos diagnóstico
   (State.INIT, 'diag_fail'): State.ERROR, # El checklist falló, abortamos
   (State.DIAG, 'start'): State.SCAN, # Diagnóstico correcto, encendemos el láser
   (State.SCAN, 'sopt'): State.STOP, # Usuario o programa solicita detener escaneo
  
 }
 return transitions.get((state, event), state) 
 
if __name__ == '__main__':
 # Demo de la FSM para comprobar que la lógica funciona aislada
 check = Checklist(lidar_fijo=True, cable_ok=True, parada_probada=True, puerto_correcto=True)
 print('Checklist OK:', all([check.lidar_fijo, check.cable_ok, check.parada_probada, check.puerto_correcto]))
 
 st = State.INIT
 for evento in ['diag_ok', 'start', 'stop', 'cualquier_cosa']:
  st = transition(st, evento)
  print(f' Evento: {evento!r:12} → Estado: {st.name}')
