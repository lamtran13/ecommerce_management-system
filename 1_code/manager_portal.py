'''
This module contains the class for the Manager Portal.
The Manager Portal has the following functionalities:
- Navigation through different sections like Seller Info, Seller Modify, and Dashboards.
- Display and manage seller information, including creation, updating, and deletion of sellers.
- Generate and display various business performance dashboards, including revenue trends, customer satisfaction, payment methods, and product sales.
- Dynamic data visualization using Matplotlib and Seaborn for various reports like sales, order status, and delivery performance.
- Filtering and querying data based on user input from dropdown menus (e.g., month, category, status).
- Integration with the database to fetch and update seller and business data.
- Provides functionality for managing seller-related data and business insights in a bike store environment.

File: manager_portal.py
Project: E-Commerce Management System
Author: A SQL Master
Course: DATA 201    
'''

import sys
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import (QDialog, QApplication, QTableWidgetItem, QHeaderView, QMessageBox, QTableWidget)
from data201 import make_connection
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from shared import open_login_portal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


conn = make_connection(config_file='sqlproject.ini')
cursor = conn.cursor()

class ManagerPortal(QDialog):
    """
    The main dialog for the Bike Store Manager portal.
    """
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        self.ui = uic.loadUi('manager_portal.ui')  # Load the UI file
             
        # Store the current seller_id
        self.current_seller_id = None

        # Set default screen
        self.ui.ManagerPortalStacked.setCurrentIndex(0) 

        # Setup QTableWidget buttons
        self._setup_sellers_table()
        self._setup_seller_details_table()
        
        # Setup sidebar buttons
        self._setup_sidebar()

        self._initialize_dropdowns()
        self._setup_refresh_button()
        self._setup_event_connections()
        self.setRevenue_trend_yearandmonth()  

        # Initialize seller modify and dashboard features
        self._initialize_seller_modify()
        self._initialize_dashboard()

        # Populate the sellers table
        self._populate_sellers_table() 

        self.showDashboard()
        self.showLabels()
        self.showDashboard2()
        
    # ------------------------ #
    # sidebar   
    # ------------------------ #
    def _setup_sidebar(self):
        """
        Connect sidebar buttons to respective screens.
        """
        self.ui.btnSellerInfo.clicked.connect(
            lambda: self.ui.ManagerPortalStacked.setCurrentIndex(0)  # Show first page
        )
        self.ui.btnModify.clicked.connect(
            lambda: self.ui.ManagerPortalStacked.setCurrentIndex(1)  # Show second page
        )
        self.ui.btnDashboard.clicked.connect(
            lambda: self.ui.ManagerPortalStacked.setCurrentIndex(2)  # Show third page
        )
        self.ui.btnDashboard_2.clicked.connect(
            lambda: self.ui.ManagerPortalStacked.setCurrentIndex(3)  # Show fourth page
        )
        self.ui.pushButton_exit.clicked.connect(self.logout)
    
    def logout(self):
        """Handle user logout."""
        self.close()
        open_login_portal(self) 
    
    # ------------------------ #
    # seller subpage    
    # ------------------------ #
    def _setup_sellers_table(self):
        """
        Configure the QTableWidget for displaying sellers' information.
        """
        self.ui.sellersTableWidget.setColumnCount(4)  # Set the number of columns
        self.ui.sellersTableWidget.setHorizontalHeaderLabels(['Seller ID', 'First Name', 'Last Name', 'Order Count'])  # Set column titles
        self.ui.sellersTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Automatically adjust column width
        self.ui.sellersTableWidget.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable direct editing of the table
        self.ui.sellersTableWidget.setSelectionBehavior(QTableWidget.SelectRows)  # Select the entire column when clicking
        self.ui.sellersTableWidget.setSelectionMode(QTableWidget.SingleSelection)  # Only allows selection of one column

    def _setup_seller_details_table(self):
        """
        Configure the QTableWidget for displaying selected seller's details.
        """
        self.ui.sellerDetailsWidget.setColumnCount(6)  # Set the number of columns
        self.ui.sellerDetailsWidget.setHorizontalHeaderLabels(['Seller ID', 'Email', 'Phone', 'Zipcode', 'City', 'State'])  # Set column titles
        self.ui.sellerDetailsWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Automatically adjust column width
        self.ui.sellerDetailsWidget.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable direct editing of the table
        self.ui.sellerDetailsWidget.setSelectionMode(QTableWidget.NoSelection)  # Disable selection of table content
    
    def _populate_sellers_table(self):
        # Establish a connection to the database using a configuration file for connection details
        conn = make_connection(config_file='sqlproject.ini')
        cursor = conn.cursor()

        # SQL query to retrieve seller information along with the count of orders each seller has processed
        sql = """
            SELECT s.seller_id, s.seller_first_name, s.seller_last_name, COUNT(i.seller_id) AS order_count
            FROM sellers s
            LEFT JOIN order_items i ON s.seller_id = i.seller_id
            GROUP BY s.seller_id, s.seller_first_name, s.seller_last_name
            ORDER BY order_count DESC;
        """
        # Execute the SQL query to fetch the results
        cursor.execute(sql)
        rows = cursor.fetchall()

        # Clear any previous rows in the sellers table widget before populating it with new data
        self.ui.sellersTableWidget.setRowCount(0)

        # Iterate through the fetched rows and insert them into the table widget
        for row_index, row_data in enumerate(rows):
            self.ui.sellersTableWidget.insertRow(row_index)  # Insert a new row for each seller
            for col_index, col_data in enumerate(row_data):
                # Populate each column of the row with the seller data (ID, first name, last name, and order count)
                self.ui.sellersTableWidget.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

        # Connect the cell click event to display the seller's detailed information when a row is clicked
        self.ui.sellersTableWidget.cellClicked.connect(self._display_seller_details)

        # Close the cursor and database connection
        cursor.close()
        conn.close()

    def _display_seller_details(self, row, column):
        """
        Display detailed information about the seller in the selected row.
        :param row: The row number of the clicked cell.
        :param column: The column number of the clicked cell (not used in this case).
        """
        # Get the seller ID from the first column of the clicked row
        seller_id_item = self.ui.sellersTableWidget.item(row, 0)
        if not seller_id_item:
            # Show a warning if no valid seller ID is found
            QMessageBox.warning(self, "Error", "Invalid selection!")
            return

        seller_id = seller_id_item.text()  # Extract the seller ID from the clicked row

        # Fetch and display the seller's details from the database
        conn = make_connection(config_file='sqlproject.ini')
        cursor = conn.cursor()

        try:
            # SQL query to fetch the seller's details along with their geolocation (city and state)
            sql = """
                SELECT s.seller_id, s.seller_email, s.seller_phone, s.seller_zip_code, g.city, g.state_name
                FROM sellers s 
                JOIN geolocation g ON g.geolocation_id = s.seller_zip_code
                WHERE s.seller_id = %s
            """
            cursor.execute(sql, (seller_id,))
            seller_details = cursor.fetchone()  # Fetch the seller's details

            if seller_details:
                # Clear previous details and populate the details widget with fetched seller data
                self.ui.sellerDetailsWidget.setRowCount(0)
                self.ui.sellerDetailsWidget.insertRow(0)
                for col_index, detail in enumerate(seller_details):
                    self.ui.sellerDetailsWidget.setItem(0, col_index, QTableWidgetItem(str(detail)))
            else:
                # If no details are found, show an information dialog
                QMessageBox.information(self, "No Details", "No details found for the selected seller.")
        except Exception as e:
            # Handle any exceptions that occur during the database query
            QMessageBox.critical(self, "Error", f"Failed to fetch seller details: {e}")
        finally:
            cursor.close()
            conn.close()



    # ------------------------ #
    # modify subpage    
    # ------------------------ #

    # Initialize the modify subpage by connecting UI elements (buttons) to their respective methods
    def _initialize_seller_modify(self):
        # Connect buttons to their corresponding functions for searching, clearing, updating, creating, and deleting seller information
        self.ui.btnSearchSeller.clicked.connect(self._search_seller)  # Search seller button
        self.ui.btnClearFields.clicked.connect(self._clear_seller_info)  # Clear fields button
        self.ui.btnUpdSeller.clicked.connect(self._update_seller_info)  # Update seller button
        self.ui.btnCreateSeller.clicked.connect(self._create_seller_info)  # Create new seller button
        self.ui.btnDeleteSeller.clicked.connect(self._delete_seller)  # Delete seller button
        
    def _initialize_dashboard(self):
        """
        Set up the dashboard page, including the population of dropdowns for sellers, states, and cities.
        These dropdowns are dynamically populated and trigger updates to the dashboard when their values change.
        """
        # Connect dropdowns to update the seller dashboard when their selection changes
        self.ui.cmbAllSellers.currentIndexChanged.connect(self._update_seller_dashboard)
        self.ui.cmbStates.currentIndexChanged.connect(self._update_seller_dashboard)
        self.ui.cmbCities.currentIndexChanged.connect(self._update_seller_dashboard)

        # Populate dropdowns with initial data for sellers, states, and cities
        self._populate_sellers_dropdown()
        self._populate_states_and_cities()

    # Populate the 'All Sellers' dropdown with seller full names
    def _populate_sellers_dropdown(self):
        """
        This function populates the 'All Sellers' dropdown with seller full names (first + last name).
        It fetches the seller IDs and names from the database and adds them to the dropdown list.
        """
        conn = make_connection(config_file="sqlproject.ini")
        cursor = conn.cursor()

        try:
            # SQL query to fetch seller IDs and concatenated first and last names for the dropdown options
            sql = """
                SELECT DISTINCT seller_id, CONCAT(seller_first_name, ' ', seller_last_name) AS full_name
                FROM sellers
                ORDER BY full_name
            """
            cursor.execute(sql)
            rows = cursor.fetchall()  # Fetch the rows containing seller information

            # Clear previous entries in the dropdown
            self.ui.cmbAllSellers.clear()

            # Add a default item to the dropdown list to prompt the user to select a seller
            self.ui.cmbAllSellers.addItem("Select Seller", userData=None)

            # Add each seller's full name to the dropdown list with their corresponding seller_id
            for seller_id, full_name in rows:
                self.ui.cmbAllSellers.addItem(seller_id + " " + full_name, userData=seller_id)

            # Set the default or first item as selected, if applicable
            if self.ui.cmbAllSellers.count() > 0:
                self.ui.cmbAllSellers.setCurrentIndex(0)

        except Exception as e:
            # If there is an error with the database query, display a critical error message
            QMessageBox.critical(self, "Error", f"An error occurred while populating seller dropdown: {e}")
        finally:
            # Close the cursor and database connection after the operation is complete
            cursor.close()
            conn.close()

    # state and city dropdown
    def _populate_states_and_cities(self):
        """
        Populate the states and cities dropdowns with data, with default placeholder options.
        """
        conn = make_connection(config_file="sqlproject.ini")
        cursor = conn.cursor()

        try:
            sql_states = "SELECT DISTINCT state_name FROM geolocation ORDER BY state_name"
            sql_cities = "SELECT DISTINCT city FROM geolocation ORDER BY city"

            cursor.execute(sql_states)
            states = [row[0] for row in cursor.fetchall()]
            cursor.execute(sql_cities)
            cities = [row[0] for row in cursor.fetchall()]

            # Clear and populate dropdowns with default options
            self.ui.cmbStates.clear()
            self.ui.cmbCities.clear()
            self.ui.cmbStates.addItem("Select a State")
            self.ui.cmbCities.addItem("Select a City")
            self.ui.cmbStates.addItems(states)
            self.ui.cmbCities.addItems(cities)

            # Connect signals for cascading updates
            self.ui.cmbStates.currentIndexChanged.connect(self._update_cities_based_on_state)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while populating state/city dropdowns: {e}"
            )
        finally:
            cursor.close()
            conn.close()

    def _update_cities_based_on_state(self):
        """
        Update the Cities dropdown based on the selected State.
        """
        selected_state = self.ui.cmbStates.currentText()
        if selected_state == "Select a State": 
            return

        conn = make_connection(config_file="sqlproject.ini")
        cursor = conn.cursor()

        try:
            # Fetch cities for the selected state
            sql = "SELECT DISTINCT city FROM geolocation WHERE state_name = %s ORDER BY city"
            cursor.execute(sql, (selected_state,))
            cities = [row[0] for row in cursor.fetchall()]


            self.ui.cmbCities.blockSignals(True)  
            self.ui.cmbCities.clear()
            self.ui.cmbCities.addItem("Select a City")
            self.ui.cmbCities.addItems(cities)
            self.ui.cmbCities.blockSignals(False)  

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while updating cities: {e}")
        finally:
            cursor.close()
            conn.close()

    # search    
    def _search_seller(self):
        """
        Search for a seller based on seller_id, seller_first_name, or seller_last_name.
        Supports combined queries and prompts user if multiple results are found.
        Ensures dropdown selection and input fields align.
        """
        # Reset any previously stored seller_id
        self.current_seller_id = None  

        # Extract dropdown selection and user-input fields
        selected_seller_id = self.ui.cmbAllSellers.currentData()  # Get seller_id from dropdown (None if "Select Seller")
        seller_id = self.ui.seller_id_search.text().strip()
        seller_first_name = self.ui.seller_first_name_search.text().strip()
        seller_last_name = self.ui.seller_last_name_search.text().strip()

        # Check if dropdown is set to "Select Seller"
        if selected_seller_id is None:
            # No dropdown selection; use the user-input fields
            if not (seller_id or seller_first_name or seller_last_name):
                QMessageBox.warning(self, "Input Error", "Please enter at least one search criterion.")
                return
        else:
            # Dropdown has a valid selection; check consistency with user input
            if seller_id and seller_id != selected_seller_id:
                QMessageBox.warning(
                    self, "Mismatch Error", 
                    "The dropdown selection and Seller ID input do not match. Please adjust your input."
                )
                return

            # Clear other fields since dropdown takes priority
            seller_id = selected_seller_id
            seller_first_name = seller_last_name = ""  

        conn = make_connection(config_file="sqlproject.ini")
        cursor = conn.cursor()

        try:
            # Build the SQL query for searching by seller_id, seller_first_name, or seller_last_name
            sql = """
                SELECT seller_id, seller_first_name, seller_last_name, seller_email, seller_phone
                FROM sellers
                WHERE (%s IS NULL OR seller_id = %s)
                AND (%s IS NULL OR seller_first_name LIKE %s)
                AND (%s IS NULL OR seller_last_name LIKE %s)
            """
            query_values = (
                seller_id if seller_id else None, seller_id if seller_id else None,
                seller_first_name if seller_first_name else None, f"%{seller_first_name}%",
                seller_last_name if seller_last_name else None, f"%{seller_last_name}%"
            )
            
            cursor.execute(sql, query_values)
            results = cursor.fetchall()

            if not results:
                QMessageBox.information(self, "No Results", "No sellers found matching the criteria.")
                return

            if len(results) == 1:
                # Single result: store the seller_id and display seller information
                self.current_seller_id = results[0][0]
                self._display_seller_information(results[0])
                QMessageBox.information(self, "Seller Found", f"Selected Seller ID: {self.current_seller_id}")
            else:
                # Multiple results: prompt the user to select one
                selected_seller = self._prompt_user_for_selection(results)
                if selected_seller:
                    self.current_seller_id = selected_seller[0]
                    self._display_seller_information(selected_seller)
                    QMessageBox.information(self, "Seller Selected", f"Selected Seller ID: {self.current_seller_id}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while searching: {e}")
        finally:
            cursor.close()
            conn.close()

    def _update_seller_from_dropdown(self):
        """
        Handle seller selection from the dropdown and display seller details.
        """
        selected_seller = self.ui.cmbAllSellers.currentData()  # Get the seller_id from the dropdown selection

        if selected_seller:
            conn = make_connection(config_file="sqlproject.ini")
            cursor = conn.cursor()

            try:
                sql = """
                    SELECT seller_id, seller_first_name, seller_last_name, seller_email, seller_phone
                    FROM sellers
                    WHERE seller_id = %s
                """
                cursor.execute(sql, (selected_seller,))
                seller_details = cursor.fetchone()

                if seller_details:
                    self._display_seller_information(seller_details)
                else:
                    QMessageBox.information(self, "No Details", "No details found for the selected seller.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to fetch seller details: {e}")
            finally:
                cursor.close()
                conn.close()

    def _display_seller_information(self, seller_details):
        """
        Display the selected seller's details in the seller information section,
        including city and state selection from the geolocation data.
        :param seller_details: Tuple containing seller details from the database.
        """
        try:
            # Extract seller information from the tuple
            seller_id, first_name, last_name, email, phone = seller_details
            
            # Fetch city and state from geolocation table based on seller's zip code
            conn = make_connection(config_file="sqlproject.ini")
            cursor = conn.cursor()
    
            # Fetch the city and state based on the seller's zip code (seller_zip_code)
            cursor.execute("""
                SELECT DISTINCT city, state_name
                FROM geolocation
                WHERE geolocation_id = (
                    SELECT seller_zip_code FROM sellers WHERE seller_id = %s
                )
            """, (seller_id,))
            location = cursor.fetchone()

            # Set default city and state to "Unknown" if not found
            city = location[0] if location else "Unknown"
            state = location[1] if location else "Unknown"

            # Populate the text fields with seller details
            self.ui.seller_first_name_edit.setText(first_name)
            self.ui.seller_last_name_edit.setText(last_name)
            self.ui.seller_email_edit.setText(email)
            self.ui.seller_phone_edit.setText(phone)

            # Fetch all available cities and states from the geolocation table
            cursor.execute("SELECT DISTINCT city FROM geolocation ORDER BY city")
            cities = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT state_name FROM geolocation ORDER BY state_name")
            states = [row[0] for row in cursor.fetchall()]

            # Clear existing items in dropdowns
            self.ui.cmbStates.clear()
            self.ui.cmbCities.clear()

            # Add cities and states to their respective dropdowns
            self.ui.cmbStates.addItems(states)
            self.ui.cmbCities.addItems(cities)

            # Set the current city and state based on the fetched values
            self.ui.cmbStates.setCurrentText(state)  # Set the state to the fetched value
            self.ui.cmbCities.setCurrentText(city)  # Set the city to the fetched value

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display seller information: {e}")

    
    def _update_seller_dashboard(self):
        """
        Update the seller dashboard based on dropdown and text input filters.
        """
        selected_seller_down = self.ui.cmbAllSellers.currentData()
        selected_seller_text = self.ui.seller_id_search.text().strip()

        selected_seller = selected_seller_down if selected_seller_down else selected_seller_text

        conn = make_connection(config_file="sqlproject.ini")
        cursor = conn.cursor()

        try:
            sql = """
                SELECT p.product_id, p.product_category, p.product_description, p.product_price
                FROM products p
                JOIN product_stock ps ON ps.product_id = p.product_id
                JOIN sellers s ON ps.seller_id = s.seller_id
                WHERE s.seller_id = %s
            """
            cursor.execute(sql, (selected_seller,))
            products = cursor.fetchall()

            self.ui.tblProducts.setRowCount(0)
            if products:
                for row_index, row_data in enumerate(products):
                    self.ui.tblProducts.insertRow(row_index)
                    for col_index, col_data in enumerate(row_data):
                        self.ui.tblProducts.setItem(
                            row_index, col_index, QTableWidgetItem(str(col_data))
                        )
            else:
                self.ui.tblProducts.setRowCount(1)
                self.ui.tblProducts.setItem(
                    0, 0, QTableWidgetItem("No Products!")
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while fetching products: {e}"
            )
        finally:
            cursor.close()
            conn.close()
         
    # clear information
    def _clear_seller_info(self):
        """
        Clear the displayed seller information in the UI without triggering unnecessary pop-ups.
        """
        try:
            # Clear text fields
            self.ui.seller_first_name_edit.clear()
            self.ui.seller_last_name_edit.clear()
            self.ui.seller_email_edit.clear()
            self.ui.seller_phone_edit.clear()

            # Clear dropdown selections
            self.ui.cmbCities.setCurrentIndex(-1)  # Deselect the current city
            self.ui.cmbStates.setCurrentIndex(-1)  # Deselect the current state
            self.ui.cmbAllSellers.setCurrentIndex(-1) #Deselect current seller

            # Reset the display of the tblProducts table in the UI (this does not delete data)
            self.ui.tblProducts.clearContents()  # Clears the contents displayed in the table
            self.ui.tblProducts.setRowCount(0)  # Resets the row count to 0 (removes visible rows)

        except Exception as e:
            # Log the error without showing a pop-up
            print(f"Error during clear operation: {e}")

    # update seller
    def _update_seller_info(self):
        """
        Update the seller information in the database using the stored seller_id.
        """
        # Check if current_seller_id is set
        if not self.current_seller_id:
            QMessageBox.warning(self, "Update Error", "No seller selected for update. Please search for a seller first.")
            return

        # Extract data from UI input fields
        seller_first_name = self.ui.seller_first_name_edit.text().strip()
        seller_last_name = self.ui.seller_last_name_edit.text().strip()
        seller_email = self.ui.seller_email_edit.text().strip()
        seller_phone = self.ui.seller_phone_edit.text().strip()
        seller_state = self.ui.cmbStates.currentText().strip()  
        seller_city = self.ui.cmbCities.currentText().strip()  

        # Ensure that all required fields are filled
        if not (seller_first_name and seller_last_name and seller_email and seller_phone):
            QMessageBox.warning(self, "Input Error", "All fields must be filled!")
            return

        print(f"Updating Seller: {self.current_seller_id}")
        print(f"Seller Info: {seller_first_name}, {seller_last_name}, {seller_email}, {seller_phone}, {seller_city}, {seller_state}")

        conn = None
        cursor = None

        try:
            # Establish a connection to the database
            conn = make_connection(config_file="sqlproject.ini")
            cursor = conn.cursor()

            # Fetch ZIP code based on city and state
            geolocation_query = """
                SELECT geolocation_id
                FROM geolocation
                WHERE city = %s AND state_name = %s
            """
            cursor.execute(geolocation_query, (seller_city, seller_state,))
            geolocation_data = cursor.fetchone()

            if not geolocation_data:
                seller_zip_code = None
                QMessageBox.warning(self, "Geolocation Warning", "No matching ZIP Code found for the provided city and state. Setting ZIP code to NULL.")


            seller_zip_code = geolocation_data[0]
            print(f"Found ZIP Code: {seller_zip_code}")

            # Update seller information in the database
            update_sql = """
                UPDATE sellers
                SET seller_first_name = %s, seller_last_name = %s, seller_email = %s,
                    seller_phone = %s, seller_zip_code = %s
                WHERE seller_id = %s
            """
            cursor.execute(
                update_sql, (
                    seller_first_name, seller_last_name, seller_email, seller_phone,
                    seller_zip_code, self.current_seller_id
                )
            )
            conn.commit()

            QMessageBox.information(self, "Success", "Seller information updated successfully!")

            # Refresh UI elements
            self._populate_sellers_table()
            self._populate_sellers_dropdown()

        except Exception as e:
            print(f"Error occurred during update: {e}")  # Log the error to console for debugging
            QMessageBox.critical(self, "Error", f"Failed to update seller: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
  
    # Delete the selected seller from the database
    def _delete_seller(self):
        """
        Delete the selected seller from the database after confirming the action.
        If the seller has associated products or product stock, they will also be deleted.
        """
        seller_id = self.current_seller_id  # Retrieve the current seller ID to be deleted

        if not seller_id:
            # If no seller ID is found, prompt the user with an error message
            QMessageBox.warning(self, "Input Error", "Seller ID is required!")
            return

        # Ask for confirmation before deleting the seller
        confirmation = QMessageBox.question(
            self, "Delete Seller", f"Are you sure you want to delete seller ID {seller_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.No:
            # If the user clicks "No", cancel the deletion process
            return

        conn = make_connection(config_file="sqlproject.ini")
        cursor = conn.cursor()

        try:
            # Check if the seller has any associated products and delete them if so
            cursor.execute("SELECT COUNT(*) FROM products p JOIN product_stock ps ON ps.product_id = p.product_id WHERE seller_id = %s", (seller_id,))
            product_count = cursor.fetchone()[0]
            if product_count > 0:
                # Delete associated products and product stock
                cursor.execute("DELETE FROM products p JOIN product_stock ps ON ps.product_id = p.product_id WHERE seller_id = %s", (seller_id,))

            # Check if the seller has product stock records and delete them if necessary
            cursor.execute("SELECT COUNT(*) FROM product_stock WHERE seller_id = %s", (seller_id,))
            product_stock_count = cursor.fetchone()[0]
            if product_stock_count > 0:
                cursor.execute("DELETE FROM product_stock WHERE seller_id = %s", (seller_id,))

            # Finally, delete the seller record from the sellers table
            cursor.execute("DELETE FROM sellers WHERE seller_id = %s", (seller_id,))
            conn.commit()  # Commit the changes to the database

            # Show a success message and refresh the UI to reflect the deletion
            QMessageBox.information(self, "Success", "Seller deleted successfully!")
            self._clear_seller_info()  # Clear any displayed seller info
            self._populate_sellers_table()  # Refresh the sellers table
            self._populate_sellers_dropdown()  # Refresh the sellers dropdown

        except Exception as e:
            # If an error occurs during the deletion process, log the error and show a failure message
            print(f"Error during deletion: {e}")  # Log error for debugging
            QMessageBox.critical(self, "Error", "Failed to delete seller.")
        finally:
            # Ensure the cursor and database connection are closed after the operation
            cursor.close()
            conn.close()

    # Create a new seller
    def _create_seller_info(self):
        """
        Create a new seller in the database by collecting information from the UI.
        """
        # Get the seller details entered in the UI and strip any extra spaces
        seller_first_name = self.ui.seller_first_name_edit.text().strip()
        seller_last_name = self.ui.seller_last_name_edit.text().strip()
        seller_email = self.ui.seller_email_edit.text().strip()
        seller_phone = self.ui.seller_phone_edit.text().strip()
        seller_city = self.ui.cmbCities.currentText().strip()
        seller_state = self.ui.cmbStates.currentText().strip()

        # Check if required fields are empty and prompt the user to fill them
        if not (seller_first_name and seller_last_name and seller_email and seller_phone):
            QMessageBox.warning(self, "Input Error", "All fields must be filled!")
            return

        # Check if city and state are selected
        if not (seller_city and seller_state):
            QMessageBox.warning(self, "Input Error", "City and State must be selected!")
            return

        # Create a database connection and cursor to execute SQL queries
        conn = make_connection(config_file="sqlproject.ini")
        cursor = conn.cursor()

        try:
            # Fetch the geolocation_id based on the city and state selected
            cursor.execute(
                "SELECT geolocation_id FROM geolocation WHERE city = %s AND state_name = %s LIMIT 1",
                (seller_city, seller_state)
            )
            geolocation_result = cursor.fetchone()

            # If no matching geolocation found, show an error message
            if not geolocation_result:
                QMessageBox.warning(
                    self, "Geolocation Error", 
                    f"No matching geolocation found for City: {seller_city}, State: {seller_state}!"
                )
                return

            seller_zip_code = geolocation_result[0]  # Retrieve geolocation_id (zip code)

            # Generate a new seller ID
            new_seller_id = self._generate_new_seller_id(cursor)

            # SQL query to insert a new seller into the database
            sql = """
                INSERT INTO sellers (seller_id, seller_first_name, seller_last_name, 
                                    seller_email, seller_phone, seller_zip_code)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            # Execute the insert query with the gathered seller information
            cursor.execute(
                sql, (
                    new_seller_id, seller_first_name, seller_last_name,
                    seller_email, seller_phone, seller_zip_code
                )
            )
            conn.commit()  # Commit the changes to the database

            # Show a success message after the seller is created
            QMessageBox.information(self, "Success", f"Seller {new_seller_id} created successfully!")

            # Clear the seller form and update the sellers table and dropdown list
            self._clear_seller_info()
            self._populate_sellers_table()
            self._populate_sellers_dropdown()

        except Exception as e:
            # Log and display any errors that occur during the seller creation process
            print(f"Error during creation: {e}")  # Log error for debugging
            QMessageBox.critical(self, "Error", "Failed to create seller.")
        finally:
            # Close the cursor and the database connection after the operation
            cursor.close()
            conn.close()


    
    def _generate_new_seller_id(self, cursor):
        """
        Generate the next available seller_id.
        """
        cursor.execute("SELECT seller_id FROM sellers WHERE seller_id REGEXP '^S[0-9]+'")
        all_ids = [int(row[0][1:]) for row in cursor.fetchall()]
        all_ids.sort()

        for i in range(1001, 9999):  # Assuming max seller_id is S9999
            if i not in all_ids:
                return f"S{i}"
        raise ValueError("No available seller ID!")
    

    def _handle_navigation(self, subpage_name):
        """
        Handle navigation between subpages, prompting for unsaved changes if necessary.
        """
        if self.unsaved_changes:
            user_response = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"You have unsaved changes in the current page. Do you want to save them before navigating to {subpage_name}?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            )
            if user_response == QMessageBox.Yes:
                self._update_seller_info()
            elif user_response == QMessageBox.Cancel:
                return  # Cancel navigation

        # Proceed to navigate to the specified subpage
        self.ui.mainStackedWidget.setCurrentWidget(getattr(self.ui, subpage_name))


    # ------------------------ #
    # dashboard "Sales & Customer Insight"
    # ------------------------ #
    def _setup_event_connections(self):
        """
        Setup dropdowns and buttons
        """
        self.ui.cmbAllMonth.currentIndexChanged.connect(self.setRevenue_trend_yearandmonth)
        self.ui.cmbAllCategory.currentIndexChanged.connect(self.setRevenue_trend_yearandmonth)
        self.ui.cmbAllStatus.currentIndexChanged.connect(self.setRevenue_trend_yearandmonth)
        self.ui.btnRefresh.clicked.connect(self.setRevenue_trend_yearandmonth)
        
        self.ui.cmbAllMonth.currentIndexChanged.connect(self.setCustomer_Satisfaction)
        self.ui.cmbAllCategory.currentIndexChanged.connect(self.setCustomer_Satisfaction)
        self.ui.cmbAllStatus.currentIndexChanged.connect(self.setCustomer_Satisfaction)
        self.ui.btnRefresh.clicked.connect(self.setCustomer_Satisfaction)
        
        self.ui.cmbAllMonth.currentIndexChanged.connect(self.setOrder_Status_proportion)
        self.ui.cmbAllCategory.currentIndexChanged.connect(self.setOrder_Status_proportion)
        self.ui.cmbAllStatus.currentIndexChanged.connect(self.setOrder_Status_proportion)
        self.ui.btnRefresh.clicked.connect(self.setOrder_Status_proportion)
        
        self.ui.cmbAllMonth.currentIndexChanged.connect(self.setPayment_Value_Over_Time)
        self.ui.cmbAllCategory.currentIndexChanged.connect(self.setPayment_Value_Over_Time)
        self.ui.cmbAllStatus.currentIndexChanged.connect(self.setPayment_Value_Over_Time)
        self.ui.btnRefresh.clicked.connect(self.setPayment_Value_Over_Time)
   
    # initial dropdowns
    def _initialize_dropdowns(self):
        """
        Setup the dashboard page, including sellers dropdown, states, cities, and products.
        """
        self.ui.cmbAllMonth.currentIndexChanged.connect(self._update_seller_dashboard)
        self.ui.cmbAllCategory.currentIndexChanged.connect(self._update_seller_dashboard)
        self.ui.cmbAllStatus.currentIndexChanged.connect(self._update_seller_dashboard)

        # Populate dropdowns with initial data
        self._populate_month()
        self._populate_category()
        self._populate_status()

    # reset charts and dropdowns to default    
    def _setup_refresh_button(self):
        self.ui.btnRefresh.clicked.connect(self._reset_to_default_state)

    def _reset_to_default_state(self):
        self.ui.cmbAllMonth.setCurrentIndex(0)
        self.ui.cmbAllCategory.setCurrentIndex(0)
        self.ui.cmbAllStatus.setCurrentIndex(0)

        # call the original chart function 
        self.showDashboard() 


    # month dropdown        
    def _populate_month(self):
        """
        Populate the 'All Month' dropdown with the month names.
        """
        conn = make_connection(config_file="sqlproject_wh.ini")
        cursor = conn.cursor()

        try:
            # Fetch months for dropdown population
            sql = """
                SELECT DISTINCT month
                FROM Dim_Time
                ORDER BY month
            """
            cursor.execute(sql)
            rows = cursor.fetchall()

            # Clear previous dropdown entries
            self.ui.cmbAllMonth.clear()
            self.ui.cmbAllMonth.addItem("Select Month", userData=None)

            for row in rows:
                month_num = row[0]
                month_name = self._get_month_name(month_num)
                self.ui.cmbAllMonth.addItem(month_name, userData=month_num)

            if self.ui.cmbAllMonth.count() > 0:
                self.ui.cmbAllMonth.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while populating month dropdown: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def _get_month_name(self, month_num):
        """Convert month number to month name."""
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return months[month_num - 1]
    
    # category dropdown
    def _populate_category(self):
        """
        Populate the 'Category' dropdown with product categories.
        """
        conn = make_connection(config_file="sqlproject_wh.ini")
        cursor = conn.cursor()

        try:
            # Fetch product categories for dropdown population
            sql = """
                SELECT DISTINCT product_category
                FROM Dim_Products
                ORDER BY product_category
            """
            cursor.execute(sql)
            rows = cursor.fetchall()

            # Clear previous dropdown entries
            self.ui.cmbAllCategory.clear()
            self.ui.cmbAllCategory.addItem("Select Category", userData=None)

            for row in rows:
                category = row[0]
                self.ui.cmbAllCategory.addItem(category, userData=category)

            if self.ui.cmbAllCategory.count() > 0:
                self.ui.cmbAllCategory.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while populating category dropdown: {e}")
        finally:
            cursor.close()
            conn.close()
    
    # status dropdown
    def _populate_status(self):
        """
        Populate the 'Status' dropdown with order statuses.
        """
        conn = make_connection(config_file="sqlproject.ini")
        cursor = conn.cursor()

        try:
            # Fetch order statuses for dropdown population
            sql = """
                SELECT DISTINCT order_status
                FROM orders
                ORDER BY order_status
            """
            cursor.execute(sql)
            rows = cursor.fetchall()

            # Clear previous dropdown entries
            self.ui.cmbAllStatus.clear()
            self.ui.cmbAllStatus.addItem("Select Status", userData=None)

            for row in rows:
                status = row[0]
                self.ui.cmbAllStatus.addItem(status, userData=status)

            if self.ui.cmbAllStatus.count() > 0:
                self.ui.cmbAllStatus.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while populating status dropdown: {e}")
        finally:
            cursor.close()
            conn.close()


    def _selected_dropdown(self):
        """
        Generate SQL WHERE conditions based on the options selected from the dropdown menu.
        """
        conditions = []
        selected_month = self.ui.cmbAllMonth.currentData()
        selected_category = self.ui.cmbAllCategory.currentText()
        selected_status = self.ui.cmbAllStatus.currentText()

        if selected_month:
            conditions.append(f"MONTH(orders.order_purchase_timestamp) = {selected_month}")
        if selected_category and selected_category != "Select Category":
            conditions.append(f"products.product_category = '{selected_category}'")
        if selected_status and selected_status != "Select Status":
            conditions.append(f"orders.order_status = '{selected_status}'")

        return " AND ".join(conditions) if conditions else ""

    # show all the dashboards
    def showDashboard(self):
        """
        Function to set up and display the dashboard page.
        """
        # Set up other dashboard UI elements (if applicable)
        
        # Automatically display the Revenue chart
        self.setRevenue_trend_yearandmonth()
        self.setCustomer_Satisfaction()
        self.setPayment_Value_Over_Time()
        self.setOrder_Status_proportion() 

    # plot 0,0
    def setRevenue_trend_yearandmonth(self):
        """
        Generate and display Monthly Revenue Trends in the Revenue_trend_yearandmonth layout.
        Updates dynamically based on dropdown selections or defaults to full data.
        """
        try:
            conn = make_connection(config_file="sqlproject.ini")
            cursor = conn.cursor()
            
            # Generate conditions based on selected options.
            conditions = self._selected_dropdown()
            if conditions:
                query = f"""
                    SELECT DATE_FORMAT(order_purchase_timestamp, '%Y-%m') AS year_and_month, 
                        SUM(payment_value) AS total_revenue
                    FROM orders
                    JOIN order_payments ON orders.order_id = order_payments.order_id
                    JOIN order_items ON orders.order_id = order_items.order_id
                    JOIN products ON products.product_id = order_items.product_id
                    WHERE {conditions}
                    GROUP BY DATE_FORMAT(order_purchase_timestamp, '%Y-%m')
                    ORDER BY year_and_month;
                """
            else:
                # Default to displaying complete data.
                query = """
                    SELECT DATE_FORMAT(order_purchase_timestamp, '%Y-%m') AS year_and_month, 
                        SUM(payment_value) AS total_revenue
                    FROM orders
                    JOIN order_payments ON orders.order_id = order_payments.order_id
                    GROUP BY DATE_FORMAT(order_purchase_timestamp, '%Y-%m')
                    ORDER BY year_and_month;
                """
            
            cursor.execute(query)
            revenue_data = cursor.fetchall()
            cursor.close()
            conn.close()

            # draw plot
            if revenue_data:
                year_and_month = [row[0] for row in revenue_data]
                total_revenue = [row[1] for row in revenue_data]

                fig, ax = plt.subplots(figsize=(5, 3))
                ax.plot(year_and_month, total_revenue, marker='o', color='skyblue', label='Revenue')
                ax.set_xlabel('Year and Month', fontsize=10, fontname='serif', color='#6f7782')
                ax.set_ylabel('Total Revenue', fontsize=10, fontname='serif', color='#6f7782')
                ax.set_title('Monthly Revenue Trends', color='#37383b', fontsize=12, fontweight='bold',fontname='serif')
                
                ax.set_facecolor('#ebebeb')
                ax.grid(True, which='both', axis='y', linestyle='--', color='#6f7782', zorder=1) 
                ax.tick_params(axis='x', labelrotation=45, labelsize=8)
                ax.tick_params(axis='y', labelsize=8)
                ax.legend(fontsize=8)
                fig.tight_layout()

                canvas = FigureCanvas(fig)
                # clean up old plot
                while self.ui.Revenue_trend_yearandmonth.count():
                    item = self.ui.Revenue_trend_yearandmonth.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                # add new canvas
                self.ui.Revenue_trend_yearandmonth.addWidget(canvas)
                plt.close(fig)
            else:
                # dealing with no data condition
                while self.ui.Revenue_trend_yearandmonth.count():
                    item = self.ui.Revenue_trend_yearandmonth.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                noData = QtWidgets.QLabel("No Data")
                noData.setStyleSheet("color: white; background-color: DodgerBlue;")
                noData.setAlignment(QtCore.Qt.AlignCenter)
                self.ui.Revenue_trend_yearandmonth.addWidget(noData)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display Revenue Trends: {e}")
  
    # plot 0,1  
    def setCustomer_Satisfaction(self):
        """
        Generate a bar chart of review scores by product categories and embed it into the UI.
        Updates dynamically based on dropdown selections or defaults to full data.
        """
        try:
            conn = make_connection(config_file="sqlproject.ini")
            cursor = conn.cursor()
            
            # Generate conditions based on selected options
            conditions = self._selected_dropdown()
            if conditions:
                query = f"""
                    SELECT products.product_category, AVG(order_reviews.review_score) AS avg_review_score
                    FROM products
                    JOIN order_items ON products.product_id = order_items.product_id
                    JOIN orders ON order_items.order_id = orders.order_id
                    JOIN order_reviews ON orders.order_id = order_reviews.order_id
                    WHERE {conditions}
                    GROUP BY products.product_category;
                """
            else:
                # Default to displaying complete data
                query = """
                    SELECT products.product_category, AVG(order_reviews.review_score) AS avg_review_score
                    FROM products
                    JOIN order_items ON products.product_id = order_items.product_id
                    JOIN orders ON order_items.order_id = orders.order_id
                    JOIN order_reviews ON orders.order_id = order_reviews.order_id
                    GROUP BY products.product_category;
                """

            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            
            
            if result:
                # Prepare data for plotting
                categories = [row[0] for row in result]  # Product categories
                avg_review_scores = [row[1] for row in result]  # Average review scores

                # Create a new figure and axis
                fig, ax = plt.subplots(figsize=(5, 3))
                bar_colors = sns.color_palette("pastel", len(categories))
                ax.bar(categories, avg_review_scores, color=bar_colors)

                # Customize chart
                ax.set_title("Customer Satisfaction by Product Categories", color='#37383b', fontsize=12, fontweight='bold',fontname='serif')
                ax.set_xlabel("Product Category", fontname='serif', color='#6f7782')
                ax.set_ylabel("Average Review Score", fontname='serif', color='#6f7782')
                ax.tick_params(axis='x', labelrotation=45, labelsize=8)
                ax.tick_params(axis='y', labelsize=8)

                ax.set_facecolor('#ebebeb')
                ax.grid(True, which='both', axis='y', linestyle='--', color='#6f7782', zorder=1) 
                ax.tick_params(axis='x', labelsize=8)  # x ticks
                ax.tick_params(axis='y', labelsize=8, left = False)

                fig.tight_layout(rect=[0, 0, 0.95, 1]) 
                
                canvas = FigureCanvas(fig)
                
                # clean up old plot
                while self.ui.Customer_Satisfaction.count():
                    item = self.ui.Customer_Satisfaction.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                # add new canvas
                self.ui.Customer_Satisfaction.addWidget(canvas)
                plt.close(fig)
            else:
                # dealing with no data condition
                while self.ui.Revenue_trend_yearandmonth.count():
                    item = self.ui.Revenue_trend_yearandmonth.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                noData = QtWidgets.QLabel("No Data")
                noData.setStyleSheet("color: white; background-color: DodgerBlue;")
                noData.setAlignment(QtCore.Qt.AlignCenter)
                self.ui.Revenue_trend_yearandmonth.addWidget(noData)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display Revenue Trends: {e}")

    # plot 1,0 
    def setPayment_Value_Over_Time(self):
        """
        Generate a stacked bar chart of total payment value by payment type over time and embed it into the UI.
        """
        try:            
            conn = make_connection(config_file="sqlproject_wh.ini")
            
            conditions = self._selected_dropdown()
            if conditions:
                conn_db2 = make_connection(config_file="sqlproject.ini")
                cursor_db2 = conn_db2.cursor()
                q2 = f"""
                    SELECT products.product_id as product_id, orders.order_id as order_id, Month(orders.order_purchase_timestamp) as month
                    FROM products
                    JOIN order_items ON products.product_id = order_items.product_id
                    JOIN orders ON orders.order_id = order_items.order_id
                    WHERE {conditions}
                """
                cursor_db2.execute(q2)
                # Fetch the result of the second query to use in the main query
                result_db2 = cursor_db2.fetchall()

                # Extract the product_ids and order_ids from the result
                product_ids = [row[0] for row in result_db2]
                order_ids = [row[1] for row in result_db2]
                months = [row[2] for row in result_db2]  # month values for filtering

                # Close the second database connection
                cursor_db2.close()
                conn_db2.close()
                
                conditions_combined = []
            
                if product_ids:
                    # Add product_id condition if product_ids exists
                    product_condition = f"Dim_Products.product_id IN ({','.join([f"'{pid}'" for pid in product_ids])})"
                    conditions_combined.append(product_condition)
                
                if order_ids:
                    # Add order_id condition if order_ids exists
                    order_condition = f"Fact_Payments.order_id IN ({','.join(map(str, order_ids))})"
                    conditions_combined.append(order_condition)
                
                if months:
                    # Add month condition if months exists
                    month_condition = f"Dim_Time.month IN ({','.join(map(str, months))})"
                    conditions_combined.append(month_condition)

                # Combine conditions dynamically with AND
                if conditions_combined:
                    conditions_combined = " AND ".join(conditions_combined)
                    conditions_combined = f"({conditions_combined})"

                if conditions_combined:
                    # Main query with dynamic WHERE clause
                    query = f"""
                        SELECT Dim_Time.year, Dim_Time.month, Fact_Payments.payment_type, SUM(Fact_Payments.payment_value) AS total_payment_value
                        FROM Fact_Payments
                        JOIN Dim_Time ON Fact_Payments.time_id = Dim_Time.time_id
                        JOIN Dim_Products ON Dim_Products.product_id = Fact_Payments.product_id
                        WHERE {conditions_combined}
                        GROUP BY Dim_Time.year, Dim_Time.month, Fact_Payments.payment_type
                        ORDER BY Dim_Time.year, Dim_Time.month, total_payment_value DESC;
                    """
                    df = pd.read_sql(query, conn)
                    # Pivot data for stacked bar chart
                    df_pivot = df.pivot(index=['year', 'month'], columns='payment_type', values='total_payment_value').fillna(0)

                    # Plot the stacked bar chart
                    fig, ax = plt.subplots(figsize=(5, 3.5))
                    df_pivot.plot(kind='bar', stacked=True, ax=ax, colormap='Set2')

                    # Customize chart
                    ax.set_title("Payment Value by Payment Type Over Time", color='#37383b', fontsize=10, fontweight='bold')
                    ax.set_xlabel("Year and Month", fontname='serif', color='#6f7782')
                    ax.set_ylabel("Total Payment Value", fontname='serif', color='#6f7782')
                    
                    ax.set_facecolor('#ebebeb')
                    ax.grid(True, which='both', axis='y', linestyle='--', color='#6f7782', zorder=1) 
                    ax.tick_params(axis='x', labelrotation=45, labelsize=6)  # x ticks
                    ax.tick_params(axis='y', labelsize=6, left = False)
                    ax.legend(title="Payment Type", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)
                    fig.tight_layout(rect=[0, 0, 0.95, 1]) 

                    # Embed the plot into the UI layout
                    self._embed_plot(self.ui.Payment_Value_Over_Time, fig)
                else:
                    # Handle No Data Condition
                    while self.ui.Payment_Value_Over_Time.count():
                        item = self.ui.Payment_Value_Over_Time.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                    noData = QtWidgets.QLabel("No Data")
                    noData.setStyleSheet("color: white; background-color: DodgerBlue;")
                    noData.setAlignment(QtCore.Qt.AlignCenter)
                    self.ui.Payment_Value_Over_Time.addWidget(noData)
            else:
                query = """
                    SELECT d_t.year, d_t.month, f.payment_type, SUM(f.payment_value) AS total_payment_value
                    FROM Fact_Payments f
                    JOIN Dim_Time d_t ON f.time_id = d_t.time_id
                    GROUP BY d_t.year, d_t.month, f.payment_type
                    ORDER BY d_t.year, d_t.month, total_payment_value DESC;
                """
                df = pd.read_sql(query, conn)
                # Pivot data for stacked bar chart
                df_pivot = df.pivot(index=['year', 'month'], columns='payment_type', values='total_payment_value').fillna(0)

                # Plot the stacked bar chart
                fig, ax = plt.subplots(figsize=(5, 3.5))
                df_pivot.plot(kind='bar', stacked=True, ax=ax, colormap='Set2')

                # Customize chart
                ax.set_title("Payment Value by Payment Type Over Time", color='#37383b', fontsize=10, fontweight='bold', fontname='serif')
                ax.set_xlabel("Year and Month", fontname='serif', color='#6f7782')
                ax.set_ylabel("Total Payment Value", fontname='serif', color='#6f7782')

                ax.set_facecolor('#ebebeb')
                ax.grid(True, which='both', axis='y', linestyle='--', color='#6f7782', zorder=1) 
                ax.tick_params(axis='x', labelrotation=45, labelsize=6) 
                ax.tick_params(axis='y', labelsize=6, left = False)
                ax.legend(title="Payment Type", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)
                fig.tight_layout(rect=[0, 0, 0.95, 0.95]) 

                # Embed the plot into the UI layout
                self._embed_plot(self.ui.Payment_Value_Over_Time, fig)
        finally:
            conn.close()

    # plot 1,1  
    def setOrder_Status_proportion(self):
        """
        Generate a pie chart for order status proportions and embed it into the UI.
        """
        try:
            conn = make_connection(config_file="sqlproject.ini")
            cursor = conn.cursor()
            
            conditions = self._selected_dropdown()
            if conditions:
                query = f"""
                    SELECT orders.order_status, COUNT(*) AS status_count
                    FROM orders
                    JOIN order_items ON order_items.order_id = orders.order_id
                    JOIN products ON products.product_id = order_items.product_id
                    WHERE {conditions}
                    GROUP BY orders.order_status;
                """
            else:
                query = """
                    SELECT order_status, COUNT(*) AS status_count
                    FROM orders
                    GROUP BY order_status;
                """
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if result:
                order_status = [row[0] for row in result]
                status_count = [row[1] for row in result]

                total = sum(status_count)

                labels_with_percentages = [f"{status} ({count / total:.1%})" for status, count in zip(order_status, status_count)]

                fig, ax = plt.subplots(figsize=(5, 3))
                wedges, _ = ax.pie(
                    status_count, 
                    labels=None, 
                    autopct=None, 
                    startangle=90, 
                    colors=sns.color_palette("pastel"),
                    textprops={'fontsize': 8}
                )

                ax.legend(
                    wedges, 
                    labels_with_percentages, 
                    title="Order Status", 
                    loc="center left", 
                    bbox_to_anchor=(1, 0, 0.5, 1), 
                    fontsize=8
                )

                ax.axis('equal')
                ax.set_title("Order Status Proportions", color='#37383b', fontsize=12, fontweight='bold', fontname='serif')
                plt.tight_layout()
                canvas = FigureCanvas(fig)
                
                while self.ui.Order_Status_proportion.count():
                    item = self.ui.Order_Status_proportion.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                self.ui.Order_Status_proportion.addWidget(canvas)
                plt.close(fig)
            else:
                # dealing with no data condition
                while self.ui.Order_Status_proportion.count():
                    item = self.ui.Order_Status_proportion.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                noData = QtWidgets.QLabel("No Data")
                noData.setStyleSheet("color: white; background-color: DodgerBlue;")
                noData.setAlignment(QtCore.Qt.AlignCenter)
                self.ui.Order_Status_proportion.addWidget(noData)            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate Order Status pie chart: {e}")

    

    # ------------------------ #
    # dashboard "Product & Operations Analysis"
    # ------------------------ #
    # show top labels
    def showLabels(self):
        try:
            conn = make_connection(config_file="sqlproject.ini")
            
            total_sales_query = """SELECT SUM(payment_value) AS total_sales FROM order_payments"""
            total_orders_query = """SELECT COUNT(*) AS total_orders FROM orders"""
            avg_rating_query = """SELECT AVG(review_score) AS avg_rating FROM order_reviews"""
            top_seller_query = """
                SELECT CONCAT(s.seller_id, ' - ', s.seller_last_name, ' ', s.seller_first_name) AS top_seller
                FROM sellers s
                JOIN order_items oi ON oi.seller_id = s.seller_id
                JOIN orders o ON o.order_id = oi.order_id
                JOIN order_payments op ON op.order_id = o.order_id
                GROUP BY s.seller_id
                ORDER BY SUM(op.payment_value) DESC 
                LIMIT 1; 
            """

            total_sales_df = pd.read_sql(total_sales_query, conn)
            total_orders_df = pd.read_sql(total_orders_query, conn)
            avg_rating_df = pd.read_sql(avg_rating_query, conn)
            top_seller_df = pd.read_sql(top_seller_query, conn)
            
            if total_sales_df.empty or total_orders_df.empty or avg_rating_df.empty or top_seller_df.empty:
                QMessageBox.warning(self, "No Data", "No data available for the labels.")
                return

            total_sales = total_sales_df.iloc[0]['total_sales']
            total_orders = total_orders_df.iloc[0]['total_orders']
            avg_rating = avg_rating_df.iloc[0]['avg_rating']
            top_seller = top_seller_df.iloc[0]['top_seller']
        finally:
            conn.close()
            
        self.ui.Sales.setText(f"${total_sales: .2f}")
        self.ui.Orders.setText(f"{total_orders} orders")
        self.ui.AvgRating.setText(f"{avg_rating} / 5")
        self.ui.TopSeller.setText(f"{top_seller}")
   
    # show dashboard
    def showDashboard2(self):
        """
        Function to set up and display the dashboard page.
        """
        self.setPayment_Method_preferences()       
        self.setRevenue_by_product_categories()
        self.setProduct_Sales_Over_Time()
        self.setDelivery_Performance()
        
    # plot 0,0     
    def setPayment_Method_preferences(self):
        """
        Generate a pie chart for payment method preferences and embed it into the UI.
        """
        try:
            conn = make_connection(config_file="sqlproject.ini")
            query = """
            SELECT payment_type, COUNT(*) AS count
            FROM order_payments
            GROUP BY payment_type;
            """
            df = pd.read_sql(query, conn)
            # Plot
            fig, ax = plt.subplots(figsize=(3, 3))
            ax.pie(
                df['count'],
                labels=df['payment_type'],
                autopct='%1.1f%%',
                startangle=90,
                colors=sns.color_palette("muted")
            )
            ax.axis('equal')  # Ensure circular pie chart
            ax.set_title("Payment Method Preferences", color='#37383b', fontsize=12, fontweight='bold',fontname='serif')
            self._embed_plot(self.ui.Payment_Method_preferences, fig)
            
            if df.empty:
                # dealing with no data condition
                while self.ui.Payment_Method_preferences.count():
                    item = self.ui.Payment_Method_preferences.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                noData = QtWidgets.QLabel("No Data")
                noData.setStyleSheet("color: white; background-color: DodgerBlue;")
                noData.setAlignment(QtCore.Qt.AlignCenter)
                self.ui.Payment_Method_preferences.addWidget(noData)   
        finally:
            conn.close()
    
    # plot 0,1wh
    def setProduct_Sales_Over_Time(self):
        """
        Generate a stacked bar chart of product sales (quantity and freight value) by product category over time and embed it into the UI.
        """
        try:
            conn = make_connection(config_file="sqlproject_wh.ini")
            query = """
            SELECT 
                d_t.year,  
                d_t.month,  
                d_p.product_category, 
                SUM(f.quantity) AS total_quantity,     
                SUM(f.freight_value) AS total_freight_value
            FROM Fact_Orders f
            JOIN Dim_Products d_p ON f.product_id = d_p.product_id
            JOIN Dim_Time d_t ON f.time_id = d_t.time_id
            GROUP BY d_t.year, d_t.month, d_p.product_category
            ORDER BY d_t.year, d_t.month, d_p.product_category;
            """
            df = pd.read_sql(query, conn)
            # Pivot data for stacked bar chart
            df_pivot = df.pivot(index=['year', 'month'], columns='product_category', values='total_quantity').fillna(0)

            fig, ax = plt.subplots(figsize=(7, 3))  
            df_pivot.plot(kind='bar', stacked=True, ax=ax, colormap='Set3')

            ax.set_title("Product Category Sales by Year and Month", color='#37383b', fontsize=12, fontweight='bold', fontname='serif')
            ax.set_xlabel("Year and Month", fontsize=10, fontname='serif', color='#6f7782')
            ax.set_ylabel("Total Quantity", fontsize=10, fontname='serif', color='#6f7782')
            ax.set_facecolor('#ebebeb')
            ax.grid(True, which='both', axis='y', linestyle='--', color='#6f7782', zorder=1) 
            ax.tick_params(axis='x', labelrotation=45, labelsize=6)  
            ax.tick_params(axis='y', labelsize=6, left = False)

            ax.legend(title="Product Categories", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)

            fig.tight_layout(rect=[0, 0, 0.95, 1]) 


            # Embed the plot into the UI layout
            self._embed_plot(self.ui.Product_Sales_Over_Time, fig)
            
            if df.empty:
                # dealing with no data condition
                while self.ui.Product_Sales_Over_Time.count():
                    item = self.ui.Product_Sales_Over_Time.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                noData = QtWidgets.QLabel("No Data")
                noData.setStyleSheet("color: white; background-color: DodgerBlue;")
                noData.setAlignment(QtCore.Qt.AlignCenter)
                self.ui.Product_Sales_Over_Time.addWidget(noData)  
        finally:
            conn.close()
   
    # plot 1,0 
    def setRevenue_by_product_categories(self):
        """
        Generate and display Revenue by Product Categories in the Revenue_by_product_categories layout.
        """
        try:
            conn = make_connection(config_file="sqlproject.ini")
            cursor = conn.cursor()

            # SQL Query to fetch revenue by product categories
            query = """
            SELECT p.product_category, SUM(op.payment_value) AS total_revenue
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN orders o ON oi.order_id = o.order_id
            JOIN order_payments op ON o.order_id = op.order_id
            GROUP BY p.product_category;
            """
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            conn.close()

            # Plot the data if available
            if data:
                categories = [row[0] for row in data]
                revenues = [row[1] for row in data]

                # Create the bar chart
                fig, ax = plt.subplots(figsize=(3, 3))
                bar_colors = sns.color_palette("pastel", len(categories))
                ax.bar(categories, revenues, color=bar_colors)
                ax.set_xlabel('Product Category', fontsize=10, fontname='serif', color='#6f7782')
                ax.set_ylabel('Total Revenue', fontsize=10, fontname='serif', color='#6f7782')
                ax.set_title('Revenue by Product Categories', color='#37383b', fontsize=12, fontweight='bold', fontname='serif')

                ax.set_facecolor('#ebebeb')
                ax.grid(True, which='both', axis='y', linestyle='--', color='#6f7782', zorder=1) 
                ax.tick_params(axis='x', labelrotation=45, labelsize=6)  
                ax.tick_params(axis='y', labelsize=8, left = False)
                fig.tight_layout() 

                # Embed the plot into Revenue_by_product_categories layout
                canvas = FigureCanvas(fig)

                # Clear existing widgets in the layout
                while self.ui.Revenue_by_product_categories.count():
                    item = self.ui.Revenue_by_product_categories.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                # Add the new canvas to the layout
                self.ui.Revenue_by_product_categories.addWidget(canvas)
                plt.close(fig)  # Close the figure after embedding it
            else:
                # No data to display
                while self.ui.Revenue_by_product_categories.count():
                    item = self.ui.Revenue_by_product_categories.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                noData = QtWidgets.QLabel("No Data")
                noData.setStyleSheet("color: white; background-color: DodgerBlue;")
                noData.setAlignment(QtCore.Qt.AlignCenter)
                self.ui.Revenue_by_product_categories.addWidget(noData)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display Revenue by Product Categories: {e}")
 
    # plot 1,1
    def setDelivery_Performance(self):
        """
        Generate a bar chart comparing estimated vs. actual delivery times.
        """
        try:
            conn = make_connection(config_file="sqlproject.ini")
            query = """
            SELECT 
                DATEDIFF(order_delivered_customer_date, order_estimated_delivery_date) AS delivery_delay,
                COUNT(*) AS count
            FROM orders
            WHERE order_delivered_customer_date IS NOT NULL
            GROUP BY delivery_delay;
            """
            df = pd.read_sql(query, conn)
            # Plot
            fig, ax = plt.subplots(figsize=(5, 3))
            sns.barplot(x=df['delivery_delay'], y=df['count'], ax=ax, palette="viridis")
            ax.set_title("Delivery Performance (Estimated vs. Actual)", color='#37383b', fontsize=12, fontweight='bold', fontname='serif')
            ax.set_xlabel("Delivery Delay (Days)",fontsize=9, fontname='serif', color='#6f7782')
            ax.set_ylabel("Count", fontsize=9, color='#6f7782', fontname='serif')
            ax.set_facecolor('#ebebeb')
            ax.grid(True, which='both', axis='y', linestyle='--', color='#6f7782', zorder=1) 
            ax.tick_params(axis='x', labelsize=5)  # x ticks
            ax.tick_params(axis='y', labelsize=5, left = False)
            fig.tight_layout(rect=[0, 0, 0.95, 1]) 
            self._embed_plot(self.ui.Delivery_Performance, fig)
            
            if df.empty:
                # No data to display
                while self.ui.Delivery_Performance.count():
                    item = self.ui.Delivery_Performance.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                noData = QtWidgets.QLabel("No Data")
                noData.setStyleSheet("color: white; background-color: DodgerBlue;")
                noData.setAlignment(QtCore.Qt.AlignCenter)
                self.ui.Delivery_Performance.addWidget(noData)
        finally:
            conn.close()
   
   
   
   # embeded plot    
    def _embed_plot(self, layout, fig):
        """
        Embed a Matplotlib figure into a PyQt layout.
        :param layout: The layout to embed the plot into.
        :param fig: The Matplotlib figure to embed.
        """
        canvas = FigureCanvas(fig)
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        layout.addWidget(canvas)
        plt.close(fig)

    def _embed_no_data(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        noData = QtWidgets.QLabel("No Data")
        noData.setStyleSheet("color: white; background-color: DodgerBlue;")
        noData.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(noData)


    def show_dialog(self):
        """
        Show this dialog.
        """
        self.ui.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = ManagerPortal()
    form.show_dialog()
    sys.exit(app.exec_())