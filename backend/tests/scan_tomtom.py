import requests
import psycopg
import urllib3
import concurrent.futures

urllib3.disable_warnings()

DB_DSN = 'postgresql://traffic_user:traffic_pass@db:5432/traffic_gt'
TOMTOM_URL = 'https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json'
API_KEY = 'YUtYmvSNZ6LsVTYEc17rSljCiYbB1i55'

print('Buscando cobertura en toda Guatemala...')

def check_point(route_code, lat, lon):
    if not lat or not lon: return None
    try:
        res = requests.get(TOMTOM_URL, params={'key': API_KEY, 'point': f'{lat},{lon}'}, verify=False, timeout=5)
        if res.ok:
            data = res.json().get('flowSegmentData')
            if data:
                return {'route': route_code, 'lat': lat, 'lon': lon, 'speed': data.get('currentSpeed')}
    except:
        pass
    return None

try:
    with psycopg.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                WITH segments AS (
                    SELECT route_code, (ST_Dump(geom)).geom as g
                    FROM road_segments
                ),
                points AS (
                    SELECT route_code, 
                           ST_Y(ST_LineInterpolatePoint(g, 0.2)) as lat1, ST_X(ST_LineInterpolatePoint(g, 0.2)) as lon1,
                           ST_Y(ST_LineInterpolatePoint(g, 0.5)) as lat2, ST_X(ST_LineInterpolatePoint(g, 0.5)) as lon2,
                           ST_Y(ST_LineInterpolatePoint(g, 0.8)) as lat3, ST_X(ST_LineInterpolatePoint(g, 0.8)) as lon3
                    FROM segments
                )
                SELECT route_code, lat1, lon1, lat2, lon2, lat3, lon3 FROM points;
            ''')
            rows = cur.fetchall()
            
    tasks = []
    for row in rows:
        route_code = row[0]
        tasks.append((route_code, row[1], row[2]))
        tasks.append((route_code, row[3], row[4]))
        tasks.append((route_code, row[5], row[6]))

    print(f'Evaluando {len(tasks)} puntos en paralelo...')
    found_routes = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_point = {executor.submit(check_point, r, lat, lon): (r, lat, lon) for r, lat, lon in tasks}
        for future in concurrent.futures.as_completed(future_to_point):
            result = future.result()
            if result:
                r = result['route']
                if r not in found_routes:
                    found_routes[r] = result
                    speed = result.get('speed')
                    print(f'[+] Cobertura encontrada en: {r} (Velocidad: {speed} km/h)')

    print('\\nResumen de rutas con cobertura:')
    for r, data in found_routes.items():
        print(f"{r}: {data['lat']}, {data['lon']}")
        
except Exception as e:
    print('Error:', e)
