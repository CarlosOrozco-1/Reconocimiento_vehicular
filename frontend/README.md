# Frontend

Aplicacion Angular para mapa interactivo y dashboard de trafico.

Decision vigente: Leaflet como motor de mapa para acelerar desarrollo del MVP.

## Estructura

- `src/app/pages/map/`
- `src/app/pages/dashboard/`
- `src/app/services/api/`

## Ejecucion en entorno aislado

```bash
distrobox enter vehicle-counter-dev
cd /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular/frontend
npm install
npm run start
```

App local: `http://localhost:4200`

Para la decision de stack y contexto tecnico:

- `docs/decision_stack_mapa.md`
- `docs/maplibre_como_funciona.md`

Requiere backend API en `http://localhost:8000` para cargar rutas principales.
