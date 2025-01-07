'''
This module contains the class for the SignUpPage, which is used for creating a new customer in the E-Commerce Management System.
The functionalities of the portal include:
- A sign-up form where the user can enter their details (first name, last name, phone number, zip code, email, password).
- Validation of inputs to ensure the fields are filled out correctly and the passwords match.
- A check to prevent duplicate email entries in the database.
- Integration with the database to insert a new customer into the 'customers' table and the 'user_portal' table for login purposes.
- The ability to toggle password visibility for the user.

File: sign_up.py
Project: E-Commerce Management System
Author: A SQL Master
Course: DATA 201    
'''

import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QApplication
import os
import mysql
from shared import open_login_portal
from data201 import make_connection 

class SignUpPage(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setObjectName("Dialog")
        self.resize(422, 476)
        self.setWindowTitle("Sign Up Page")

        # Set dialog background color
        self.setStyleSheet("background-color: #F8E7E7;")

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)

        # Logo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "picture", "logo.png")

        logo = QtWidgets.QLabel()
        logo.setPixmap(QtGui.QPixmap(logo_path))
        logo.setScaledContents(True)
        logo.setAlignment(QtCore.Qt.AlignCenter)
        logo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Set minimum and maximum sizes to control resizing
        logo.setMinimumSize(132, 132)
        logo.setMaximumSize(132, 132)

        # Create a horizontal layout to center the logo
        logo_layout = QtWidgets.QHBoxLayout()
        logo_layout.addWidget(logo)
        logo_layout.setAlignment(QtCore.Qt.AlignCenter)  # Center the logo within the layout

        # Add the logo layout to the main layout
        main_layout.addLayout(logo_layout)

        # Title
        title = QtWidgets.QLabel("Sign Up Portal")
        title.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title)

        # Form layout
        form_layout = QtWidgets.QFormLayout()

        # First Name
        self.first_name = QtWidgets.QLineEdit()
        self.first_name.setStyleSheet(self._input_field_style())
        form_layout.addRow("First Name:", self.first_name)

        # Last Name
        self.last_name = QtWidgets.QLineEdit()
        self.last_name.setStyleSheet(self._input_field_style())
        form_layout.addRow("Last Name:", self.last_name)

        # Phone Number
        self.phone = QtWidgets.QLineEdit()
        self.phone.setStyleSheet(self._input_field_style())
        form_layout.addRow("Phone Number:", self.phone)

        # Zip Code
        self.zip_code = QtWidgets.QLineEdit()
        self.zip_code.setStyleSheet(self._input_field_style())
        form_layout.addRow("Zip Code:", self.zip_code)

        # Email
        self.email = QtWidgets.QLineEdit()
        self.email.setStyleSheet(self._input_field_style())
        form_layout.addRow("Email:", self.email)

        # Password
        password_layout = QtWidgets.QHBoxLayout()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setStyleSheet(self._input_field_style())
        password_layout.addWidget(self.password)

        # Password toggle button
        self.password_toggle = QtWidgets.QPushButton()
        self.password_toggle.setText("👀")
        self.password_toggle.setStyleSheet("border: none; background-color: transparent; font-size: 18px;")
        self.password_toggle.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.password_toggle)
        form_layout.addRow("Password:", password_layout)

        # Retype Password
        retype_password_layout = QtWidgets.QHBoxLayout()
        self.retype_password = QtWidgets.QLineEdit()
        self.retype_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.retype_password.setStyleSheet(self._input_field_style())
        retype_password_layout.addWidget(self.retype_password)

        # Retype Password toggle button
        self.retype_password_toggle = QtWidgets.QPushButton()
        self.retype_password_toggle.setText("👀")
        self.retype_password_toggle.setStyleSheet("border: none; background-color: transparent; font-size: 18px;")
        self.retype_password_toggle.clicked.connect(self.toggle_retype_password_visibility)
        retype_password_layout.addWidget(self.retype_password_toggle)

        form_layout.addRow("Retype Password:", retype_password_layout)

        # Add form layout to main layout
        main_layout.addLayout(form_layout)

        # Spacer
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

        # Sign-Up Button
        signup_button = QtWidgets.QPushButton("Sign Up")
        signup_button.setStyleSheet(self._button_style())
        signup_button.clicked.connect(self.sign_up)
        main_layout.addWidget(signup_button, alignment=QtCore.Qt.AlignCenter)

        # Back to Login Button
        back_to_login_button = QtWidgets.QPushButton("Back to Login")
        back_to_login_button.setStyleSheet(self._button_style())
        back_to_login_button.clicked.connect(lambda: open_login_portal(self))  # Use shared function
        main_layout.addWidget(back_to_login_button, alignment=QtCore.Qt.AlignCenter)

        # Track password visibility state
        self.password_visible = False
        self.retype_password_visible = False

    def _input_field_style(self):
        """Return the stylesheet for input fields."""
        return "background-color: #FFD6D6; border: 1px solid #FFAAAA; border-radius: 5px; padding: 3px;"

    def _button_style(self):
        """Return the stylesheet for buttons."""
        return "background-color: #FFAAAA; border: 1px solid #D66A6A; border-radius: 5px; padding: 10px 20px; font-size: 16px;"

    def toggle_password_visibility(self):
        """Toggle visibility for the password field."""
        if self.password_visible:
            self.password.setEchoMode(QtWidgets.QLineEdit.Password)
            self.password_toggle.setText("👀")  # Closed eye icon
        else:
            self.password.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.password_toggle.setText("🙈")  # Open eye icon
        self.password_visible = not self.password_visible

    def toggle_retype_password_visibility(self):
        """Toggle visibility for the retype password field."""
        if self.retype_password_visible:
            self.retype_password.setEchoMode(QtWidgets.QLineEdit.Password)
            self.retype_password_toggle.setText("👀")  # Closed eye icon
        else:
            self.retype_password.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.retype_password_toggle.setText("🙈")  # Open eye icon
        self.retype_password_visible = not self.retype_password_visible

    def sign_up(self):
        """
        Create a new customer in the database.
        """
        if not self.validate_inputs():
            return

        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        phone = self.phone.text().strip()
        zip_code = self.zip_code.text().strip()
        email = self.email.text().strip()
        password = self.password.text().strip()

        if not (first_name and last_name and phone and zip_code and email and password):
            QMessageBox.warning(self, "Input Error", "All fields must be filled!")
            return

        conn = make_connection(config_file="sqlproject.ini")
        cursor = conn.cursor()

        try:
            # Check if the email already exists in the customers table
            cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_email = %s", (email,))
            if cursor.fetchone()[0] > 0:
                # If email exists, show a warning and exit
                QMessageBox.warning(self, "Email Already Taken", "This email is already registered. Please use a different email.")
                return

            # Check if the zip code exists in the geolocation table
            cursor.execute("SELECT COUNT(*) FROM geolocation WHERE geolocation_id = %s", (zip_code,))
            if cursor.fetchone()[0] == 0:
                # If the zip code does not exist, show an error message and exit
                QMessageBox.warning(self, "Invalid Zip Code", "The provided zip code is invalid.")
                return

            # Generate a new customer ID
            new_customer_id = self._generate_new_customer_id(cursor)

            # Insert the new customer record
            sql = """
                INSERT INTO customers (customer_id, customer_first_name, customer_last_name, customer_email, customer_phone, customer_zip_code)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (new_customer_id, first_name, last_name, email, phone, zip_code))
            conn.commit()

            # Insert into user_portal table
            user_portal_query = """
                INSERT INTO user_portal (portal, user_name, password)
                VALUES (%s, %s, %s)
            """
            cursor.execute(user_portal_query, ("customer", email, password))
            conn.commit()

            QMessageBox.information(self, "Sign Up Successful", "Welcome! Thank you for signing up.")
            open_login_portal(self)  # Redirect to the login page

        except Exception as e:
            print(f"Error during creation: {e}")  # Log error
            QMessageBox.critical(self, "Error", "Failed to create account.")
        finally:
            cursor.close()
            conn.close()


    def _generate_new_customer_id(self, cursor):
        """
        Generate a new customer ID starting from 1001 and incrementing by 1.
        """
        cursor.execute("SELECT customer_id FROM customers ORDER BY customer_id DESC LIMIT 1")
        last_id = cursor.fetchone()

        if last_id:
            new_customer_id = last_id[0] + 1 
        else:
            new_customer_id = 1001

        return new_customer_id


    def validate_inputs(self):
        """Validate input fields."""
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        phone = self.phone.text().strip()
        zip_code = self.zip_code.text().strip()
        email = self.email.text().strip()
        password = self.password.text().strip()
        retype_password = self.retype_password.text().strip()

        if not (first_name and last_name and phone and zip_code and email and password and retype_password):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return False

        if password != retype_password:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return False

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Invalid Email", "Enter a valid email address.")
            return False

        return True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_portal = SignUpPage()
    login_portal.show()
    sys.exit(app.exec_())