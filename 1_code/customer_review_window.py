'''
This module contains the class for the ReviewWindow.
The ReviewWindow allows users to submit or cancel product reviews for orders.
It includes functionalities for:
- Submitting a review (rating and comment) and storing it in the database
- Updating an existing review if one already exists for the order
- Canceling the review and returning to the OrderWindow

File: customer_review_window.py 
Project: E-Commerce Management System
Author: A SQL Master
Course: DATA 201    
'''

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QPushButton, QPlainTextEdit, QLabel, QComboBox, QMessageBox, QHeaderView, QLineEdit, QVBoxLayout, QWidget
from PyQt5 import uic
from data201 import make_connection
from data201 import make_connection
import mysql.connector


class ReviewWindow(QMainWindow):
    """
    The ReviewWindow class manages the user interface for submitting reviews for products in an order.
    It allows the user to select a rating and enter a review comment for a product. The class checks if a review already exists 
    for the order and either updates the existing review or inserts a new one into the database.
    Upon successful submission, a success message is shown, and the order details in the OrderWindow are refreshed.
    The class also allows the user to cancel the review, in which case the ReviewWindow is closed, and the OrderWindow is displayed again.
    """
    
    def __init__(self, product_id, product_name, order_window, order_id, customer_id):
        super().__init__()
        uic.loadUi("customer_review_window.ui", self)

        # Store customer_id
        self.customer_id = customer_id

        # Set background color
        self.setStyleSheet("background-color: #F8E7E7;")

        # Access widgets
        self.comboBox_rating = self.findChild(QComboBox, "comboBox_rating")
        self.plainTextEdit_review = self.findChild(QPlainTextEdit, "plainTextEdit_review")
        self.pushButton_submit = self.findChild(QPushButton, "pushButton_submit")
        self.pushButton_submit_2 = self.findChild(QPushButton, "pushButton_submit_2")  # Cancel button

        # Initialize with product information
        self.product_id = product_id
        self.order_id = order_id  # Order associated with the review
        self.order_window = order_window  # Reference to the OrderWindow

        # Connect submit button
        self.pushButton_submit.clicked.connect(self.submit_review)
        self.pushButton_submit_2.clicked.connect(self.cancel_review)

    def submit_review(self):
        """ 
        This function allows the user to submit a review for an order. It retrieves the rating and review text entered by the user,
        checks for missing or incomplete inputs, and either inserts a new review or updates an existing one in the database.
        Upon successful submission, a success message is displayed, the order details are refreshed, and the review window is closed.
        
        """
        try:
            # Get review details
            rating = self.comboBox_rating.currentText().split(" - ")[0]
            review_text = self.plainTextEdit_review.toPlainText()

            if not rating or not review_text.strip():
                QMessageBox.warning(self, "Incomplete Input", "Please fill out all fields before submitting.")
                return

            # Connect to the database
            conn = make_connection(config_file='sqlproject.ini')
            cursor = conn.cursor()

            # Check if a review already exists for the order_id
            check_query = """
                SELECT COUNT(*) FROM order_reviews 
                WHERE order_id = %s
            """
            cursor.execute(check_query, (self.order_id,))
            review_exists = cursor.fetchone()[0]

            if review_exists:
                # If the review exists, update it
                update_query = """
                    UPDATE order_reviews
                    SET review_score = %s, comment_message = %s, review_date = NOW()
                    WHERE order_id = %s
                """
                cursor.execute(update_query, (rating, review_text, self.order_id))
                print(f"Updated review for Order ID {self.order_id}")
            else:
                # If the review doesn't exist, insert a new one
                insert_query = """
                    INSERT INTO order_reviews (review_score, comment_message, review_date, order_id)
                    VALUES (%s, %s, NOW(), %s)
                """
                cursor.execute(insert_query, (rating, review_text, self.order_id))
                print(f"Inserted new review for Order ID {self.order_id}")

            # Commit the changes to the database
            conn.commit()
            cursor.close()
            conn.close()

            # Show success message
            QMessageBox.information(self, "Review Submitted", "Thank you for your review!")

            # Refresh the order details in OrderWindow
            self.order_window.populate_order_details(
                self.order_window.table_orders.currentRow(), self.order_window.table_orders.currentColumn()
            )

            # Close the review window and show the order window
            self.close()
            self.order_window.show()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Failed to submit the review: {err}")

    def cancel_review(self):
        """Cancel the review and go back to the OrderHistory window."""
        # Close the review window and go back to the OrderWindow
        self.close()  # Close the review window
        self.order_window.show()  # Show the order history window again

