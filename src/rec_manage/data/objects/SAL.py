"""
SAL.py (Save and Load)
The connecting class and wrapper for all data handling modules,
gets the desired business ID, and passes it to the classes incharge of populating data for the app page.
Also handles invite code generation and redemption for business sharing.
Author: Ethan Hageman
Version: 0.1
"""
import secrets
from src.rec_manage.data.database.connection import get_db, init_db
from src.rec_manage.data.objects.data_business import Businessdata
from src.rec_manage.data.objects.data_employees import EmployeeData
from src.rec_manage.data.objects.data_zones import Zonedata
from src.rec_manage.data.objects.data_schedule import Scheduledata

class save_and_load(Businessdata, EmployeeData, Zonedata, Scheduledata):
    # The main class for handling all data operations related to the current business, including invite code management for sharing access between managers.
    def __init__(self, business_id=None):
        self.business_id = business_id
        try:
            init_db()
        except Exception as e:
            print(f"Database initialization error: {e}")


    def generate_invite_code(self):
        #Generates a unique invite code for the current business and stores it in the database, returning the code for sharing
        #using the secret library to generate a 8 bit random hex code
        code = secrets.token_hex(8)
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO invite_code (business_id, code) VALUES (?, ?)",
                (self.business_id, code)
            )
            conn.commit()
            return code
        finally:
            conn.close()

    def redeem_invite_code(self, code):
        #Redeems an invite code by checking if it exists and is unused, marks it as used, and returns the associated business_id for access
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT business_id FROM invite_code WHERE code = ? AND used = 0",
                (code,)
            )
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE invite_code SET used = 1 WHERE code = ?", (code,))
                conn.commit()
                return row[0]
            return None
        finally:
            conn.close()