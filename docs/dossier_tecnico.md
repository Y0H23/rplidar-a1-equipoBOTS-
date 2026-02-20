






## Actuadores: 
## Operación Segura, Diagrama FSM y Checklist

### 1. Máquina de Estados Finitos (FSM)
El comportamiento central del sistema y el flujo de ejecución se han modelado mediante una Máquina de Estados Finitos

Se han diseñado dos flujos dependiendo del modo de ejecución: 
**A. Flujo con Sensor Físico Conectado:**
**INIT:** Estado inicial, esperando el checklist
**DIAG:** Ejecutando diagnóstico del sensor
**SCAN:** Escaneo activo
**STOP:** Parada solicitada, ejecutando shutdown_safe
**DONE:** Finalización limpia
**ERROR:** Error irrecuperable

**B. Flujo del Pipeline CSV (Modo Simulación):**
Para el trabajo sin sensor, la FSM transita por las fases de procesamiento de datos:
**INIT:** Esperando validación del checklist
**LOAD:** Cargando y validando el CSV
**PROCESS:** Aplicando filtros y proyección XY
**SAVE:** Guardando archivos de salida
**SHUTDOWN:** Parada segura completada
**ERROR:** Fallo en algún paso

### 2. Reglas de Operación Segura
Para garantizar que el sensor no sufra daños mecánicos ni eléctricos, se han establecido las siguientes reglas:
**Fijación del hardware:** El sensor debe estar físicamente fijo y estable antes de iniciar
**Cableado:** El cable USB debe estar sin tensión excesiva
**Parada Segura Estricta:** Nunca se debe desconectar el cable bruscamente. 
Siempre se debe ejecutar el orden obligatorio: `stop()` -> `stop_motor()` -> `disconnect()`

### 3. Checklist de Arranque y Parada
Antes de permitir que la FSM pase del estado `INIT` al siguiente, se verifican los siguientes criterios de aceptación:

**Para el sensor físico:**
`lidar_fijo`: Sensor físicamente fijo/estable
`cable_ok`: Cable USB sin tensión excesiva
`parada_probada`: Se ha verificado shutdown_safe()
`puerto_correcto`: Puerto serie identificado y accesible

**Para el pipeline CSV:**
`csv_exists`: El archivo CSV existe en disco
`header_ok`: El header del CSV es válido
`scan_length_ok`: El CSV tiene el nº esperado de filas
`processed_ok`: El filtrado/proyección completó sin errores
`files_saved_ok`: Los archivos de salida se guardaron