class OrderWindow(QMainWindow):
    """
    The OrderWindow class handles the user interface for managing and viewing customer orders.

    It allows users to:
    - View a list of their orders, including order status, purchase date, and total amount.
    - Search and filter orders based on user input.
    - View detailed information for a selected order, including product details and associated reviews.
    - Write a review for a product within the selected order.
    - Navigate back to the main window from the OrderWindow.

    The class includes functions to set up and populate tables with order and product data,
    apply custom styling to the UI components, and handle user interactions like searching and selecting orders.
    """
    def __init__(self, main_window, customer_id):
        super().__init__()
        uic.loadUi("customer_order_history.ui", self)  

        self.customer_id = customer_id
        self.main_window = main_window

        # Access widgets
        self.table_orders = self.findChild(QTableWidget, "table_orders")
        self.table_order_details = self.findChild(QTableWidget, "table_order_details")
        self.cart_button = self.findChild(QPushButton, "pushButton")  

        # Add search box for filtering orders
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Search orders...")
        self.search_box.textChanged.connect(self.filter_orders)

        # Add the search box to the layout
        self.central_layout = QVBoxLayout()
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.central_layout.addWidget(self.search_box)
        self.central_layout.addWidget(self.table_orders)
        self.central_layout.addWidget(self.table_order_details)
        self.central_layout.addWidget(self.cart_button)
        self.central_widget.setLayout(self.central_layout)

        # Set up tables
        self.setup_table(self.table_orders, ["Order ID", "Order Status", "Ordered Date", "Shipped Date", "Total"])
        self.setup_table(self.table_order_details, [
            "Product ID", "Product Name", "Unit Price", "Quantity", "Review Score", "Review Comment", "Action"
        ])

        # Connect Cart button to go back to MainWindow
        self.cart_button.clicked.connect(self.go_to_main_window)

        # Populate orders table by default
        self.populate_orders()

    def setup_table(self, table_widget, headers):
        """Set up table with fixed column widths and non-adjustable headers."""
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)
        header = table_widget.horizontalHeader()

        # Prevent column resizing
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.Fixed)

        # Set default column widths
        for i, column_name in enumerate(headers):
            if column_name in ["Ordered Date", "Shipped Date", "Product Name"]:
                table_widget.setColumnWidth(i, 200)  # Wider for date columns
            elif column_name in ["Review Comment"]:
                table_widget.setColumnWidth(i, 600)  # Wider for date columns    
            elif column_name in ["Action", "Order Status"]:
                table_widget.setColumnWidth(i, 150)  # Wider for date columns   
            else:
                table_widget.setColumnWidth(i, 100)  # Default width for other columns

        # Disable editing and alternate row colors
        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        table_widget.setAlternatingRowColors(True)

        # Apply the stylesheet to the table widget to style the header
        table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #FFF0F5;  /* Lavender blush for table background */
                border: 1px solid #FFC0CB;  /* Pink border for table */
            }
            QHeaderView::section {
                background-color: #FFC0CB;  /* Pink background for headers */
                color: white;               /* White text for headers */
                border: 1px solid #FF69B4;  /* Hot pink border for header */
                font-weight: bold;          /* Bold text for header */
                padding: 5px;               /* Padding for header text */
                text-align: center;         /* Center text in header */
            }
            QHeaderView::section:horizontal {
                border: 1px solid #FF1493; /* Darker hot pink border for header */
            }
            QTableWidget::item {
                color: #FF69B4;             /* Hot pink text for items */
            }
        """)

        # Apply the style to the header
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #FFC0CB;  /* Pink background */
                color: white;               /* White text color */
                border: 1px solid #FF69B4;  /* Hot pink border */
                font-weight: bold;
                text-align: center;
                padding: 5px;
            }
        """)


    def populate_orders(self):
        """Populate the orders table with data from the database."""
        try:
            # Establish the database connection
            conn = make_connection(config_file='sqlproject.ini')
            cursor = conn.cursor()

            # Query to fetch orders based on the customer_id
            query = """
                SELECT 
                    o.order_id,
                    o.order_status,
                    o.order_purchase_timestamp,
                    o.order_estimated_delivery_date,
                    CONCAT('$', FORMAT(COALESCE(SUM(op.payment_value), 0), 2)) AS total
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                LEFT JOIN order_payments op ON o.order_id = op.order_id
                WHERE o.customer_id = %s
                GROUP BY 
                    o.order_id, 
                    o.order_status, 
                    o.order_purchase_timestamp, 
                    o.order_estimated_delivery_date
                ORDER BY o.order_purchase_timestamp DESC
            """

            # Execute the query with the provided customer_id
            print(f"Fetching orders for customer_id: {self.customer_id}")
            cursor.execute(query, (self.customer_id,))
            self.orders_data = cursor.fetchall()

            print(f"Orders fetched: {self.orders_data}")

            # Clear the table and populate it with fetched data
            self.table_orders.setRowCount(0)
            if not self.orders_data:
                # Handle the case where no orders are found
                QMessageBox.information(self, "No Orders", "You have no order history.")
                return

            for row_index, row_data in enumerate(self.orders_data):
                self.table_orders.insertRow(row_index)
                for col_index, value in enumerate(row_data):
                    self.table_orders.setItem(row_index, col_index, QTableWidgetItem(str(value)))

            # Connect cell click event to populate order details
            self.table_orders.cellClicked.connect(self.populate_order_details)
            cursor.close()
            conn.close()

            print("Order history populated successfully.")

        except mysql.connector.Error as err:
            # Log and display database errors
            print(f"Database error: {err}")
            QMessageBox.critical(self, "Database Error", f"Failed to fetch orders: {err}")

        except Exception as e:
            # Handle unexpected errors
            print(f"Unexpected error: {e}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")


    def filter_orders(self):
        """Filter orders based on search input."""
        search_term = self.search_box.text().lower()
        self.table_orders.setRowCount(0)  

        # Filter the orders data
        filtered_data = [
            row for row in self.orders_data if any(search_term in str(cell).lower() for cell in row)
        ]

        # Populate the table with filtered data
        for row_index, row_data in enumerate(filtered_data):
            self.table_orders.insertRow(row_index)
            for col_index, value in enumerate(row_data):
                self.table_orders.setItem(row_index, col_index, QTableWidgetItem(str(value)))
  
    def closeEvent(self, event):
        """Override close event to return to main window."""
        if self.main_window:
            self.main_window.show()
        print("Order history closed, returning to main window.")
        event.accept()

    def populate_order_details(self, row, column):
        try:
            # Get the selected order ID
            selected_order_id = self.table_orders.item(row, 0).text()

            # --- Fetch product details ---
            product_results = []
            try:
                conn_products = make_connection(config_file='sqlproject.ini')
                cursor_products = conn_products.cursor()

                query_products = """
                    SELECT 
                        oi.product_id,
                        p.product_description AS product_name,
                        CONCAT('$', FORMAT(p.product_price, 2)) AS unit_price,
                        oi.quantity
                    FROM 
                        order_items oi
                    JOIN 
                        products p ON oi.product_id = p.product_id
                    WHERE 
                        oi.order_id = %s
                """
                cursor_products.execute(query_products, (selected_order_id,))
                product_results = cursor_products.fetchall()

                # Ensure all results are consumed
                while cursor_products.nextset():
                    pass

            finally:
                cursor_products.close()
                conn_products.close()

            # --- Fetch review details ---
            review_results = []
            try:
                conn_review = make_connection(config_file='sqlproject.ini')
                cursor_review = conn_review.cursor()

                query_review = """
                    SELECT 
                        COALESCE(orv.review_score, 'No Review') AS review_score,
                        COALESCE(orv.comment_message, 'No Comments') AS review_comment
                    FROM 
                        order_reviews orv
                    WHERE 
                        orv.order_id = %s
                """
                cursor_review.execute(query_review, (selected_order_id,))
                review_results = cursor_review.fetchall()

                # Ensure all results are consumed
                while cursor_review.nextset():
                    pass

            finally:
                cursor_review.close()
                conn_review.close()

            # --- Populate the order details table ---
            self.table_order_details.setRowCount(0)  

            for row_index, product_data in enumerate(product_results):
                self.table_order_details.insertRow(row_index)
                for col_index, value in enumerate(product_data):
                    self.table_order_details.setItem(row_index, col_index, QTableWidgetItem(str(value)))

                # Add review score and comment if available
                review_score = "No Review"
                review_comment = "No Comments"

                if review_results:
                    review_score = review_results[0][0]
                    review_comment = review_results[0][1]

                self.table_order_details.setItem(row_index, 4, QTableWidgetItem(review_score))  # Review Score
                self.table_order_details.setItem(row_index, 5, QTableWidgetItem(review_comment))  # Review Comment

                            # Add "Write a Review" button
            write_review_button = QPushButton("Write a Review")
            write_review_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFC0CB;  /* Light pink background */
                    color: white;               /* White text */
                    font-weight: bold;
                    border: 1px solid #FF69B4;  /* Hot pink border */
                    border-radius: 5px;         /* Rounded corners */
                    padding: 5px 10px;          /* Padding around text */
                }

                QPushButton:hover {
                    background-color: #FF1493;  /* Darker pink on hover */
                    border: 1px solid #FF1493;  /* Darker pink border on hover */
                }

                QPushButton:pressed {
                    background-color: #FF69B4;  /* Keep it pink when pressed */
                    border: 1px solid #FF69B4;  /* Same pink border when pressed */
                }

                QPushButton:focus {
                    outline: none;              /* Remove blue focus outline */
                }
            """)
            write_review_button.clicked.connect(
                lambda _, p_id=product_data[0], p_name=product_data[1]: self.open_review_window(p_id, p_name, selected_order_id)
            )

            # Add button to the table
            self.table_order_details.setCellWidget(row_index, 6, write_review_button)


        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            QMessageBox.critical(self, "Database Error", f"Error fetching order details: {err}")

        except Exception as e:
            print(f"Unexpected error: {e}")
            QMessageBox.critical(self, "Error", f"Unexpected error occurred: {e}")


    def open_review_window(self, product_id, product_name, order_id):
        """Open the ReviewWindow for the selected product."""
        self.review_window = ReviewWindow(product_id, product_name, self, order_id, self.customer_id)
        self.review_window.show()
        self.hide()  # Hide the OrderWindow while the ReviewWindow is open

    def go_to_main_window(self):
        """Navigate back to the MainWindow."""
        self.close()
        self.main_window.show()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    from customer_home import CustomerHome
    main_window = CustomerHome()
    order_window = OrderWindow(main_window)
    order_window.show()
    sys.exit(app.exec_())
