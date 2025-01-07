'''
This module contains shared utility functions for handling database connections
and navigating between the login and signup portals in the E-Commerce Management System.

The functions are designed to:
- Establish a connection to the MySQL database.
- Open the login portal by closing the current window.
- Open the signup portal by closing the current window.

File: shared.py
Project: E-Commerce Management System
Author: A SQL Master
Course: DATA 201
'''

import mysql.connector
from PyQt5 import QtWidgets
from data201 import make_connection

def connect_to_database():
    """
    Establish a connection to the MySQL database using credentials and settings 
    from the provided config file ('sqlproject.ini').
    If an error occurs during the connection, an error message is displayed.
    
    Returns:
        connection: A MySQL database connection object if successful, otherwise None.
    """
    try:
        return make_connection(config_file = 'sqlproject.ini')
    except mysql.connector.Error as e:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Error connecting to the database: {e}")
        return None

def open_login_portal(current_window):
    """
    Close the current window and open the login portal.

    Args:
        current_window: The current window object that will be closed after opening the login portal.
    """
    from login_page import LoginPage  # Import here to avoid circular imports
    login_portal = LoginPage()
    login_portal.show()
    current_window.close()

def open_signup_portal(current_window):
    """
    Close the current window and open the signup portal.

    Args:
        current_window: The current window object that will be closed after opening the signup portal.
    """
    from sign_up import SignUpPage  # Import here to avoid circular imports
    signup_portal = SignUpPage()
    signup_portal.show()
    current_window.close()
