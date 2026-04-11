# Despliegue con Caddy y certificados

## Complejidad estimada

Con la estructura actual (`frontend` separado de `backend`), el despliegue con Caddy es de complejidad media-baja.

- Dificultad: 4/10
- Riesgo principal: DNS/firewall y puertos abiertos (80/443)
- Riesgo secundario: CORS entre frontend y backend si se usan dominios distintos

## Por que esta estructura ayuda

- `frontend/` puede desplegarse como sitio estatico (build Angular).
- `backend/` corre como API independiente (FastAPI + Uvicorn/Gunicorn).
- Caddy funciona como reverse proxy, TLS automatico con Let's Encrypt.

## Topologia recomendada

1. `app.tudominio.com` -> frontend Angular estatico.
2. `api.tudominio.com` -> backend FastAPI.
3. Caddy termina TLS y enruta trafico interno.

## Caddyfile base

```caddy
app.tudominio.com {
  root * /srv/traffic/frontend
  encode zstd gzip
  file_server
  try_files {path} /index.html
}

api.tudominio.com {
  reverse_proxy 127.0.0.1:8000
  encode zstd gzip
}
```

## Requisitos minimos

- DNS A/AAAA correcto para ambos subdominios.
- Puertos `80` y `443` accesibles desde internet.
- FastAPI escuchando localmente en `127.0.0.1:8000` o red interna.
- Variables de entorno bien definidas (`POSTGRES_*`, `API_*`).

## Buenas practicas

- Mantener DB fuera de exposicion publica (sin `-p` externo en produccion).
- Limitar CORS en FastAPI a dominios reales de frontend.
- Agregar backups de Postgres y rotacion de logs.
- Definir entorno `staging` antes de produccion.
