from __future__ import annotations

import csv
from pathlib import Path

from src.api.db import get_connection
from src.data.fetch_ine_vehicle_mix import build_vehicle_mix

def load_vehicle_mix_to_db() -> int:
    output_dir = Path("outputs/csv")
    output_csv = output_dir / "ine_vehicle_type_mix.csv"
    
    # Process the text file and generate the csv
    build_vehicle_mix(output_csv)
    
    query = """
        INSERT INTO vehicle_type_mix (
            vehicle_type, vehicle_count, percentage,
            source_dataset, source_resource, source_url
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    inserted = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Vaciar la tabla para refrescar los montos exactos si se vuelve a correr
            cur.execute("TRUNCATE TABLE vehicle_type_mix RESTART IDENTITY CASCADE")

            with open(output_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cur.execute(query, (
                        row.get("vehicle_type"),
                        row.get("count"),
                        row.get("percentage"),
                        row.get("source_dataset"),
                        row.get("source_resource"),
                        row.get("source_url"),
                    ))
                    inserted += 1
        conn.commit()
    return inserted

if __name__ == "__main__":
    count = load_vehicle_mix_to_db()
    print(f"Loaded {count} vehicle mix records into the database.")
