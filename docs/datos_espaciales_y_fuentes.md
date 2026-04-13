# Datos espaciales y fuentes de trafico

## Que son datos espaciales en este proyecto

Datos espaciales son datos que tienen geometria (forma en el mapa):

- `POINT`: un punto (ej. camara o punto de conteo).
- `LINESTRING`: una linea (ej. ruta o segmento vial).
- `POLYGON`/`MULTIPOLYGON`: un area (ej. departamento).

En PostGIS, cada registro tiene:

1. atributos (nombre, codigo, conteo, fecha),
2. geometria (`geom`) en coordenadas geograficas (SRID 4326).

## Como se usan esos datos

1. Dibujamos departamentos (poligonos).
2. Dibujamos rutas (lineas).
3. Cruzamos espacialmente rutas con departamentos (`ST_Intersects`).
4. Asociamos metricas de trafico por ruta para mostrar en popup/tooltip.

## De donde saldran los datos del mapa

### Capa geoespacial base (rutas y departamentos)

- Rutas principales: OpenStreetMap via OSMnx/Overpass.
- Departamentos: dataset oficial abierto (si disponible) o OSM/GeoBoundaries para bootstrap.

### Capa de trafico (conteos)

Prioridad de fuentes:

1. APIs publicas abiertas (si tienen cobertura util para Guatemala y terminos de uso compatibles).
2. Datos propios (conteo por vision en puntos de ruta).
3. Proveedores comerciales como complemento (TomTom/Here/Waze for Cities) segun acceso.

## Fuentes objetivo por tipo

1. Geometria de rutas

- OSMnx (consultas por lugar/pais) para red vial principal.
- pyrosm para extraer desde archivos `.pbf` cuando crezca volumen.

2. Geometria de departamentos

- GeoJSON oficial abierto (si disponible) o fuentes abiertas equivalentes.
- Carga y limpieza con GeoPandas.

3. Flujo de vehiculos

- API publica con series por tramo/hora (si existe cobertura).
- Si no hay API completa: carga por CSV/JSON desde reportes institucionales.
- Complemento con conteo propio por vision para cerrar vacios.

## Metricas que mostraremos

- `flujo_normal` (veh/h): promedio horario en periodo seleccionado.
- `flujo_hora_pico` (veh/h): maximo horario en periodo seleccionado.
- `hora_pico`: hora donde ocurre el maximo.
- `total_dia`: suma de intervalos diarios por ruta.

## Pipeline de datos recomendado

1. Ingestion: API externa o CSV -> tabla cruda.
2. Normalizacion: unificar esquema por ruta, fecha, hora, tipo de vehiculo.
3. Agregacion:
   - por hora (`traffic_hourly_agg`)
   - por dia (`traffic_daily_agg`, siguiente fase)
4. Publicacion API para frontend:
   - `/routes/main`
   - `/departments`
   - `/routes/{route_code}/departments`
   - `/routes/{route_code}/summary`

## Nota de realismo de datos

En el estado actual, la geometria de departamentos esta sembrada para validar flujo tecnico. En siguientes fases se reemplaza por limites oficiales mas precisos y se conectan fuentes reales de trafico.
