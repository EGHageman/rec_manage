"""The web package.

This file conatins
the main web method
which controls the program
flow
Author: Ethan Hageman.
Version: 0.1
"""
import os
from flask import Flask
from typing import List
from src.rec_manage.data.web.PageController import PageController
from src.rec_manage.data.database.connection import init_db

class Web:
    """Controls the progams flow."""
    @staticmethod
    def main(args: List[str]):
        """Activates the web controller.

        Args:
            args: string from the command
            line
        """
        print("attempting to do the things with the starting")
        app = Flask(__name__, template_folder='../templates', static_folder='../static')

        app.secret_key = os.environ.get('SECRET_KEY')
        
        # Initialize database
        with app.app_context():
            try:
                init_db()
                print("Database initialized successfully")
            except Exception as e:
                print(f"Database initialization error: {e}")
        
        PageController.register(app)
        app.config['WTF_CSRF_ENABLED'] = False
        return app