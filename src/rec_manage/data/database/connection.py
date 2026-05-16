"""
connection.py
Database connection utilities for rec_manage.
Author: Ethan Hageman
Version: 0.1
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")


def get_db():
    #connects to the sqlite database and enables foreign_key constraints, returning the connection object
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    #initializes the database by executing the schema.sql file
    schema_path = os.path.join(os.path.dirname(__file__), "datactions", "tables.sql")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at {schema_path}")
    with get_db() as conn:
        with open(schema_path, "r") as f:
            conn.executescript(f.read())
        conn.commit()