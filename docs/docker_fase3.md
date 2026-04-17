# Docker Fase 3 (Caddy + HTTPS)

En esta fase se agrega Caddy como reverse proxy y gestor de certificados TLS.

## Archivos clave

- `deploy/Caddyfile.local`
- `deploy/Caddyfile.prod`
- `docker-compose.yml` (servicio `caddy` por defecto)
- `.env.docker.example` (variables de host/puertos/caddyfile)

## 1) Configurar `.env.docker`

```bash
cp .env.docker.example .env.docker
```

Configura estos valores:

- `SITE_HOST` (en local: `localhost`)
- `CADDY_HTTP_PORT=80`
- `CADDY_HTTPS_PORT=443`
- `CADDYFILE_PATH=./deploy/Caddyfile.local`

## 2) Levantar stack con Caddy

```bash
docker compose --env-file .env.docker up -d --build
```

## 3) Verificar

- App: `https://SITE_HOST`
- API vía proxy: `https://SITE_HOST/api/health`

## Nota importante de TLS

Local:

- usa `Caddyfile.local` (TLS interno de Caddy)
- no requiere email ni dominio público

Producción (un solo dominio DuckDNS):

- cambia `SITE_HOST` a tu dominio (ej. `tusitio.duckdns.org`)
- cambia `CADDYFILE_PATH=./deploy/Caddyfile.prod`
- abre puertos 80/443 y apunta DNS a tu servidor

Con eso Caddy emite certificado público automáticamente sin separar app y api en dos dominios.

## Local en desarrollo

La API se publica bajo prefijo `/api` en el mismo host.
