# Módulo de monitoreo del worker

## Qué incluye

1. Control runtime del worker TomTom:

- `POST /monitor/worker/start`
- `POST /monitor/worker/stop`

2. Estado y observabilidad:

- `GET /monitor/worker/status`
- `GET /monitor/worker/requests?minutes=60&limit=100`

3. Curva temporal por ruta:

- `GET /routes/{route_code}/live-history?hours=24&limit=300`
- usado por dashboard para graficar afluencia en el tiempo.

4. Gestión de rutas monitoreadas:

- `GET /monitor/routes`
- `POST /monitor/routes/{route_code}`
- `DELETE /monitor/routes/{route_code}`

5. Persistencia:

- `monitored_routes`
- `worker_request_log`
- `worker_status`
- `route_live_history`

## Flujo operativo

1. Inicias worker desde dashboard.
2. Worker recorre rutas habilitadas en `monitored_routes`.
3. Consulta TomTom y guarda:
   - log de solicitud,
   - métricas de estado,
   - historial de velocidad/afluencia por ruta.
4. Dashboard refresca cada 10s y muestra estado real.
