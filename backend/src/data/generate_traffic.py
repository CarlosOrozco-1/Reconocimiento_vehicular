import random
import math
from datetime import datetime, date
import sys
import os

# Añadir el path del proyecto para importar src
sys.path.append(os.getcwd())

from src.api.db import get_connection

def generate_mock_traffic():
    """
    Genera datos sinteticos de trafico para las rutas principales.
    Crea sensores virtuales (count_points) y rellena traffic_hourly_agg con curvas realistas.
    """
    print("🚀 Iniciando generacion de datos sinteticos de trafico...")
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Obtener todas las rutas disponibles
            cur.execute("SELECT DISTINCT route_code FROM road_segments")
            routes = [row['route_code'] for row in cur.fetchall()]
            
            if not routes:
                print("❌ No se encontraron rutas en road_segments. Ejecuta db-init primero.")
                return

            print(f"📊 Procesando {len(routes)} rutas...")

            for route in routes:
                # 2. Buscar un segmento representativo (el que este mas al centro geograficamente)
                cur.execute("""
                    SELECT id, geom 
                    FROM road_segments 
                    WHERE route_code = %s 
                    ORDER BY id DESC 
                    LIMIT 1
                """, (route,))
                segment = cur.fetchone()
                if not segment: continue
                
                # 3. Crear punto de conteo (sensor virtual)
                cur.execute("SELECT id FROM count_points WHERE road_segment_id = %s", (segment['id'],))
                cp = cur.fetchone()
                if not cp:
                    cur.execute("""
                        INSERT INTO count_points (name, road_segment_id, direction, status, geom)
                        VALUES (%s, %s, %s, %s, ST_Centroid(%s))
                        RETURNING id
                    """, (f"Estacion Virtual {route}", segment['id'], 'Both', 'active', segment['geom']))
                    cp_id = cur.fetchone()['id']
                else:
                    cp_id = cp['id']
                
                # 4. Generar 24 horas de datos para hoy
                # Elegimos una hora pico aleatoria entre mañana (7-9) o tarde (17-19)
                peak_hour = random.choice([7, 8, 17, 18])
                base_flow = random.randint(50, 150)
                
                for hour in range(24):
                    # Curva gaussiana para simular comportamiento humano
                    dist = abs(peak_hour - hour)
                    gaussian = math.exp(-(dist**2)/12)
                    
                    # Flujo total con variacion aleatoria
                    flow = int(base_flow + (random.randint(600, 1200) * gaussian))
                    flow = max(10, flow + random.randint(-20, 20))
                    
                    # Mix de vehiculos (Moto 30%, Liviano 60%, Pesado 10%)
                    motos = int(flow * random.uniform(0.2, 0.35))
                    livianos = int(flow * random.uniform(0.5, 0.65))
                    pesados = max(0, flow - motos - livianos)
                    
                    cur.execute("""
                        INSERT INTO traffic_hourly_agg 
                        (count_point_id, hour, date, motorcycle_count, light_vehicle_count, heavy_vehicle_count, total_count, avg_speed)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (count_point_id, date, hour) DO UPDATE SET
                        total_count = EXCLUDED.total_count,
                        motorcycle_count = EXCLUDED.motorcycle_count,
                        light_vehicle_count = EXCLUDED.light_vehicle_count,
                        heavy_vehicle_count = EXCLUDED.heavy_vehicle_count,
                        avg_speed = EXCLUDED.avg_speed
                    """, (cp_id, hour, date.today(), motos, livianos, pesados, flow, random.uniform(40, 85)))
            
            conn.commit()
            print(f"✅ Datos generados exitosamente para {len(routes)} estaciones virtuales.")

if __name__ == "__main__":
    generate_mock_traffic()
