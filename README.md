# Vehicle Counter Guatemala

Proyecto de analitica de trafico para Guatemala con arquitectura por capas y separacion de servicios.

Objetivo funcional actual:

- visualizar rutas principales de Guatemala en mapa,
- mostrar estadisticas de flujo vehicular normal y horas pico,
- consultar detalle por ruta al hover/click,
- priorizar datos de APIs publicas y complementar con datos propios.

## Estructura actual

- `backend/`: API, analitica, pipelines de deteccion y base de datos.
- `frontend/`: aplicacion web (mapa interactivo y dashboards).
- `docs/`: documentacion funcional y tecnica del proyecto.
- `AGENTS.md`: reglas de desarrollo.

Plan de trabajo oficial por fases:

- `docs/fases_desarrollo.md`
- `docs/maplibre_como_funciona.md`
- `docs/arquitectura_backend_fase1.md`
- `docs/cambios_recientes.md`
- `docs/despliegue_caddy.md`
- `docs/git_workflow.md`
- `docs/conexion_dbeaver.md`
- `docs/postman/traffic_map_guatemala.postman_collection.json`
- `docs/rutas_departamentos_mapa.md`
- `docs/decision_stack_mapa.md`
- `docs/datos_espaciales_y_fuentes.md`
- `docs/matriz_fuentes_trafico.md`

## Entorno (Fedora + Distrobox)

```bash
distrobox enter vehicle-counter-dev
source .venv/bin/activate
```

Nota: los comandos del backend se ejecutan dentro de `backend/`.

## Ejecucion rapida del backend

```bash
cd backend
python -m src.main --source data/raw/videos/circulacionVehiculos.mp4 --output outputs/csv/events.csv --video-output outputs/videos/annotated.mp4
streamlit run src/dashboard/app_streamlit.py
```

API geoespacial (Fase 1):

```bash
cd backend
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Ejecucion rapida del frontend

```bash
distrobox enter vehicle-counter-dev
cd /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular/frontend
npm install
npm run start
```
