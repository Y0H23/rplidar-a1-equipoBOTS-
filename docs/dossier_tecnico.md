






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



## Visión Artificial: 
## Interpretación, filtrado y visualización en tiempo real

### 1. Transformación de datos a cartesianas
El sensor entrega mediciones en coordenadas polares. Para representar el entorno en una pantalla 2D, transformamos los datos utilizando el módulo compartido:
**Variables de entrada:**
`quality`: Calidad de la señal de rebote
`angle`: Ángulo de barrido del láser en grados
`measure_m`: Distancia medida convertida a metros
**Proyección matemática:**
Los ángulos se pasan a radianes. Usando el sensor como origen (0,0), calculamos las coordenadas aplicando x = r * cos(θ) e y = r * sin(θ).

### 2. Filtrado de señal "engineering sense"
Para evitar que valores atípicos (outliers) deformen el mapa de la habitación, se aplica una máscara de filtrado antes de dibujar. Se descartan los puntos si incumplen estas reglas:
**Distancia mínima:** Se ignoran rebotes físicos muy cercanos (menores a 0.15 m)
**Distancia máxima:** Se descartan lecturas fuera del rango útil para la vista (mayores a 6.0 m)
**Calidad mínima:** Se exige un valor de reflectancia mínimo (`q >= 10`)

### 3. Modos de ejecución e interfaz
La visualización se ha construido con `matplotlib`, utilizando el modo interactivo (`plt.ion()`) para no bloquear el hilo de ejecución. 
**Con Sensor Físico (`view_live.py`):**
`Renderizado en vivo`: Se actualiza en cada frame de rotación usando fig.canvas.flush_events()
`Captura automática`: El script guarda una imagen de evidencia en docs/capturas/live_view.png

**Con pipeline CSV (`view_live_csv.py`):**
`--animate`: Simula el giro del láser dibujando los puntos progresivamente
`Modo Polar`: Vista alternativa circular de distancia vs ángulo
`Puntos inválidos`: Los puntos descartados se muestran con un marcador diferente para visualizarlos como ruido





