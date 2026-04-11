# Propuesta: mapa interactivo de trafico para Guatemala

## Objetivo

Construir una plataforma para visualizar rutas principales de Guatemala, estimar volumen vehicular por tramo y detectar horas pico por zona/ruta.

## Fuentes de datos recomendadas

1. Datos propios (recomendado para empezar)

- Sensores por vision (YOLO + tracking) en puntos de conteo.
- Resultado: conteo por intervalo (5 min, 15 min, 1 hora) por punto y clase de vehiculo.

2. Datos cartograficos base

- OpenStreetMap para red vial principal (carreteras CA, RN, etc.).
- Consulta por Overpass API para extraer segmentos y metadatos.
- Licencia ODbL: agregar atribucion en mapa y documentacion.

3. Datos de trafico externos (opcionales)

- Waze for Cities: programa para entidades publicas, no siempre abierto para cualquier organizacion.
- TomTom Traffic API: flujo/velocidad por segmento (requiere API key y costos por uso).
- Google Maps Platform (Roads/Routes): util para matching/metadata, no reemplaza conteo historico nacional sin costos.

Nota: en esta etapa no se confirmo una API publica nacional/municipal de Guatemala con conteos masivos listos para consumo continuo. Se recomienda disenar la plataforma para usar datos propios + conectores opcionales.

## Arquitectura recomendada (v2)

### Backend

- FastAPI (Python) para API REST.
- Jobs de ingestion y agregacion con Celery o APScheduler.
- Capa GIS con PostGIS.

### Base de datos

- PostgreSQL + PostGIS.
- TimescaleDB (opcional) para series de tiempo de alto volumen.

### Frontend

- Angular + MapLibre GL JS (o Leaflet si se busca simplicidad).
- Graficas con Apache ECharts o Plotly.

### Infra

- Docker/Podman para servicios.
- Nginx como reverse proxy.
- MinIO/S3 para archivos grandes y exportaciones.

## Modelo de datos inicial

1. `road_segments`

- `id`
- `name`
- `route_code`
- `geom` (LINESTRING, SRID 4326)
- `department`

2. `count_points`

- `id`
- `name`
- `road_segment_id`
- `geom` (POINT)
- `direction`
- `status`

3. `traffic_counts`

- `id`
- `count_point_id`
- `timestamp`
- `interval_min`
- `motorcycle_count`
- `light_vehicle_count`
- `heavy_vehicle_count`
- `total_count`

4. `traffic_hourly_agg`

- `count_point_id`
- `date`
- `hour`
- `total_count`
- `avg_speed` (nullable)

## Indicadores clave

- Flujo por hora y por ruta.
- Top 10 segmentos con mayor volumen.
- Hora pico AM/PM por ruta y por dia.
- Variacion dia habil vs fin de semana.
- Mapa de calor por tramos.

## API backend (ejemplo)

- `GET /routes/main`
- `GET /segments/{id}/timeseries?from=&to=&interval=`
- `GET /heatmap?date=&hour=`
- `GET /peak-hours?route_code=&from=&to=`
- `POST /ingest/counts`

## Plan de implementacion rapido (4 semanas)

Semana 1

- Levantar Postgres/PostGIS + FastAPI.
- Cargar red vial principal de OSM.
- Definir puntos de conteo iniciales (10-30).

Semana 2

- Ingestion de conteos YOLO a `traffic_counts`.
- Agregaciones horarias y diarias.
- API de consulta para mapa y series temporales.

Semana 3

- Front Angular con mapa interactivo (segmentos + capas).
- Dashboard de horas pico y ranking por rutas.

Semana 4

- Alertas de congestion por umbral.
- Exportaciones CSV/Excel.
- Optimizacion de consultas espaciales e indices.

## Recomendacion final de stack

Para este nuevo alcance, Streamlit queda corto como interfaz principal geoespacial. Recomendado:

- Angular + MapLibre GL (frontend)
- FastAPI + PostGIS (backend/datos)
- Python jobs para analytics

Mantener Streamlit solo como consola interna de exploracion o QA.
