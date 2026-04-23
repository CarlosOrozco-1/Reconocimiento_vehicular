import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOMTOM_URL = 'https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json'
API_KEY = 'YUtYmvSNZ6LsVTYEc17rSljCiYbB1i55' # Api key de TomTom
HEADERS = {'User-Agent': 'Test', 'Accept': 'application/json'}

points = {
    'CA-1_Occidente_Chimaltenango': '14.6644,-90.8197',
    'CA-9_Sur_Escuintla': '14.3000,-90.7833',
    'CA-9_Norte_El_Progreso': '14.8500,-90.0333',
    'CA-1_Oriente_Jutiapa': '14.2833,-89.8833',
    'Ciudad_GT_Zona_10': '14.5986,-90.5126',
    'Ruta_Interamericana_San_Lucas': '14.6133,-90.6558'
}

print('Testing TomTom Coverage...')
for name, point in points.items():
    res = requests.get(TOMTOM_URL, params={'key': API_KEY, 'point': point}, headers=HEADERS, verify=False)
    if res.ok:
        data = res.json().get('flowSegmentData', {})
        print(f'[OK] {name} ({point}) -> Speed: {data.get("currentSpeed")} km/h')
    else:
        err = res.json() if 'application/json' in res.headers.get('content-type', '') else res.text
        print(f'[FAIL] {name} ({point}) -> {err}')
