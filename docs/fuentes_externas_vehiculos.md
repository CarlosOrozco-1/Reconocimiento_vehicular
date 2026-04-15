# Fuentes externas validadas (vehiculos por tipo)

## Fuente principal validada: DATOS INE (CKAN API)

Portal:

- `https://datos.ine.gob.gt`

API CKAN:

- `https://datos.ine.gob.gt/api/3/action/package_search?q=vehiculos`
- `https://datos.ine.gob.gt/api/3/action/package_search?q=transito`

Conjunto util detectado:

- `ACCIDENTES DE TRÁNSITO - VEHICULOS INVOLUCRADOS`
- URL dataset: `https://datos.ine.gob.gt/dataset/accidentes-de-transito-vehiculos-involucrados`

Recursos (ejemplo 2024):

- `https://datos.ine.gob.gt/dataset/a241d504-1c89-49d2-a490-a73cfc21276d/resource/a59d6ca6-cea1-4d60-8c80-7e4a0c2fb879/download/base-de-datos-vehiculos-involucrados-pnc-2024.xlsx`

Diccionario de variables:

- `https://datos.ine.gob.gt/dataset/a241d504-1c89-49d2-a490-a73cfc21276d/resource/dd105b8e-929b-41be-a87a-7112ebfc2f8a/download/diccionario-vehiculos-involucrados.xlsx`

## Uso recomendado en dashboard

1. Descargar/ingestar archivo anual (XLSX/CSV).
2. Mapear tipos de vehiculo a categorias del proyecto:
   - motocicleta
   - liviano
   - pesado
3. Calcular porcentaje por tipo:
   - `% tipo = (conteo_tipo / total) * 100`
4. Integrar en panel de ruta con periodo seleccionado.

## Nota metodologica

Estos datos representan vehiculos involucrados en hechos de transito (no aforo total por carretera). Se pueden usar como indicador complementario del tipo de vehiculo, mientras se construye una fuente de aforo por ruta/hora.
