"""
This module contains the class for the OrderWindow.
The OrderWindow provides the user interface for viewing and managing a customer's orders.

It includes the following functionalities:
- Displaying a list of orders with relevant details (Order ID, Order Status, Ordered Date, Shipped Date, Total).
- Enforcing fixed column widths and formatting for the tables displaying order data.
- Handling clicks on orders to populate detailed information about the selected order.
- Navigating back to the MainWindow when the "Back" button is clicked.
- Populating the order details table when an order is selected from the orders table.
- Enabling the user to write a review for each product in the order by providing a "Write Review" button.
- Navigating back to the MainWindow when the "Back" button is clicked.

File: customer_order_history.py 
Project: E-Commerce Management System
Author: A SQL Master
Course: DATA 201    
"""

from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHeaderView
from PyQt5 import uic
import mysql.connector
from data201 import make_connection

class OrderWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()
        uic.loadUi("customer_order_history.ui", self)  # Load UI for the order window

        # Store reference to MainWindow for navigation
        self.main_window = main_window

        # Access the widgets defined in the UI
        self.table_orders = self.findChild(QTableWidget, "table_orders")  # Table for displaying orders
        self.table_order_details = self.findChild(QTableWidget, "table_order_details")  # Table for displaying order details
        self.cart_button = self.findChild(QPushButton, "pushButton")  # Back button to return to MainWindow

        # Set up tables for displaying orders and order details
        self.setup_table(self.table_orders, ["Order ID", "Order Status", "Ordered Date", "Shipped Date", "Total"])
        self.setup_table(self.table_order_details, ["Product ID", "Product Name", "Unit Price", "Quantity", "Review"])

        # Connect Back button to the MainWindow
        self.cart_button.clicked.connect(self.go_to_main_window)

        # Populate the orders table with data
        self.populate_orders()

    def setup_table(self, table_widget, headers):
        """Set up the table with non-adjustable headers."""
        table_widget.setColumnCount(len(headers))  # Set the number of columns based on headers
        table_widget.setHorizontalHeaderLabels(headers)  # Set the headers for the columns
        header = table_widget.horizontalHeader()

        # Fix header and prevent resizing
        header.setSectionsClickable(False)  # Disable clicking on the header to sort
        header.setStretchLastSection(False)  # Prevent last column from stretching

        # Set table properties: Read-only cells, word wrapping, and alternating row colors
        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # Make cells read-only
        table_widget.setWordWrap(True)  # Allow text wrapping in cells
        table_widget.setAlternatingRowColors(True)  # Alternate row colors for readability

    def enforce_column_widths(self, table_widget):
        """Explicitly enforce larger column widths for specific columns."""
        column_count = table_widget.columnCount()  # Get the total number of columns
        for i in range(column_count):
            if i == 2:  # "Ordered Date" column
                table_widget.setColumnWidth(i, 300)  # Set a wider width for "Ordered Date"
            elif i == 3:  # "Shipped Date" column
                table_widget.setColumnWidth(i, 300)  # Set a wider width for "Shipped Date"
            else:
                table_widget.setColumnWidth(i, 150)  # Set default width for other columns

            header = table_widget.horizontalHeader()
            header.setSectionResizeMode(i, QHeaderView.Fixed)  # Enforce fixed column widths

    def populate_orders(self):
        """Populate the orders table with data fetched from the database."""
        try:
            # Connect to the database
            conn = make_connection(config_file = 'sqlproject.ini')  # Establish a database connection
            cursor = conn.cursor()

            # SQL query to retrieve orders data
            query = """
                SELECT 
                    oi.order_id,
                    o.order_status,
                    o.order_purchase_timestamp,
                    o.order_estimated_delivery_date,
                    SUM(op.payment_value) AS total
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                JOIN order_payments op ON o.order_id = op.order_id
                GROUP BY oi.order_id, o.order_status, o.order_purchase_timestamp, o.order_estimated_delivery_date
                ORDER BY o.order_purchase_timestamp DESC
            """
            cursor.execute(query)  # Execute the query
            results = cursor.fetchall()  # Fetch all results

            self.table_orders.setRowCount(len(results))  # Set the number of rows in the table

            # Insert the fetched data into the orders table
            for row_index, row_data in enumerate(results):
                for col_index, value in enumerate(row_data):
                    self.table_orders.setItem(row_index, col_index, QTableWidgetItem(str(value)))

            # Apply initial resizing and enforce column widths
            self.table_orders.resizeColumnsToContents()  # Resize columns to fit contents
            self.enforce_column_widths(self.table_orders)  # Enforce specific column widths

            for i in range(self.table_orders.columnCount()):
                print(f"Column {i} width: {self.table_orders.columnWidth(i)}")  # Print column widths for debugging

            # Connect cell click event to populate order details
            self.table_orders.cellClicked.connect(self.populate_order_details)  # Link cell click to order details population

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            # Handle database errors
            QMessageBox.critical(self, "Database Error", f"Failed to retrieve orders: {err}")  # Display error message

    def populate_order_details(self, row, column):
        """Populate the order details table based on the selected order."""
        try:
            # Get the selected order ID from the orders table
            selected_order_id = self.table_orders.item(row, 0).text()

            # Establish a database connection
            conn = make_connection(config_file = 'sqlproject.ini')
            cursor = conn.cursor()

            # Query to fetch product details for the selected order
            query = """
                SELECT 
                    oi.product_id,
                    p.product_description AS product_name,
                    p.product_price AS unit_price,
                    oi.quantity
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """
            cursor.execute(query, (selected_order_id,))
            results = cursor.fetchall()  # Fetch the product details for the selected order

            # Set the number of rows in the order details table
            self.table_order_details.setRowCount(len(results))

            # Populate the order details table with fetched data
            for row_index, row_data in enumerate(results):
                for col_index, value in enumerate(row_data):
                    self.table_order_details.setItem(row_index, col_index, QTableWidgetItem(str(value)))

                # Add a "Write Review" button in the last column of the order details table
                review_button = QPushButton("Write Review")
                review_button.clicked.connect(
                    lambda _, p_id=row_data[0], p_name=row_data[1]: self.open_review_window(p_id, p_name)  # Open review window when clicked
                )
                self.table_order_details.setCellWidget(row_index, 4, review_button)  # Add the button to the table

            # Apply initial resizing and enforce specific column widths
            self.table_order_details.resizeColumnsToContents()  # Automatically resize columns to fit content
            self.enforce_column_widths(self.table_order_details)  # Enforce fixed column widths

            # Debugging: Print column widths to verify proper layout
            for i in range(self.table_order_details.columnCount()):
                print(f"Column {i} width: {self.table_order_details.columnWidth(i)}")

            # Close the database connection
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            # Handle database errors
            QMessageBox.critical(self, "Database Error", f"Failed to retrieve order details: {err}")  # Show error message

    def open_review_window(self, product_id, product_name):
        """Open the review window for the selected product."""
        from customer_review_window import ReviewWindow  # Import ReviewWindow here to avoid circular imports
        review_window = ReviewWindow(product_id, product_name)  # Create the review window instance
        review_window.exec_()  # Show the review window as a modal dialog

    def go_to_main_window(self):
        """Return to MainWindow without closing."""
        self.hide()  # Hide the current window
        self.main_window.show()  # Show the MainWindow

