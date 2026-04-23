import random
import math
from datetime import datetime, date
import sys
import os

# Añadir el path del proyecto para importar src
sys.path.append(os.getcwd())

from src.api.db import get_connection

def get_sat_proportions():
    """
    Consulta la base de datos para obtener las proporciones reales de la SAT
    y mapearlas a nuestras 3 categorias: Motos, Livianos, Pesados.
    """
    mapping = {
        'motorcycle': ['MOTO', 'TRIMOTO', 'CUATRIMOTO'],
        'light': ['AUTOMOVIL', 'PICK UP', 'CAMIONETA', 'CAMIONETILLA', 'CAMIONETA SPORT', 'PANEL', 'JEEP'],
        'heavy': ['CAMION', 'MICROBUS', 'CABEZAL', 'BUS', 'CAMION FURGON', 'FURGON', 'SEMI REMOLQUE', 'CAMION VOLTEO', 'PLATAFORMA', 'PORTA CONTENEDOR']
    }
    
    proportions = {'motorcycle': 0.3, 'light': 0.6, 'heavy': 0.1} # Valores por defecto (fallback)
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT vehicle_type, percentage FROM vehicle_type_mix")
                rows = cur.fetchall()
                
                if rows:
                    m_perc = sum(float(r['percentage']) for r in rows if r['vehicle_type'].strip() in mapping['motorcycle'])
                    l_perc = sum(float(r['percentage']) for r in rows if r['vehicle_type'].strip() in mapping['light'])
                    h_perc = sum(float(r['percentage']) for r in rows if r['vehicle_type'].strip() in mapping['heavy'])
                    
                    total = m_perc + l_perc + h_perc
                    if total > 0:
                        proportions['motorcycle'] = m_perc / total
                        proportions['light'] = l_perc / total
                        proportions['heavy'] = h_perc / total
    except Exception as e:
        print(f"⚠️ No se pudo obtener el mix de SAT, usando valores por defecto: {e}")
        
    return proportions

def generate_mock_traffic():
    """
    FLUJO DE FUNCIONAMIENTO:
    1. Identifica las rutas reales cargadas en la DB (CA-1, CA-9, etc).
    2. Coloca un "Sensor Virtual" (count_point) en un punto centrico de cada ruta.
    3. Simula 24 horas de trafico usando una Curva de Distribucion Normal (Gaussiana).
    4. Aplica el Mix Vehicular real obtenido de la SAT/INE.
    
    NIVEL DE CONFIANZA:
    - Geografia: 100% (Datos oficiales SEGEPLAN).
    - Mix Vehicular: 90% (Datos oficiales SAT/INE 2026).
    - Volumen/Hora: 60% (Sintetico basado en patrones de ingenieria de trafico standard).
    """
    print("🚀 Iniciando generacion de trafico inteligente (Simulacion + SAT)...")
    
    # Obtener el ADN vehicular de Guatemala desde la SAT
    sat_mix = get_sat_proportions()
    print(f"🧬 Mix SAT aplicado: Motos({sat_mix['motorcycle']:.1%}), Livianos({sat_mix['light']:.1%}), Pesados({sat_mix['heavy']:.1%})")

    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Obtener todas las rutas disponibles (Red Primaria)
            cur.execute("SELECT DISTINCT route_code FROM road_segments")
            routes = [row['route_code'] for row in cur.fetchall()]
            
            if not routes:
                print("❌ No hay rutas. Ejecuta db-init primero.")
                return

            for route in routes:
                # 2. Sensor Virtual: Buscamos un segmento para 'anclar' el conteo
                cur.execute("SELECT id, geom FROM road_segments WHERE route_code = %s LIMIT 1", (route,))
                segment = cur.fetchone()
                if not segment: continue
                
                # 3. Asegurar que exista el punto de conteo en la DB
                cur.execute("SELECT id FROM count_points WHERE road_segment_id = %s", (segment['id'],))
                cp = cur.fetchone()
                if not cp:
                    cur.execute("""
                        INSERT INTO count_points (name, road_segment_id, direction, status, geom)
                        VALUES (%s, %s, %s, %s, ST_Centroid(%s))
                        RETURNING id
                    """, (f"Estacion {route}", segment['id'], 'Both', 'active', segment['geom']))
                    cp_id = cur.fetchone()['id']
                else:
                    cp_id = cp['id']
                
                # 4. Generar Curva de 24 Horas
                # Elegimos una hora pico (Rush Hour) para esta ruta
                peak_hour = random.choice([7, 8, 17, 18]) 
                base_flow = random.randint(100, 300) # Trafico minimo en la madrugada
                
                for hour in range(24):
                    # ALGORITMO GAUSSIANO: 
                    # Calcula la distancia a la hora pico. Mientras mas cerca, mas flujo.
                    dist = abs(peak_hour - hour)
                    gaussian_factor = math.exp(-(dist**2)/12) # Crea la 'campana' de trafico
                    
                    # El flujo pico es la base + una magnitud aleatoria multiplicada por el factor Gaussiano
                    total_flow = int(base_flow + (random.randint(800, 1600) * gaussian_factor))
                    
                    # Aplicar el Mix de la SAT al flujo total generado
                    motos = int(total_flow * sat_mix['motorcycle'])
                    livianos = int(total_flow * sat_mix['light'])
                    pesados = max(0, total_flow - motos - livianos)
                    
                    # Guardar en la tabla de agregados horarios
                    cur.execute("""
                        INSERT INTO traffic_hourly_agg 
                        (count_point_id, hour, date, motorcycle_count, light_vehicle_count, heavy_vehicle_count, total_count, avg_speed)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (count_point_id, date, hour) DO UPDATE SET
                        total_count = EXCLUDED.total_count,
                        motorcycle_count = EXCLUDED.motorcycle_count,
                        light_vehicle_count = EXCLUDED.light_vehicle_count,
                        heavy_vehicle_count = EXCLUDED.heavy_vehicle_count
                    """, (cp_id, hour, date.today(), motos, livianos, pesados, total_flow, random.uniform(30, 80)))
            
            conn.commit()
            print(f"✅ Trafico generado para {len(routes)} rutas usando ADN vehicular de la SAT.")

if __name__ == "__main__":
    generate_mock_traffic()
