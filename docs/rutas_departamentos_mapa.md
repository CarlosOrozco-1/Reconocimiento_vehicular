# Visualizacion de rutas y departamentos

## Como funciona

1. El frontend carga primero los departamentos (`/departments`) como poligonos.
2. Luego carga rutas principales (`/routes/main`) como lineas.
3. Al hacer clic sobre una ruta, consulta `/routes/{route_code}/departments`.
4. Consulta `/routes/{route_code}/summary` para flujo normal y hora pico.
5. En hover se muestra popup con datos de ruta y departamentos que cruza.
6. El usuario puede mostrar/ocultar capas con botones de control en la vista de mapa.

## Capas en Leaflet

- `departments-fill-layer`: relleno suave de departamentos.
- `departments-line-layer`: borde de departamentos.
- `routes-layer`: rutas principales.

## Endpoints implicados

- `GET /departments`
- `GET /routes/main`
- `GET /routes/{route_code}/departments`
- `GET /routes/{route_code}/summary`

## Nota de datos

En esta fase se usan geometrias semilla para validar flujo funcional. En fases siguientes se sustituiran por geometrias oficiales mas precisas.
