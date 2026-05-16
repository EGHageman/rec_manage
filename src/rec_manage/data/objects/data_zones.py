"""
data_zones.py
Handles data operations for zones and zone metadata.
Author: Ethan Hageman
Version: 0.1
"""
import json
from src.rec_manage.data.database.connection import get_db

class Zonedata:
    # Handles zone-related data operations for the current business

    def load_zones(self):
        # Load all zones for the current business and return parsed geojson data
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT zone_id, name, color, coordinates FROM zone WHERE business_id = ?",
                (self.business_id,)
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                try:
                    geojson = json.loads(row[3]) if row[3] else {}
                except json.JSONDecodeError:
                    geojson = {}
                result.append({
                    "id": row[0],
                    "label": row[1],
                    "name": row[1],
                    "color": row[2],
                    "geojson": geojson
                })
            return result
        finally:
            conn.close()

    def add_zone(self, name, color, geojson):
        # Add a new zone record and store the geojson polygon as JSON text
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO zone (business_id, name, color, coordinates) VALUES (?, ?, ?, ?)",
                (self.business_id, name, color, json.dumps(geojson))
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()