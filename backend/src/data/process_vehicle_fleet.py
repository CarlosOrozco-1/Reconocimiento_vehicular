import pandas as pd
import sys
import os
from src.api.db import get_connection

# Aumentar path para importaciones
sys.path.append(os.getcwd())

def process_sat_data(file_path):
    """
    Procesa el archivo masivo de parque vehicular (300MB+) y extrae estadisticas
    para poblar la tabla vehicle_type_mix.
    """
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return

    print(f"📂 Procesando datos de SAT/INE: {file_path}...")
    
    # Procesar por trozos (chunks) para no saturar la RAM
    chunk_size = 100000
    totals = {}
    total_records = 0

    try:
        # Usamos pipe | como separador segun el peek anterior
        for chunk in pd.read_csv(file_path, sep='|', chunksize=chunk_size, encoding='latin-1', on_bad_lines='skip', low_memory=False):
            # Limpiar nombres de columnas
            chunk.columns = [c.strip() for c in chunk.columns]
            
            if 'TIPO_VEHICULO' in chunk.columns and 'CANTIDAD' in chunk.columns:
                # Asegurar que CANTIDAD sea numerico
                chunk['CANTIDAD'] = pd.to_numeric(chunk['CANTIDAD'], errors='coerce').fillna(0).astype(int)
                
                # Agrupar por TIPO_VEHICULO y sumar CANTIDAD
                summary = chunk.groupby('TIPO_VEHICULO')['CANTIDAD'].sum()
                for vtype, count in summary.items():
                    vtype = str(vtype).strip()
                    if vtype and vtype != 'nan':
                        totals[vtype] = totals.get(vtype, 0) + count
                total_records += len(chunk)
                print(f"⏳ Procesados {total_records} registros...")

        if not totals:
            print("⚠️ No se pudieron extraer datos. Verifica el formato del archivo.")
            return

        # Calcular porcentajes
        grand_total = sum(totals.values())
        final_data = []
        for vtype, count in totals.items():
            percentage = (count / grand_total) * 100
            final_data.append({
                'type': vtype,
                'count': int(count),
                'percentage': round(percentage, 2)
            })

        # Ordenar por cantidad descendente
        final_data = sorted(final_data, key=lambda x: x['count'], reverse=True)

        # Insertar en la base de datos
        print(f"💾 Insertando {len(final_data)} tipos de vehiculos en la DB...")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM vehicle_type_mix")
                for item in final_data:
                    cur.execute("""
                        INSERT INTO vehicle_type_mix (vehicle_type, vehicle_count, percentage, source_dataset)
                        VALUES (%s, %s, %s, %s)
                    """, (item['type'], item['count'], item['percentage'], 'SAT/INE Parque Vehicular 2026'))
            conn.commit()

        print("✅ Procesamiento completado exitosamente.")
        print(f"📈 Total vehiculos en Guatemala: {grand_total:,}")

    except Exception as e:
        print(f"❌ Error procesando el archivo: {e}")

if __name__ == "__main__":
    sat_file = "docs/INE_PARQUE_VEHICULAR_080426.txt"
    process_sat_data(sat_file)
