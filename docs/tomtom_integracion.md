# Integracion TomTom (detalle quirurgico)

## Objetivo

Cuando el usuario pasa el mouse sobre una ruta en el mapa, el backend consulta TomTom y devuelve datos de trafico en tiempo real para esa ruta.

## Flujo exacto

1. Frontend hace hover sobre una ruta (`route_code`).
2. Frontend consulta `GET /routes/{route_code}/summary?include_live=true`.
3. Backend calcula resumen historico local (`normal_flow`, `peak_flow`, `peak_hour`).
4. Backend busca puntos de prueba sobre la geometria de la ruta en PostGIS.
5. Backend intenta TomTom sobre 5 puntos distribuidos en la ruta (12%, 28%, 45%, 62%, 80%).
6. Si un punto devuelve 400 "Point too far", prueba el siguiente.
7. Si encuentra segmento valido, devuelve velocidad/tiempo/cierre en la respuesta.
8. Resultado se cachea por ruta (TTL configurable) para evitar saturar API y mejorar latencia.
9. Si no se encuentra segmento en tiempo real, la ruta queda con estado `unavailable` y no rompe el popup.

## Variables de entorno

- `TOMTOM_ENABLED=true`
- `TOMTOM_API_KEY=<tu_key>`
- `TOMTOM_ZOOM=10`
- `TOMTOM_TIMEOUT_SEC=12`
- `TOMTOM_CACHE_TTL_SEC=60`
- `TOMTOM_PROBE_MAX_POINTS=120`

## Calibracion de rutas

Para aumentar tasa de exito en rutas principales:

```bash
cd backend
./scripts/calibrate_tomtom.sh 50
```

La calibracion guarda un punto valido por ruta en `route_live_probe_points` y luego el hover usa ese punto primero.

Escaneo expandido (más agresivo) para encontrar nuevas rutas con cobertura:

```bash
./scripts/scan_tomtom_coverage.sh 50
```

Este escaneo prueba muchos más puntos por ruta y guarda un reporte en:

- `backend/outputs/csv/tomtom_route_scan.csv`

## Monitoreo del worker

Endpoints operativos:

- `GET /monitor/worker/status`
- `GET /monitor/worker/requests?minutes=60&limit=100`
- `POST /monitor/worker/start`
- `POST /monitor/worker/stop`

Gestión dinámica de rutas monitoreadas:

- `GET /monitor/routes`
- `POST /monitor/routes/{route_code}`
- `DELETE /monitor/routes/{route_code}`

## Campos live en la respuesta

- `live_status`: `ok`, `unavailable`, `disabled`, `error`
- `live_message`: detalle de estado
- `live_current_speed_kph`
- `live_free_flow_speed_kph`
- `live_current_travel_time_sec`
- `live_free_flow_travel_time_sec`
- `live_confidence`
- `live_road_closure`
- `live_probe_point` (lat/lon usado)

## Consideraciones de escalabilidad

- La consulta espacial por ruta usa geometria consolidada (no por cada segmento individual).
- Se usa cache por ruta para no golpear TomTom en cada hover.
- Si no hay segmento TomTom en el punto, hay fallback a varios puntos de la misma ruta.
