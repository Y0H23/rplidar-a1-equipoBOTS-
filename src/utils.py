"""
utils.py
Máquina de estados (FSM) y checklist de arranque/parada para el sistema LiDAR.
Propietario: Actuadores.
Estados FSM (sensor conectado):
 INIT → DIAG → SCAN → STOP → DONE
 ↘ ↗
 ERROR
Eventos posibles: 'diag_ok', 'diag_fail', 'start', 'stop', 'error'
"""
from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass
class State(Enum):
 """Estados posibles del sistema."""
 INIT = auto() # estado inicial, esperando checklist
 DIAG = auto() # ejecutando diagnóstico del sensor
 SCAN = auto() # escaneo activo
 STOP = auto() # parada solicitada, ejecutando shutdown_safe
 DONE = auto() # finalización limpia
 ERROR = auto() # error irrecuperable
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
 Función pura de transición de estado.
 Args:
 state: estado actual
 event: evento que dispara la transición
 Returns:
 nuevo estado
 """
 # 'error' siempre lleva a ERROR desde cualquier estado
 if event == 'error':
 return State.ERROR
 # TODO [Actuadores]: completar todas las transiciones
 # Tabla de transiciones:
 # INIT + 'diag_ok' → DIAG
 # INIT + 'diag_fail' → ERROR
 # DIAG + 'start' → SCAN
 # SCAN + 'stop' → STOP
 # STOP + (cualquier) → DONE
 transitions = {
 (State.INIT, 'diag_ok'): State.DIAG,
 (State.INIT, 'diag_fail'): State.ERROR,
 # TODO [Actuadores]: añadir el resto de transiciones
 }
 return transitions.get((state, event), state) # sin transición: mantener
estado
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
