# MapLibre: como funciona en este proyecto

## Que es MapLibre

MapLibre GL JS es una libreria de JavaScript para renderizar mapas interactivos en el navegador. Dibuja el mapa con WebGL y permite agregar capas (lineas, puntos, heatmaps, etiquetas).

## De donde viene el mapa

En este proyecto, el mapa base se carga desde un estilo remoto:

- `https://demotiles.maplibre.org/style.json`

Ese archivo JSON de estilo define:

1. Fuentes de datos (`sources`): tiles vectoriales/raster que contienen calles y etiquetas.
2. Capas (`layers`): como se dibujan calles, rios, etiquetas, colores, grosores y zoom.
3. Configuracion visual global (tipografias, simbolos, etc.).

Cuando cargamos ese `style.json`, MapLibre descarga automaticamente los tiles necesarios segun el zoom y el area visible.

## Componentes implicados

1. Frontend Angular

- Archivo: `frontend/src/app/pages/map/map-page.component.ts`
- Crea la instancia `new maplibregl.Map(...)`.

2. Motor de mapa (MapLibre)

- Renderiza el mapa en el `div` con id `main-map`.
- Controla zoom, pan y controles de navegacion.

3. Fuente de estilo y tiles

- `style.json` remoto (demo de MapLibre).
- Tiles remotos referenciados por ese estilo.

4. Backend propio (fase siguiente)

- Entregara GeoJSON de rutas y metricas (`/routes/main`, `/peak-hours`).
- Esos datos se agregaran como capas encima del mapa base.

## Flujo de carga del mapa

1. Angular renderiza la pagina `MapPageComponent`.
2. `ngAfterViewInit` ejecuta `new maplibregl.Map(...)`.
3. MapLibre pide el `style.json`.
4. Con ese estilo, descarga tiles segun centro/zoom.
5. Dibuja mapa base en el canvas WebGL.
6. Se agregan controles (`NavigationControl`).
7. Luego se pueden agregar capas propias de trafico (GeoJSON/API).

## Que cambiaremos mas adelante

- Reemplazar estilo demo por uno de produccion (MapTiler, self-hosted, o estilo propio).
- Agregar capas de rutas principales de Guatemala desde `backend`.
- Colorear segmentos por flujo (vehiculos/hora) y horas pico.
- Agregar popups y filtros por fecha/hora.

## Consideraciones de produccion

- El estilo demo no debe usarse para produccion.
- Si usamos OpenStreetMap como base, se debe mostrar atribucion OSM/ODbL.
- Para alto trafico, conviene proveedor de tiles dedicado o infraestructura propia de tiles.
