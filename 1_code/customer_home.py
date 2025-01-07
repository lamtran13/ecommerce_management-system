"""
This module contains the class for the Customer Portal.
The Portal has the following functionalities:

- View and manage customer orders (view order history, track order status, etc.)
- Add items to the shopping cart.
- Browse and filter products by category.
- Apply sorting and search filters to product listings.
- Proceed to checkout and place orders.
- Update quantities of items in the cart.
- View and interact with the product catalog.
- Log out from the customer portal.

File: customer_home.py
Project: E-Commerce Management System
Author: A SQL Master
Course: DATA 201    
"""


from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QMenu, QAction, QToolButton, QDialog, QVBoxLayout,
    QHBoxLayout, QSpinBox, QLabel, QFormLayout, QMessageBox, QWidget, QSizePolicy, QHeaderView, QFrame, 
)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import uic
import mysql.connector
import sys  
from customer_review_window import OrderWindow  
from data201 import make_connection
import os
from shared import open_login_portal
from datetime import datetime, timedelta


class CheckoutWindow(QDialog):
    """
    A window for the checkout process where the user can provide details like
    name, address, email, and phone number before submitting the order.

    Input:
        - total_price (float): The total price of the items in the cart.
        - cart_window (CartWindow): The window displaying the cart with items.
        - main_window (QMainWindow): The main window of the application.
        - customer_id (int): The ID of the customer placing the order.

    Output:
        - A QDialog window where the user can input their details and proceed with the order submission or cancel the operation.
    """
    
    def __init__(self, total_price, cart_window, main_window, customer_id):
        super().__init__()
        self.setWindowTitle("Checkout")  # Set the window title
        self.total_price = total_price  # Store the total price for the checkout
        self.cart_window = cart_window  # Store the cart window reference
        self.main_window = main_window  # Store the main window reference

        # Layout for form inputs
        layout = QVBoxLayout()  # Main layout of the checkout window
        form_layout = QFormLayout()  # Layout for the form inputs

        # Input fields for user details
        self.name_input = QLineEdit()  # Input field for name
        self.address_input = QLineEdit()  # Input field for address
        self.phone_input = QLineEdit()  # Input field for phone number
        self.customer_id = customer_id  # Store the customer ID

        layout.addLayout(form_layout)  # Add the form layout to the main layout

        # Total price label
        self.total_label = QLabel(f"Total Price: ${total_price:.2f}")  # Display the total price
        layout.addWidget(self.total_label)

        # Buttons layout
        button_layout = QHBoxLayout()  # Layout for the buttons

        # Submit button
        submit_button = QPushButton("Submit")  # Button to submit the details
        submit_button.clicked.connect(self.submit_details)  # Connect to the submit details method
        button_layout.addWidget(submit_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")  # Button to cancel the checkout
        cancel_button.clicked.connect(self.close)  # Close the checkout window when clicked
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)  # Add the button layout to the main layout
        self.setLayout(layout)  # Set the main layout for the window

        # Automatically shrink to fit content
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow resizing
        self.adjustSize()  # Adjust the size of the window to fit its content


