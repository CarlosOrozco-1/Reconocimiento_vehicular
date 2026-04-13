# Decision de stack para mapa y datos geograficos

## Objetivo actualizado

Visualizar el mapa de Guatemala con rutas principales y construir un dashboard con:

- circulacion vehicular total en condiciones normales,
- circulacion vehicular en horas pico,
- detalle por ruta al pasar el mouse (tooltip/popup).

La prioridad es consumir fuentes publicas cuando esten disponibles y complementar con datos propios cuando no existan series abiertas.

## Analisis de alternativas

### Frontend: MapLibre vs Leaflet

- MapLibre es fuerte para vector tiles y estilos avanzados, pero agrega complejidad para un MVP de capas y popups.
- Leaflet es mas rapido de implementar para este caso (GeoJSON + tooltips + capas + filtros) y tiene ecosistema estable en Angular.

Decision recomendada para este proyecto ahora:

- Angular + Leaflet (con `@bluehalo/ngx-leaflet` o `@asymmetrik/ngx-leaflet`).

### Backend Python: OSMnx, pyrosm y GeoPandas

- `OSMnx`: excelente para descargar y analizar red vial (grafo, jerarquia, atributos de carretera).
- `pyrosm`: muy eficiente para lectura de extractos PBF grandes; util cuando crece volumen.
- `GeoPandas`: ideal para manipular departamentos, joins espaciales y exportar GeoJSON a frontend.

Decision recomendada:

- Base operativa: `GeoPandas` + `OSMnx`.
- Escalamiento de ingestion: agregar `pyrosm` cuando se trabaje con PBF nacionales completos y pipelines pesados.

## Arquitectura objetivo (alineada al MVP)

- Backend: FastAPI + PostGIS
- Procesamiento geoespacial: OSMnx + GeoPandas
- Frontend: Angular + Leaflet
- Dashboard: Angular charts (ECharts/Plotly)

## Alcance funcional del mapa

1. Capa de departamentos (poligonos).
2. Capa de rutas principales (lineas).
3. Interaccion hover/click por ruta:
   - nombre de ruta,
   - flujo normal,
   - flujo hora pico,
   - departamentos que cruza.
4. Filtros por fecha/hora y tipo de vehiculo.

## Plan de migracion tecnica (MapLibre -> Leaflet)

1. Crear componente Leaflet paralelo al actual.
2. Reusar endpoints actuales (`/routes/main`, `/departments`, `/routes/{route_code}/departments`).
3. Replicar controles de capas y popups.
4. Activar feature flag para cambiar de motor de mapa.
5. Retirar MapLibre cuando Leaflet quede validado.
