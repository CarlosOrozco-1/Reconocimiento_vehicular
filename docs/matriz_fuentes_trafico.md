# Matriz de fuentes de datos (Guatemala)

## Objetivo operativo

Responder en mapa/dashboard:

- rutas principales,
- total de vehiculos por hora y por dia,
- hora pico por ruta,
- detalle por ruta al hover/click.

## Matriz de fuentes propuesta

1. Geometria de departamentos

- Fuente candidata: IDEG/SEGEPLAN (GeoServer WFS).
- Capa validada: `agrip:03_Limites_departamentales`.
- Endpoint ejemplo:
  - `https://ideg.segeplan.gob.gt/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=agrip:03_Limites_departamentales&outputFormat=application/json&srsName=EPSG:4326`
- Campos clave (DescribeFeatureType): `departamen`, `cod_dep`, `geom`.

2. Geometria de rutas principales

- Fuente candidata: IDEG/SEGEPLAN (GeoServer WFS).
- Capas validadas:
  - `infraestructura:caminos` (red principal amplia)
  - `infraestructura:carretera_centroamericana` (eje CA)
- Endpoint ejemplo:
  - `https://ideg.segeplan.gob.gt/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=infraestructura:caminos&outputFormat=application/json&srsName=EPSG:4326`
- Campos clave: `no_ruta`, `categoria`, `revestimie`, `descripcio`, `geom`.

3. Trafico vehicular por ruta/hora

- Prioridad A: API publica con series por tramo/hora (si existe cobertura util).
- Prioridad B: archivos institucionales (CSV/JSON) periodicos.
- Prioridad C: datos propios de conteo (vision).

## Respuesta a la duda de CSV/importacion

No es obligatorio usar CSV siempre.

- Si existe API publica estable: ingestion directa API -> base de datos.
- Si no existe API continua: usar CSV/JSON como fuente intermedia es totalmente valido.

Conclusión: sí, hay que importar datos de alguna fuente externa; CSV es una opcion de bootstrap, no un requisito permanente.

## Flujo recomendado de ingestion

1. Extraer (API/WFS/CSV).
2. Guardar crudo en `traffic_flow_raw`.
3. Normalizar/agregar por hora en `traffic_hourly_agg`.
4. Servir al frontend con FastAPI (`/routes/{route_code}/summary`, `/peak-hours`).

## Estado de validacion actual

- WFS de SEGEPLAN accesible y con `outputFormat=application/json`.
- Capas geograficas clave detectadas para departamentos y caminos.
- API del proyecto ya consume datos agregados para mostrar resumen por ruta.
