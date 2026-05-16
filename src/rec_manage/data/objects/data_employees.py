"""
data_employees.py
Handles data operations for employees and employee authentication.
Author: Ethan Hageman
Version: 0.1
"""
from src.rec_manage.data.database.connection import get_db

class EmployeeData:
    # Handles employee-related data operations for the current business

    def load_employees(self):
        # Load all employees for the current business and return formatted records
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT employee_id, name, default_status, profile_picture FROM employee WHERE business_id = ?",
                (self.business_id,)
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                name_parts = row[1].split(" ", 1)
                result.append({
                    "id": row[0],
                    "first_name": name_parts[0],
                    "last_name": name_parts[1] if len(name_parts) > 1 else "",
                    "status": row[2],
                    "profile_picture": row[3]
                })
            return result
        finally:
            conn.close()

    def add_employee(self, first_name, last_name, password, status="active", picture_path=None):
        # Add a new employee record with name, password, status, and optional profile picture path
        conn = get_db()
        cursor = conn.cursor()
        try:
            name = f"{first_name} {last_name}".strip()
            cursor.execute(
                "INSERT INTO employee (business_id, name, password, default_status, profile_picture) VALUES (?, ?, ?, ?, ?)",
                (self.business_id, name, password, status, picture_path)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def delete_employee(self, employee_id):
        # Delete the employee for the current business by their employee_id
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM employee WHERE employee_id = ? AND business_id = ?",
                (employee_id, self.business_id)
            )
            conn.commit()
        finally:
            conn.close()

    def authenticate_employee(self, employee_name, password):
        # Authenticate an employee by name and password
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT employee_id, business_id, name FROM employee WHERE name = ? AND password = ?",
                (employee_name, password)
            )
            row = cursor.fetchone()
            return {"employee_id": row[0], "business_id": row[1], "name": row[2]} if row else None
        finally:
            conn.close()