class CartWindow(QDialog):
    """
    A custom window for displaying cart items and handling interactions such as 
    checking out, updating quantities, and closing the cart window.
    
    Input:
        - cart_items (list): A list of cart items, where each item is a tuple containing:
            - product_id (int)
            - category (str)
            - description (str)
            - price (str, includes '$' symbol)
            - quantity (int)
        - customer_id (int): The ID of the customer viewing the cart.
        - main_window (QMainWindow): The main window from which the cart window is opened.
    
    Output:
        - A QDialog window showing the cart items with options to adjust quantities, 
          proceed to checkout, and close the cart.
    """
    
    def __init__(self, cart_items, customer_id, main_window):
        super().__init__()
        self.cart_items = cart_items  # List of cart items
        self.main_window = main_window  # Main window reference
        self.customer_id = customer_id  # Customer ID
        self.resize(800, 600)  # Set the default size for the CartWindow
        self.is_maximized = False  # Flag to track if the window is maximized

        # Remove default title bar for custom title
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Main layout for the cart window
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Custom title bar
        title_bar = QFrame()  # Frame for title bar
        title_bar.setStyleSheet("background-color: #FFC0CB;")  # Pink background
        title_bar.setFixedHeight(30)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        # Title text
        title_label = QLabel("Cart Items")
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        title_layout.addWidget(title_label)

        # Close button
        close_button = QPushButton("X")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 0 5px;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.close)  # Close window when clicked
        title_layout.addWidget(close_button, alignment=Qt.AlignRight)

        main_layout.addWidget(title_bar)  # Add custom title bar to the main layout

        # Cart content layout
        cart_layout = QVBoxLayout()
        self.setup_cart_layout(cart_layout)  # Method to set up the cart table layout
        main_layout.addLayout(cart_layout)

        # Apply pink theme styles to the entire cart window and its components
        self.setStyleSheet("""
        QDialog {
            background-color: #FFE4E1; /* Light pink background */
        }
        QLabel {
            color: #FF69B4; /* Hot pink text */
            font-weight: bold;
        }
        QTableWidget {
            background-color: #FFF0F5; /* Lavender blush for table */
            color: #FF69B4; /* Hot pink text */
            border: 1px solid #FFC0CB; /* Pink border */
        }
        QTableWidget::item {
            color: #FF69B4; /* Hot pink text for items */
        }
        QHeaderView::section {
            background-color: #FFC0CB; /* Pink background for headers */
            color: white; /* White text */
            border: 1px solid #FF69B4; /* Hot pink border */
            font-weight: bold;
            padding: 5px;
            text-align: center;
        }
        QSpinBox {
            background-color: #FFC0CB; /* Pink background for spin boxes */
            border: 1px solid #FF69B4; /* Hot pink border */
            border-radius: 5px;
        }
        QPushButton {
            background-color: #FFC0CB; /* Pink button */
            color: white;
            border: 1px solid #FF69B4; /* Hot pink border */
            border-radius: 5px;
            font-weight: bold;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #FF69B4; /* Darker pink when hovered */
        }
        QPushButton:pressed {
            background-color: #FF1493; /* Even darker pink when pressed */
        }
    """)


    def setup_cart_layout(self, layout):
        """
        Set up the cart layout.
        
        Input:
            - layout (QVBoxLayout): The layout to which the cart table and buttons will be added.
            - cart_items (list): A list of cart items, where each item is a list or tuple containing:
                - Product ID (str or int)
                - Category (str)
                - Description (str)
                - Price (float or int)
                - Quantity (int)
            
        Output:
            - QTableWidget: Displays cart items with columns for Product ID, Category, Description, Price, Quantity, and Delete.
            - SpinBox widgets: Allow users to change the quantity of each item.
            - Delete buttons: Allow users to delete items from the cart.
            - Total price label: Displays the total price of the cart.
            - "Check Out", "Save", "Close", and "Toggle Window Size" buttons for further actions.
            - The layout will be updated with the cart table and buttons.
        """
        
        # Table setup: Create and configure a QTableWidget to display cart items
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Define 6 columns for the table
        self.table.setHorizontalHeaderLabels(["Product ID", "Category", "Description", "Price", "Quantity", "Delete"])  # Column labels
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make cells uneditable (no direct edits allowed)
        layout.addWidget(self.table)  # Add the table to the provided layout

        # Hide the vertical header (row indices) for a cleaner look
        self.table.verticalHeader().setVisible(False)

        # Disable header resizing to keep column widths fixed
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)  # Disable resizing of columns
        header.setDefaultSectionSize(40)  # Set the height of the header row to a fixed value

        # Set custom widths for each column
        self.table.setColumnWidth(0, 150)  # Set width for Product ID column
        self.table.setColumnWidth(1, 165)  # Set width for Category column
        self.table.setColumnWidth(2, 200)  # Set width for Description column
        self.table.setColumnWidth(3, 100)  # Set width for Price column
        self.table.setColumnWidth(4, 80)   # Set width for Quantity column
        self.table.setColumnWidth(5, 100)  # Set width for Delete column

        # Populate the table with cart items
        self.table.setRowCount(len(self.cart_items))  # Set the number of rows based on the cart items
        self.spin_boxes = []  # List to store spin boxes for quantity updates
        for row_index, item in enumerate(self.cart_items):  # Loop through each item in the cart
            # Set item details in the respective columns
            for col_index, value in enumerate(item[:4]):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))  # Set value in first four columns

            # Create a QSpinBox for the quantity and set it in the Quantity column
            spin_box = QSpinBox()
            spin_box.setMinimum(1)  # Set the minimum quantity to 1
            spin_box.setValue(item[4] if len(item) > 4 else 1)  # Set initial value based on item quantity
            spin_box.valueChanged.connect(lambda value, r=row_index: self.update_quantity(r, value))  # Connect the quantity change event to update_quantity method
            self.table.setCellWidget(row_index, 4, spin_box)  # Place the spin box in the Quantity column
            self.spin_boxes.append(spin_box)  # Store spin box for future reference

            # Create a Delete button and connect it to the delete_item method
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, r=row_index: self.delete_item(r))  # Connect delete event to delete_item method
            self.table.setCellWidget(row_index, 5, delete_button)  # Place the Delete button in the last column

        # Create a layout for buttons (Total Price, Check Out, Save, Close)
        button_layout = QHBoxLayout()
        self.total_label = QLabel()  # Label to display the total price
        self.update_total_price()  # Update total price label based on current cart items
        button_layout.addWidget(self.total_label)  # Add total price label to button layout

        # Create and configure Check Out button
        check_out_button = QPushButton("Check Out")
        check_out_button.clicked.connect(self.check_out)  # Connect the check out button to check_out method
        button_layout.addWidget(check_out_button)  # Add Check Out button to button layout

        layout.addLayout(button_layout)  # Add the button layout to the main layout

        # Create and configure Save button to save any changes to the cart
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_changes)  # Connect the Save button to the save_changes method
        layout.addWidget(save_button)  # Add Save button to the main layout

        # Create and configure Close button to close the cart window
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)  # Connect the Close button to close method
        layout.addWidget(close_button)  # Add Close button to the main layout

        # Create and configure Toggle Window Size button to toggle the size of the cart window
        open_bigger_window_button = QPushButton("Toggle Window Size")
        open_bigger_window_button.clicked.connect(self.toggle_window_size)  # Connect to toggle_window_size method
        layout.addWidget(open_bigger_window_button)  # Add Toggle Window Size button to the main layout


    def update_total_price(self):
        """Update the total price label with the sum of all items in the cart.
        
        Input:
            - cart_items (list): A list of cart items, where each item is expected to be a list or tuple containing:
                - Product ID (str or int)
                - Category (str)
                - Description (str)
                - Price (str, including '$' symbol)
                - Quantity (int)

        Output:
            - The total price is calculated by summing the product of price and quantity for each item.
            - The total price label is updated to reflect the calculated value.
            - The label's text color is set to dark pink and font size to 16px.
        """
        
        # Calculate the total price by summing the price multiplied by quantity for each item
        total_price = sum(float(item[3].replace('$', '')) * item[4] for item in self.cart_items)
        
        # Update the total price label with the formatted value
        self.total_label.setText(f"Total Price: ${total_price:.2f}")
        
        # Style the total price label (dark pink text with a font size of 16px)
        self.total_label.setStyleSheet("font-size: 16px; color: #FF1493;")

    def open_bigger_window(self):
        """Maximize the window and set a minimum size to prevent excessive shrinking."""
        self.showMaximized()  # Maximize the window to take up the full screen
        self.setMinimumSize(700, 500) # Set the minimum window size to 700x500 pixels


    def update_quantity(self, row_index, value):
        """
        Update the quantity of an item in the cart and recalculate the total price.
        
        Input:
            - row_index (int): The index of the cart item whose quantity is being updated.
            - value (int): The new quantity value to set for the item at the specified row_index.
        
        Output:
            - cart_items (list): The cart item at row_index is updated with the new quantity value.
            - Total Price (float): The total price of the cart is recalculated and updated.
            - Error message (str, if applicable): If row_index is out of range, an error message is printed.
        """
        
        if 0 <= row_index < len(self.cart_items):  # Check if the row_index is within the valid range
            self.cart_items[row_index] = (*self.cart_items[row_index][:4], value)  # Update the quantity of the item at the given row index
            self.update_total_price()  # Recalculate and update the total price after the quantity change
        else:
            print(f"Error: row_index {row_index} is out of range.")  # Print an error message if the row_index is out of range

    def delete_item(self, row_index):
        """
        Delete an item from the cart and update the cart display and total price.
        
        Input:
            - row_index (int): The index of the cart item to be deleted.
        
        Output:
            - cart_items (list): The cart item at row_index is removed from the cart.
            - Table Row (QTableWidget): The row corresponding to the deleted item is removed from the table.
            - spin_boxes (list): The spin box corresponding to the deleted item is removed from the list.
            - Cart Count and Total Price: The cart item count and total price are updated.
            - Console Output (str): A message is printed showing the deleted item and the updated cart.
        """
        
        if row_index < len(self.cart_items):  # Check if the row_index is valid
            del self.cart_items[row_index]   # Remove the item from the cart
            self.table.removeRow(row_index)  # Remove the corresponding row from the table
            del self.spin_boxes[row_index]  # Remove the corresponding spin box
            self.update_cart_count()        # Update the cart item count
            self.update_total_price()       # Recalculate and update the total price
            print(f"Deleted item at row {row_index}. Updated cart: {self.cart_items}")  # Print the updated cart


    def update_cart_count(self):
        """
        Update the cart count and the cart button text based on the total quantity of items in the cart.
        
        Input:
            - cart_items (list): A list of cart items, where each item is expected to be a list or tuple containing:
                - Product ID (str or int)
                - Category (str)
                - Description (str)
                - Price (float or int)
                - Quantity (int)
        
        Output:
            - cart_count (int): The total number of items in the cart (sum of quantities).
            - Cart Button Text: The cart button text is updated to show the current item count.
            - Console Output (str): A message is printed showing the updated cart item count.
        """
        
        # Calculate the total quantity of items in the cart by summing the quantity of each item
        total_items = sum(item[4] for item in self.cart_items)
        
        # Update the cart count in the main window and update the cart button text
        self.main_window.cart_count = total_items  # Update the cart count in the main window
        self.main_window.cart_button.setText(f"Cart ({total_items})")  # Update the cart button's label
        
        print(f"Cart updated to {total_items} items.") # Print the updated cart count to the console


    def update_total_price(self):
        """
        Update the total price label based on the items in the cart.
        
        Input:
            - cart_items (list): A list of cart items, where each item is expected to be a list or tuple containing:
                - Product ID (str or int)
                - Category (str)
                - Description (str)
                - Price (str) (includes the '$' symbol)
                - Quantity (int)
        
        Output:
            - total_price (float): The total price of all items in the cart (calculated as the sum of price * quantity for each item).
            - Total Price Label: The total price label (`self.total_label`) is updated with the calculated total price, formatted to two decimal places.
            - Console Output (str, if applicable): If an error occurs, an error message is printed, and the label is updated with the calculated value (if possible).
        """
        
        try:
            # Calculate the total price by summing the product of price (after removing '$') and quantity for each item
            total_price = sum(float(item[3].replace('$', '')) * item[4] for item in self.cart_items)
            
            # Update the total price label with the formatted value
            self.total_label.setText(f"Total: ${total_price:.2f}")
        
        except Exception as e:
            print(f"Error updating total price: {e}")  # If an error occurs during the calculation, print the error message
            self.total_label.setText(f"Total Price: ${total_price:.2f}") # Set a default total price label in case of error
            print(f"Updated total price: ${total_price:.2f}") # Print the updated total price to the console


    def save_changes(self):
        """
        Save the changes made to the cart, update the cart items, and refresh the cart count.
        
        Input:
            - spin_boxes (list): A list of QSpinBox widgets used for updating the quantity of items in the cart.
            - cart_items (list): A list of cart items, where each item is expected to be a list or tuple containing:
                - Product ID (str or int)
                - Category (str)
                - Description (str)
                - Price (float or int)
                - Quantity (int)
        
        Output:
            - cart_items (list): The cart items are updated with the new quantities from the spin boxes.
            - cart_count (int): The cart item count is updated.
            - Console Output (str): A message is printed showing the updated cart items.
            - Cart Data: The updated cart items are saved in the `main_window.cart_items`.
            - Window Closure: The current window is closed after saving the changes.
        """
        
        # Loop through each spin box to update the quantity for each cart item
        for i, spin_box in enumerate(self.spin_boxes):
            quantity = spin_box.value()  # Get the new quantity from the spin box
            self.cart_items[i] = (*self.cart_items[i][:4], quantity)  # Update the cart item with the new quantity

        self.main_window.cart_items = self.cart_items # Save the updated cart items to the main window
        self.update_cart_count()  # Update the cart count to reflect the changes
        print(f"Saved updated cart items: {self.cart_items}") # Print the updated cart items to the console for verification
        self.close()


    def get_seller_id(self, product_id):
        """
        Retrieve seller_id for a given product_id from the database.
        
        Input:
            - product_id (int or str): The product ID for which the seller ID needs to be retrieved.
        
        Output:
            - seller_id (int or None): The seller ID associated with the given product ID, or None if no seller is found.
            - Console Output (str, if applicable): If an error occurs, an error message is printed to the console.
        """
        
        try:
            # SQL query to retrieve the seller_id from the product_stock table using product_id
            query = """
                SELECT seller_id FROM product_stock WHERE product_id = %s
            """
            self.cursor.execute(query, (product_id,)) # Execute the query with the given product_id
            result = self.cursor.fetchone() # Fetch the result (if any)
            return result[0] if result else None  # Return the seller_id if found, otherwise return None
        
        except Exception as e:
            # Print an error message if an exception occurs
            print(f"Error retrieving seller_id for product_id {product_id}: {e}")
            return None


    def check_out(self):
        """
        Process the checkout, insert the order into the database, update the stock, and handle the payment.
        
        Input:
            - cart_items (list): A list of cart items, where each item is a tuple containing:
                - product_id (int)
                - category (str)
                - description (str)
                - price (str, includes '$' symbol)
                - quantity (int)
            - customer_id (int): The ID of the customer placing the order.
        
        Output:
            - order_id (int): A new order ID is generated and used to insert a new order.
            - Database Changes: New records are inserted into `orders`, `order_items`, and `order_payments` tables.
            - Cart Update: Cart is cleared after the order is placed.
            - QMessageBox: A confirmation message is displayed, or an error message is shown if something goes wrong.
        """
        
        # Establish a connection to the database and create a cursor
        self.connection = make_connection(config_file='sqlproject.ini')
        self.cursor = self.connection.cursor()
        print(f"Customer ID passed through: {self.customer_id}")

        try:
            # Get today's date and calculate the shipping limit date
            today = datetime.now()  # Get the current date and time
            shipping_date = today + timedelta(days=7)  # Calculate the shipping limit date (7 days from today)

            # Retrieve the current maximum order_id and generate a new order_id
            order_id_query = "SELECT MAX(order_id) FROM orders"  # Query to get the highest order_id
            self.cursor.execute(order_id_query)
            max_order_id = self.cursor.fetchone()[0]  # Fetch the result of the query
            new_order_id = (max_order_id + 1) if max_order_id else 1  # If there's an order already, increment; otherwise, start from 1

            # Insert the order into the orders table
            order_query = """
                INSERT INTO orders (order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, 
                                    order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(order_query, (new_order_id, self.customer_id, 'in progress',
                                            today.strftime('%Y-%m-%d %H:%M:%S'), None, None, None, None))
            
            total_price = 0 # Initialize total_price

            # Check if cart is empty
            if not self.cart_items:  # If the cart is empty, show a warning and return
                QMessageBox.warning(self, "Empty Cart", "Your cart is empty. Please add items before checking out.")
                return

            # Insert order items into the order_items table
            for item in self.cart_items:
                product_id, category, description, price, quantity = item

                # Calculate total price for the order
                total_price += float(price.replace('$', '')) * quantity  # Remove the '$' symbol and calculate total price

                # Update stock and insert order items
                self.update_stock_quantity(product_id, self.get_stock_quantity(product_id) - quantity)  # Update stock after the order
                seller_id = self.get_seller_id(product_id)  # Retrieve the seller ID for the product
                query = """
                    INSERT INTO order_items (order_id, product_id, seller_id, shipping_limit_date, freight_value, quantity)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, (new_order_id, product_id, seller_id, shipping_date, 0.0, quantity))

            # Insert payment information into the order_payments table
            payment_query = """
                INSERT INTO order_payments (order_id, payment_type, payment_installments, payment_value)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(payment_query, (new_order_id, 'credit_card', 1, total_price))  # Assume payment is by credit card
            self.connection.commit() 

            # Clear the cart and notify the user
            self.clear_cart()  # Clear the cart after the order is placed
            QMessageBox.information(self, "Order Placed", f"Order {new_order_id} placed successfully!")

            # Refresh the order history in the main window's order window
            if self.main_window.order_window and self.main_window.order_window.isVisible():
                self.main_window.order_window.populate_orders()

        except Exception as e:
            # Rollback the transaction if an error occurs and display an error message
            self.connection.rollback()
            print(f"Error during checkout: {e}")
            QMessageBox.critical(self, "Error", f"Failed to place order: {e}")

        finally:
            self.cursor.close()
            self.connection.close()


    def get_stock_quantity(self, product_id):
        """
        Retrieve the available stock quantity for a given product_id from the database.
        
        Input:
            - product_id (int or str): The product ID for which the stock quantity is needed.
        
        Output:
            - stock_quantity (int or None): The available stock quantity for the given product ID, or None if not found.
            - Console Output (str, if applicable): If an error occurs, an error message is printed to the console.
        """
        
        try:
            # SQL query to retrieve the stock quantity from the product_stock table using product_id
            query = """
                SELECT stock FROM product_stock WHERE product_id = %s
            """
            self.cursor.execute(query, (product_id,))  # Execute the query with the given product_id
            result = self.cursor.fetchone() # Fetch the result of the query (stock quantity)
            return result[0] if result else None # Return the stock quantity if found, otherwise return None
        
        except Exception as e:
            print(f"Error retrieving stock quantity for product_id {product_id}: {e}")
            return None


    def update_stock_quantity(self, product_id, new_quantity):
        """
        Update the stock quantity for a given product_id after the order is placed.
        
        Input:
            - product_id (int or str): The product ID for which the stock quantity needs to be updated.
            - new_quantity (int): The new stock quantity for the product after the update.
        
        Output:
            - Database Update: The stock quantity for the given product_id is updated in the database.
            - Console Output (str, if applicable): If an error occurs, an error message is printed to the console.
        """
        
        try:
            # SQL query to update the stock quantity for the given product_id
            query = """
                UPDATE product_stock
                SET stock = %s
                WHERE product_id = %s
            """
            self.cursor.execute(query, (new_quantity, product_id)) # Execute the query with the new stock quantity and product_id
        
        except Exception as e:
            print(f"Error updating stock quantity for product_id {product_id}: {e}")
            raise 

    def clear_cart(self):
        """
        Clear all items from the cart, reset the cart table, and update the cart count and total price.
        
        Input:
            - cart_items (list): A list of cart items that will be cleared.
            - table (QTableWidget): The table displaying the cart items, which will be reset.
        
        Output:
            - cart_items (list): The cart is cleared (emptied).
            - table (QTableWidget): The cart table row count is set to 0, effectively clearing it.
            - cart_count (int): The cart count is updated to reflect the empty cart.
            - total_price (float): The total price label is updated to reflect the cleared cart.
            - Console Output (str): A message is printed to the console indicating that the cart has been cleared.
        """
        self.cart_items.clear()  # Empty the cart_items list
        self.table.setRowCount(0)  # Reset the cart table by setting the row count to 0 (removes all displayed rows)
        self.update_cart_count()  # Update the cart count to 0
        self.update_total_price()  # Update the total price label to reflect the empty cart
     
        print("Cart has been cleared.")

    
    def toggle_window_size(self):
        """
        Toggle between a normal and a bigger (maximized) window.
        
        Input:
            - is_maximized (bool): A boolean indicating whether the window is currently maximized.
        
        Output:
            - Window Resize: The window size is toggled between maximized and normal size.
            - is_maximized (bool): The window's maximized state is toggled.
        """
        
        if self.is_maximized:  # Check if the window is currently maximized
            self.resize(800, 600)  # Resize the window to a normal size (800x600 pixels)
        else:
            self.showMaximized()  # Maximize the window to full screen
        
        # Toggle the state of the window (from maximized to normal or vice versa)
        self.is_maximized = not self.is_maximized

    

class CustomerHome(QMainWindow):
    def __init__(self, customer_id, parent = None):
        super().__init__(parent)
        uic.loadUi("customer_home.ui", self)
        
        self.customer_id = customer_id
        # Cache data
        self.cached_data = []
        # Load data into cache
        self.load_data()

        self.refresh_order_history()

        # Set default size for the main window
        self.resize(800, 600)
        self.setMinimumSize(QSize(600, 600))

        # Automatically adjust size based on content
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.adjustSize()

        # Access widgets
        self.table_view = self.findChild(QTableWidget, "tableView")
        self.sort_combo = self.findChild(QComboBox, "comboBox")
        self.category_combo = self.findChild(QComboBox, "comboBox_2")
        self.search_bar = self.findChild(QLineEdit, "lineEdit")
        self.search_button = self.findChild(QPushButton, "pushButton")
        self.cart_button = self.findChild(QPushButton, "pushButton_2")
        self.user_button = self.findChild(QToolButton, "toolButton")  # Access the "User" button
        # Access the QLabel for the logo
        self.logo_label = self.findChild(QLabel, "logo_label")  # Replace 'logo_label' with your QLabel's object name
        
        # Set the logo image
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "picture", "logo.png")
        self.set_logo(logo_path) 
        
        self.user_button.setPopupMode(QToolButton.DelayedPopup)  # Disable dropdown behavior
        self.user_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")  # Remove the dropdown arrow




        if not self.user_button:
            raise RuntimeError("The User button (toolButton) was not found in the UI file.")

        self.cart_items = []  # Initialize cart items
        self.cart_count = 0  # Initialize cart count

        # Populate sorting options
        self.sort_combo.addItems(["Price: High to Low", "Price: Low to High"])
        self.sort_combo.currentIndexChanged.connect(self.apply_filters)

        # Populate categories
        self.populate_categories()
        self.category_combo.currentIndexChanged.connect(self.apply_filters)

        # Set up search functionality
        self.search_bar.textChanged.connect(self.apply_filters)  # Dynamically filter as you type

        # Set up user menu
        self.setup_user_menu()

            # Set up the table
        self.setup_table()  # Automatically adjust columns based on content and prevent resizing

        # Set up cart button functionality
        self.cart_button.clicked.connect(self.open_cart_window)

        # Populate the table
        self.populate_table_view(order_by="DESC")  # Default sorting: High to Low
        # Assuming `results` is a list of data and `layout` is a layout object
        # self.populate_table_view(self.results, self.layout, order_by="ASC", category="Books", search_query="Wooden")

        self.cart_window = None  # Track the cart window
        self.order_window = None  # Track the order window


    def load_data(self):
        """
        Load data from the database into a local cache.

        Input:
            - None (fetches data from the database to load into the cache)

        Output:
            - cached_data (list): A list of tuples containing the product data (product_id, product_category, product_description, product_price).
            - Console Output (str, if applicable): If a database error occurs, an error message is printed to the console.
        """
        try:
            # Establish a connection to the database using the provided configuration file
            conn = make_connection(config_file='sqlproject.ini')
            cursor = conn.cursor()

            # SQL query to fetch product data (product_id, product_category, product_description, product_price)
            query = """
                SELECT product_id, product_category, product_description, CONCAT('$', FORMAT(product_price, 2)) AS product_price
                FROM products
            """
            cursor.execute(query)  
            self.cached_data = cursor.fetchall()
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            print(f"Database error: {err}")

    def refresh_order_history(self):
        """Refresh the order history in the order window."""
        
        # Check if the order window exists and is visible
        if hasattr(self, 'order_window') and self.order_window.isVisible():
            # If the order window is visible, refresh its data by calling populate_orders method
            self.order_window.populate_orders()

    def open_order_history(self):
        """
        Open the order history window, or show it if it's already open.
        
        Input:
            - None (fetches the order window for the customer)
        
        Output:
            - order_window (OrderWindow): Opens or shows the order history window for the customer.
            - Console Output (str, if applicable): If an error occurs, an error message is printed to the console.
        """
        try:
            # Check if the order_window attribute exists and is visible. If not, create and show the order window.
            if not hasattr(self, 'order_window') or not self.order_window.isVisible():
                self.order_window = OrderWindow(customer_id=self.customer_id, main_window=self)
            self.order_window.show()  # Show the order window
            self.hide()  # Hide the current window
        except Exception as e:
            # Print an error message if something goes wrong when opening the order history
            print(f"Error opening Order History: {e}")

    def setup_table(self):
        """Setup table headers and adjust column sizes."""
        
        # Disable user resizing of columns
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)  # Fix column size explicitly to prevent resizing
        header.setStretchLastSection(False)  # Prevent the last column from stretching to fill available space
        
        # Hide the vertical header (row indices)
        self.table_view.verticalHeader().setVisible(False)

        # Disable user adjustments for column resizing
        header.setSectionsClickable(False)

        # Set the number of rows in the table to 0 (initially empty)
        self.table_view.setRowCount(0)

        # Set column headers
        self.table_view.setColumnCount(5)  # Define 5 columns for the table
        self.table_view.setHorizontalHeaderLabels(["Product ID", "Category", "Description", "Price", "Add to Cart"])

        # Explicitly set the width of each column
        self.table_view.setColumnWidth(0, 100)  # Set width for Product ID column
        self.table_view.setColumnWidth(1, 150)  # Set width for Category column
        self.table_view.setColumnWidth(2, 250)  # Set width for Description column
        self.table_view.setColumnWidth(3, 100)  # Set width for Price column
        self.table_view.setColumnWidth(4, 85)   # Set width for "Add to Cart" button column

        # Apply custom style to the header (change header color)
        self.table_view.setStyleSheet("""
            QHeaderView::section {
                background-color: #FFC0CB;  /* Pink background for header */
                color: white;               /* White text color */
                border: 1px solid #FF69B4; /* Hot pink border for header */
                font-weight: bold;          /* Bold font for header */
                padding: 5px;               /* Padding for header text */
            }
            QHeaderView::section:horizontal {
                border: 1px solid #FF1493; /* Hot pink border for horizontal header */
            }
        """)

    def setup_user_menu(self):
        """
        Set up the user menu, including actions for viewing the order history and logging out.
        
        Input:
            - None
        
        Output:
            - A context menu with options for 'Order History' and 'Log Out' is attached to the user button.
            - The menu is styled with custom colors and hover effects.
        """
        
        # Create the user menu and initialize it
        user_menu = QMenu(self)

        # Create actions for the menu
        order_history_action = QAction("Order History", self)  # Action for viewing order history
        logout_action = QAction("Log Out", self)  # Action for logging out

        # Connect actions to corresponding methods
        order_history_action.triggered.connect(self.open_order_history)  # Connect to open_order_history method
        logout_action.triggered.connect(self.logout)  # Connect to logout method

        # Add actions to the menu
        user_menu.addAction(order_history_action)
        user_menu.addAction(logout_action)

        # Apply custom style to the menu (background color, text color, hover effects, etc.)
        user_menu.setStyleSheet("""
            QMenu {
                background-color: #FFC0CB;  /* Pink background */
                color: white;                /* White text */
                border: 1px solid #FF69B4;   /* Hot pink border */
            }
            QMenu::item {
                background-color: transparent; /* Transparent background for items */
                padding: 5px;
            }
            QMenu::item:selected {
                background-color: #FF69B4;  /* Hot pink on hover */
                color: white;                /* White text on hover */
            }
        """)

        # Attach the menu to the user button and set the popup mode to instantly show the menu
        self.user_button.setMenu(user_menu)  # Attach the menu to the user button
        self.user_button.setPopupMode(QToolButton.InstantPopup)  # Set the menu to show on button click


    def open_order_history(self):
        """
        Opens the order history window for the user.

        Input:
            - None

        Output:
            - order_window (OrderWindow): The order history window is opened for the customer.
            - Console Output (str, if applicable): If an error occurs while opening the order history, an error message is printed to the console.
        """
        
        try:
            # Create an instance of the OrderWindow and pass the customer ID and main window reference
            self.order_window = OrderWindow(customer_id=self.customer_id, main_window=self)
            self.order_window.show() # Show the order history window
            self.hide()             # Hide the current window
        except Exception as e:
            print(f"Error opening Order History: {e}")

    def logout(self):
        open_login_portal(self)

    def populate_categories(self):
        """
        Populate the category combo box with product categories from the database.
        
        Input:
            - None
        
        Output:
            - category_combo (QComboBox): The combo box is populated with distinct product categories from the database.
            - Console Output (str, if applicable): If a database error occurs, an error message is printed to the console.
        """
        
        try:
            conn = make_connection(config_file='sqlproject.ini')
            cursor = conn.cursor()

            # SQL query to fetch distinct product categories from the products table
            query = "SELECT DISTINCT product_category FROM products"

            cursor.execute(query)  
            categories = cursor.fetchall() 
            cursor.close()
            conn.close()

            self.category_combo.addItem("All Categories") # Add a default item "All Categories" to the combo box
            
            # Add each category to the combo box
            for category in categories:
                self.category_combo.addItem(category[0])

        except mysql.connector.Error as err:
            print(f"Database error: {err}")


    def populate_table_view(self, order_by="DESC", category=None, search_query=None):
        """Populate the table view using cached data."""
        
        # Initialize layout for the table view
        layout = QVBoxLayout(self)
        results = self.cached_data  # Use the cached data to populate the table
        button_height = 30  # Height of the button (same as set for the button)
        
        # Loop through the data and insert rows into the table
        for row_index, row_data in enumerate(results):
            self.table_view.insertRow(row_index)  # Insert a new row at the given index
            
            # Populate the row with data from cached_data
            for col_index, value in enumerate(row_data):
                self.table_view.setItem(row_index, col_index, QTableWidgetItem(str(value)))  # Set cell data
        
        # Apply category filter (if specified)
        if category and category != "All Categories":
            results = [row for row in results if row[1] == category]  # Filter by category
        
        # Apply search query filter (if specified)
        if search_query:
            search_query = search_query.lower()  # Convert search query to lowercase for case-insensitive comparison
            results = [
                row for row in results if
                search_query in str(row[0]).lower() or
                search_query in str(row[1]).lower() or
                search_query in str(row[2]).lower() or
                search_query in str(row[3]).lower()
            ]

        # Sort results based on price (column 3) in the specified order (ascending or descending)
        reverse = order_by == "DESC"
        results.sort(key=lambda x: x[3], reverse=reverse)  # Sort by price (column 3)

        # Reset the table and repopulate it with the filtered and sorted data
        self.table_view.setRowCount(0)  # Clear the existing rows
        for row_index, row_data in enumerate(results):
            self.table_view.insertRow(row_index)  # Insert a new row
            
            # Populate each row with the filtered and sorted data
            for col_index, value in enumerate(row_data):
                self.table_view.setItem(row_index, col_index, QTableWidgetItem(str(value)))  # Set the table cell value

            # Create the "Add to Cart" button for the current row
            add_to_cart_button = QPushButton("+")
            add_to_cart_button.setFixedSize(20, 20)  # Adjust button size
            add_to_cart_button.setToolTip("Add to Cart")  # Tooltip for the button
            # Apply the button's style
            add_to_cart_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFC0CB;  /* Pink background */
                    color: white;
                    font-weight: bold;
                    border: 1px solid #FF69B4; /* Hot pink border */
                    border-radius: 5px;
                    padding: 0 5px;
                }
                QPushButton:hover {
                    background-color: #FF69B4;  /* Darker pink on hover */
                }
                QPushButton:pressed {
                    background-color: #FF69B4;  /* Hot pink when pressed */
                    border: 1px solid #FF69B4;
                }
                QPushButton:focus {
                    outline: none;  /* Remove blue focus outline */
                }
            """)
            add_to_cart_button.clicked.connect(lambda _, r=row_data, button=add_to_cart_button: self.add_to_cart(r, button))
            
            # Create a layout to center the button
            button_layout = QHBoxLayout()
            button_layout.setAlignment(Qt.AlignCenter)  # Center the button within the cell
            button_layout.addWidget(add_to_cart_button)

            # Create a QWidget to hold the button layout and set it in the table cell
            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            # Set the button widget in the 5th column (index 4) of the current row
            self.table_view.setCellWidget(row_index, 4, button_widget)

            # Set row height to fit the button (button_height or slightly larger)
            self.table_view.setRowHeight(row_index, button_height + 10)  # Adding 10 pixels as buffer for the button height

        layout.addWidget(self.table_view)  # Add the table view to the layout


    def apply_filters(self):
        """Apply the selected filters and update the table view."""
        selected_sort = self.sort_combo.currentText()  # Get the selected text from the sort combo box
        # Determine the order for sorting: "DESC" for "High to Low" and "ASC" for "Low to High"
        order_by = "DESC" if "High to Low" in selected_sort else "ASC" 
        selected_category = self.category_combo.currentText()  # Get the selected category from the combo box
        search_query = self.search_bar.text()  # Get the search query from the search bar

        # Call the method to update the table view with the selected filters
        self.populate_table_view(order_by=order_by, category=selected_category, search_query=search_query)


    def add_to_cart(self, row_data, button):
        """
        Add an item to the cart or update its quantity if it's already in the cart.
        
        Input:
            - row_data (tuple): The data for the product being added (product_id, category, description, price).
            - button (QPushButton): The "Add to Cart" button associated with the product.
        
        Output:
            - cart_items (list): The cart items are updated with the new or modified item.
            - cart_count (int): The total number of items in the cart is updated.
            - cart_button (QPushButton): The cart button's label is updated to reflect the total number of items.
            - Console Output (str): The cart contents are printed to the console.
            - Button Style Update: The button's color toggles between pink and hot pink.
        """
        
        # Check if the item is already in the cart
        for i, item in enumerate(self.cart_items):
            if item[:4] == row_data:  # If the item is already in the cart, update its quantity
                self.cart_items[i] = (*item[:4], item[4] + 1)  # Increment the quantity by 1
                print(f"Updated quantity for item: {self.cart_items[i]}")  # Log the updated item
                break
        else:
            # If the item is not in the cart, add it with an initial quantity of 1
            self.cart_items.append((*row_data, 1))
            print(f"Added new item to cart: {row_data}")  # Log the added item

        # Update the cart count by summing the quantities of all items
        self.cart_count = sum(item[4] for item in self.cart_items)
        self.cart_button.setText(f"({self.cart_count})")  # Update the cart button label
        print(f"Current cart items: {self.cart_items}")  # Log the current cart contents

        # Toggle the button's color between pink and hot pink based on its current state
        current_style = button.styleSheet()

        # If the button is currently pink, change it to hot pink (indicating it's been clicked)
        if "background-color: #FFC0CB" in current_style:  # If the button is pink
            button.setStyleSheet("""
                QPushButton {
                    background-color: #FFC0CB; /* Pink button */
                    color: white;
                    font-weight: bold;
                    border: 1px solid #FF69B4; /* Hot pink border */
                    border-radius: 5px;
                    padding: 0 5px;
                }
                QPushButton:hover {
                    background-color: #FF69B4; /* Hot pink on hover */
                }
            """)  # Reset to normal pink with hover effect
        else:
            # Change it to a darker hot pink when clicked
            button.setStyleSheet("""
                QPushButton {
                    background-color: #FF69B4; /* Hot pink button */
                    color: white;
                    font-weight: bold;
                    border: 1px solid #FF69B4; /* Hot pink border */
                    border-radius: 5px;
                    padding: 0 5px;
                }
                QPushButton:hover {
                    background-color: #FF69B4;  /* Hot pink on hover */
                }
            """)  # Change to hot pink with hover effect


    def closeEvent(self, event):
        """
        Override the close event to close child windows when the main window is closed.
        
        Input:
            - event (QCloseEvent): The close event that is triggered when the window is closed.
        
        Output:
            - Closes child windows (cart and order windows) if they are open and visible.
            - Prints a message indicating the closure of the main window and child windows.
        """
        # Check if the cart window exists and is visible, then close it
        if self.cart_window and self.cart_window.isVisible():
            self.cart_window.close()
        
        # Check if the order window exists and is visible, then close it
        if self.order_window and self.order_window.isVisible():
            self.order_window.close()
        
        # Log a message indicating the closure of the main window and child windows
        print("Main window and all child windows closed.")
        
        # Accept the close event to allow the window to close
        event.accept()


    def open_cart_window(self):
        """
        Open the cart window with the current cart items.
        
        Input:
            - None
        
        Output:
            - Creates and shows the cart window, passing the cart items and customer ID to it.
        """
        # Create an instance of the CartWindow and pass the required data (cart items and customer ID)
        self.cart_window = CartWindow(self.cart_items, self.customer_id, self)
        
        # Show the cart window
        self.cart_window.show()


    def setup_cart_table(self):
        """
        Set up the cart table by adding spin boxes for quantity adjustment.
        
        Input:
            - None
        
        Output:
            - Populates the cart table with spin boxes for each item in the cart, allowing quantity changes.
        """
        # Loop through each item in the cart and add a spin box for quantity adjustment
        for row_index, item in enumerate(self.cart_items):
            spin_box = QSpinBox()  # Create a spin box for quantity
            spin_box.setValue(item[4])  # Set the initial value to the item's quantity
            spin_box.valueChanged.connect(lambda value, r=row_index: self.update_quantity(r, value))  # Connect the spin box to the update_quantity method
            
            # Set the spin box in the 5th column (index 4) of the current row
            self.cart_table.setCellWidget(row_index, 4, spin_box)


    def set_logo(self, logo_path):
        """
        Set the application logo by loading an image from the specified path.
        
        Input:
            - logo_path (str): The file path of the logo image.
        
        Output:
            - Sets the loaded logo as the pixmap for a QLabel to display it.
            - Prints an error message if the logo file is not found at the specified path.
        """
        # Load the logo image from the specified path
        pixmap = QPixmap(logo_path)
        
        # Check if the image was successfully loaded
        if not pixmap.isNull():
            # Set the pixmap on the logo label and scale it to fit the label's dimensions
            self.logo_label.setPixmap(pixmap)
            self.logo_label.setScaledContents(True)
        else:
            # Print an error message if the logo file was not found or couldn't be loaded
            print(f"Error: Logo not found at {logo_path}")


if __name__ == "__main__":
    """
    Entry point of the application. This block initializes and runs the application.
    
    Input:
        - None (this code is executed when the script is run directly)
    
    Output:
        - Launches the application and opens the main window (`CustomerHome`), passing the customer ID.
        - Starts the application's event loop.
    """
    
    customer_id = 1  # Example customer ID, could be dynamically set or fetched from a login process
    app = QApplication(sys.argv)  # Initialize the Qt application with command-line arguments
    main_window = CustomerHome(customer_id)  # Pass the customer ID to the CustomerHome window
    main_window.show()  # Display the main window
    sys.exit(app.exec_())  # Execute the application and ensure proper exit on closing

