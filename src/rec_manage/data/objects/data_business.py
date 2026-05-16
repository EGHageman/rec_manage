"""
data_business.py
Handles data operations related to the different businesses in the tables
Author: Ethan Hageman
Version: 0.1
"""
from src.rec_manage.data.database.connection import get_db

class Businessdata:
    #Handles data operations related to the different businesses in the tables

    def create_business(self, name, lat, lng):
        #Creates a new business entry in the database with the given name and location, returning the new business_id
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO business (name, lat, lng) VALUES (?, ?, ?)",
                (name, lat, lng)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_business_info(self):
        #Retrieves the name and location of the business
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT name, lat, lng FROM business WHERE business_id = ?",
                (self.business_id,)
            )
            row = cursor.fetchone()
            return {"name": row[0], "lat": row[1], "lng": row[2]} if row else None
        finally:
            conn.close()

    def add_manager(self, business_id, name, password, role="owner"):
        #Adds a new manager to the database for the given business, returning the new manager_id
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO manager (business_id, name, password, role) VALUES (?, ?, ?, ?)",
                (business_id, name, password, role)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def authenticate_manager(self, manager_name, password):
        #Authenticates a manager by name and password, checks in the database if there is a manager with a matching name and password
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT business_id, name FROM manager WHERE name = ? AND password = ?",
                (manager_name, password)
            )
            row = cursor.fetchone()
            return {"business_id": row[0], "name": row[1]} if row else None
        finally:
            conn.close()