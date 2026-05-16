"""
data_schedule.py
Handles schedule loading and zone assignment operations.
Author: Ethan Hageman
Version: 0.1
"""
import json
import sqlite3
from src.rec_manage.data.database.connection import get_db

class Scheduledata:
    # Provides schedule and slot assignment operations for the current business

    def load_schedule(self, shift_date):
        # Load the schedule for the selected date and return formatted employee slot data
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT e.name, z.name, ts.start_time,
                       sa.slot_assignment_id, z.coordinates
                FROM slot_assignment sa
                JOIN time_slot ts ON sa.slot_id = ts.slot_id
                JOIN zone_assignment za ON sa.assignment_id = za.assignment_id
                JOIN zone z ON za.zone_id = z.zone_id
                JOIN employee e ON za.employee_id = e.employee_id
                WHERE ts.business_id = ? AND ts.shift_date = ?
            """, (self.business_id, shift_date))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                coords = json.loads(r[4]).get("geometry", {}).get("coordinates", [[]])[0]
                zone_lat = sum(c[1] for c in coords) / len(coords) if coords else 0
                zone_lng = sum(c[0] for c in coords) / len(coords) if coords else 0
                results.append({
                    "employee_name": r[0],
                    "zone_name": r[1],
                    "start_time": r[2],
                    "slot_assignment_id": r[3],
                    "zone_lat": zone_lat,
                    "zone_lng": zone_lng
                })
            return results
        finally:
            conn.close()

    def assign_employee_to_zone(self, employee_id, zone_id, shift_date, start_time, status="active"):
        # Assign an employee to a zone for a specific shift and ensure no conflicting slot exists
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT 1 FROM slot_assignment sa
                JOIN zone_assignment za ON sa.assignment_id = za.assignment_id
                JOIN time_slot ts ON sa.slot_id = ts.slot_id
                WHERE za.employee_id = ? AND ts.start_time = ?
                AND ts.shift_date = ? AND ts.business_id = ?
            """, (employee_id, start_time, shift_date, self.business_id))
            if cursor.fetchone():
                return None
        finally:
            conn.close()

        assignment_id = self.check_zone_id(employee_id, zone_id)
        slot_id = self.check_time_slot(start_time, shift_date)

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO slot_assignment (slot_id, assignment_id, status) VALUES (?, ?, ?)",
                (slot_id, assignment_id, status)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute(
                "SELECT slot_assignment_id FROM slot_assignment WHERE slot_id = ? AND assignment_id = ?",
                (slot_id, assignment_id)
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def check_zone_id(self, employee_id, zone_id):
        # check or create if needed the zone assignment linking an employee and a zone
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT assignment_id FROM zone_assignment WHERE zone_id = ? AND employee_id = ?",
                (zone_id, employee_id)
            )
            row = cursor.fetchone()
            if row:
                return row[0]
            cursor.execute(
                "INSERT INTO zone_assignment (zone_id, employee_id) VALUES (?, ?)",
                (zone_id, employee_id)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def check_time_slot(self, start_time, shift_date=None):
        # Create or retrieve the time slot for the current business and selected date/time
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT slot_id FROM time_slot WHERE business_id = ? AND start_time = ? AND shift_date = ?",
                (self.business_id, start_time, shift_date)
            )
            row = cursor.fetchone()
            if row:
                return row[0]
            cursor.execute(
                "INSERT INTO time_slot (business_id, start_time, shift_date) VALUES (?, ?, ?)",
                (self.business_id, start_time, shift_date)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def delete_assignment(self, slot_assignment_id):
        # Delete a schedule assignment by its slot_assignment_id
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM slot_assignment WHERE slot_assignment_id = ?",
                (slot_assignment_id,)
            )
            conn.commit()
        finally:
            conn.close()