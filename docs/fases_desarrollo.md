# Fases de desarrollo

Este documento define el plan oficial del proyecto. Trabajaremos fase por fase y no se avanza a la siguiente fase sin validar la anterior.

## Regla de trabajo

- Todo se ejecuta dentro del entorno aislado en Distrobox `vehicle-counter-dev`.
- No instalar dependencias globales fuera del entorno del proyecto.
- Flujo Git activo: ramas `desa`, `pre`, `pro` (ver `docs/git_workflow.md`).

Comandos base:

```bash
distrobox enter vehicle-counter-dev
cd /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular
```

## Fase 0 - Base del proyecto

Objetivo:

- Estructura por capas (`backend/`, `frontend/`, `docs/`) lista.
- Reglas de desarrollo y documentacion inicial definidas.

Entregables:

- Estructura de carpetas consolidada.
- `AGENTS.md` y README actualizados.

Estado: completada

## Fase 1 - Base geoespacial y backend API

Objetivo:

- Levantar backend con FastAPI.
- Preparar base de datos PostgreSQL + PostGIS.
- Crear modelo inicial para rutas, puntos de conteo y conteos por intervalo.

Entregables:

- Scripts SQL en `backend/scriptDB/`.
- Endpoint healthcheck y endpoints base (`/routes/main`, `/peak-hours`).
- Documento de arquitectura backend en `docs/`.

Estado: en progreso (base implementada)

## Fase 2 - Ingestion de datos y agregaciones

Objetivo:

- Ingerir conteos desde vision (YOLO) o fuentes externas.
- Consolidar agregados por hora, dia y ruta.

Entregables:

- Job de ingestion y job de agregacion.
- Tablas de agregados validadas.
- Export CSV para analisis.

## Fase 3 - Frontend mapa interactivo

Objetivo:

- Mostrar mapa de Guatemala con rutas principales.
- Pintar flujo vehicular por segmento y filtros por fecha/hora.

Entregables:

- App Angular funcional en `frontend/`.
- Vista de mapa y vista dashboard conectadas al backend.

## Fase 4 - Horas pico y analitica avanzada

Objetivo:

- Detectar horas pico por ruta y por region.
- Construir ranking de segmentos con mayor volumen.

Entregables:

- Endpoint y vista de horas pico.
- Reportes diarios y semanales.

## Fase 5 - Hardening y beta publica

Objetivo:

- Mejorar rendimiento, estabilidad y trazabilidad.
- Preparar despliegue beta y monitoreo.

Entregables:

- Logs y metricas base.
- Guia de despliegue.
- Checklist de calidad para beta.

## Criterios de avance por fase

- Codigo versionado y documentado.
- Pruebas minimas ejecutadas.
- Entregables de la fase publicados en `docs/`.
- Validacion funcional con datos de prueba.
