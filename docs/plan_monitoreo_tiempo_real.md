# Plan de Implementación: Monitoreo y Análisis de Tráfico Histórico

Este documento detalla la estrategia para capturar, almacenar y visualizar datos de tráfico en las rutas principales de Guatemala utilizando el stack **FastAPI, PostgreSQL/PostGIS y TomTom API**.

## 1. Arquitectura de Datos (PostgreSQL)

Para generar gráficas y estadísticas de "Horas Pico", necesitamos separar la geometría (rutas) de las mediciones (historial).

### Tabla: `estaciones_conteo`
Puntos estratégicos en las rutas donde "tomaremos la foto" del tráfico.
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | SERIAL | Clave primaria |
| `nombre` | VARCHAR | Ej: "Entrada San Lucas", "Km 15 CA-9 Sur" |
| `geom` | GEOMETRY(Point, 4326) | Ubicación exacta para consultar a TomTom |
| `id_ruta_sigeplan` | INTEGER | FK para relacionar con tu GeoJSON |

### Tabla: `historial_trafico` (Serie Temporal)
Aquí se guarda el historial para las gráficas.
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | BIGSERIAL | Clave primaria |
| `estacion_id` | INTEGER | FK a la estación de conteo |
| `velocidad_actual` | INTEGER | Dato de TomTom (km/h) |
| `velocidad_libre` | INTEGER | Dato de TomTom (km/h) |
| `afluencia_calculada` | FLOAT | Porcentaje calculado (0-100%) |
| `fecha_hora` | TIMESTAMP | Fecha y hora del registro (Default: NOW()) |

---

## 2. El Worker (El Motor de Captura)

El **Worker** es un script de Python independiente que se ejecuta en segundo plano. No depende de que un usuario entre a la web; él trabaja solo.

### Funcionamiento lógico:
1. **Selección:** El script consulta en la base de datos todas las `estaciones_conteo`.
2. **Iteración:** Por cada estación, toma su latitud y longitud.
3. **Petición Externa:** Hace el `GET` a la API de TomTom.
4. **Procesamiento:** Calcula el nivel de congestión:
   `afluencia = 100 - ((velocidad_actual / velocidad_libre) * 100)`
5. **Persistencia:** Guarda el resultado en la tabla `historial_trafico`.

### Programación (Scheduling):
Para un proyecto universitario, puedes usar **`APScheduler`** dentro de FastAPI o un simple **Cron Job** de Linux que ejecute el script cada 15 minutos.

### Módulo de visualización de peticiones (nuevo)

Para validar que el worker está vivo y realizando consultas en tiempo real, se agrega un módulo de observabilidad:

1. **Tabla de ejecución:** `worker_request_log`
   - `id`, `worker_name`, `ruta_codigo`, `estacion_id`, `request_url`, `status_code`, `duracion_ms`, `resultado`, `error`, `created_at`.
2. **Tabla de estado del worker:** `worker_status`
   - `worker_name`, `last_run_at`, `last_success_at`, `requests_ok`, `requests_error`, `status`.
3. **Endpoint de monitoreo:**
   - `GET /api/v1/monitor/worker/status`
   - `GET /api/v1/monitor/worker/requests?minutes=60`
4. **Vista en frontend (Angular):**
   - contador de peticiones por minuto,
   - éxito/error en tiempo real,
   - última ejecución,
   - tabla de últimas 50 solicitudes,
   - botón para iniciar worker,
   - botón para detener worker.
5. **Indicadores visuales recomendados:**
   - verde: worker activo y exitoso,
   - amarillo: degradado (errores intermitentes),
   - rojo: sin peticiones recientes o error sostenido.

---

## 3. Visualización en Angular (La Gráfica)

Para "lucirte", la etiqueta (Tooltip) al pasar el mouse debe invocar un pequeño componente de gráfica:

1. **Endpoint de Historial:** Crea un endpoint en FastAPI: `GET /api/v1/trafico/historial/{estacion_id}`.
2. **Filtro:** Que devuelva los registros de las últimas 24 horas.
3. **Librería Recomendada:** **ApexCharts** o **Chart.js**.
4. **Impacto Visual:** - Eje X: Horas (00:00 - 23:00).
   - Eje Y: Porcentaje de Afluencia.
   - Resaltado: Sombrear las áreas donde la afluencia supera el 70% (Horas Pico).

---

## 4. Próximos Pasos Recomendados

1. **Definir Puntos:** Identifica 10 puntos críticos en Guatemala (Ej: Mixco, Villa Nueva, Carretera a El Salvador).
2. **Script Inicial:** Crear el script de Python que use `httpx` para conectar TomTom con tu DB.
3. **Trigger:** Configurar el script para que corra automáticamente.
4. **Monitoreo del Worker:** Implementar tablas de log/estado + endpoints + vista Angular en tiempo real.

---

## 5. Ajuste al modelo actual del proyecto

Este plan se puede aplicar directamente al proyecto actual. Para acoplarse a la estructura existente:

1. **Rutas principales**
   - reutilizar `road_segments` y `route_code` ya cargados (SEGEPLAN).
2. **Puntos de sondeo**
   - derivarlos de geometría de ruta (interpolación en PostGIS) y persistir en `estaciones_conteo`.
3. **Resumen en mapa**
   - mantener endpoint `GET /routes/{route_code}/summary?include_live=true`.
4. **Escalabilidad inicial**
   - empezar con rutas principales calibradas (por ejemplo CA-2, CA-1, CA-9),
   - ampliar cobertura con más puntos y reintentos controlados.
5. **Gestión de rutas en monitoreo**
   - permitir agregar rutas al worker sin redeploy,
   - permitir quitar rutas del worker en tiempo de ejecución,
   - exponer endpoints para listar/agregar/eliminar rutas monitoreadas.
