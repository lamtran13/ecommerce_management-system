# E-Commerce Management System

## Description:
We designed and built a powerful e-commerce database system to improve inventory management, analyze sales trends, and support smarter decision-making using **MySQL** and **Python**. 

To make the system accessible and easy to use, we created intuitive interfaces for **customers**, **sellers**, and **managers** using **PyQt5**, ensuring a smooth experience for everyone. 

We also leveraged tools like **Pandas, NumPy, Matplotlib**, and **Seaborn** to analyze data and generate meaningful visualizations, helping streamline operations and create a better shopping experience.

This project received a **perfect score of 100/100**, highlighting its quality, functionality, and attention to detail.
## Features

### Customer Operations
- **Product Browsing:** Customers can filter products by category and sort them by price.
- **Shopping Cart:** Users can add products to the cart, adjust quantities, and view total costs.
- **Order Management:** Customers can track order statuses, view order details, and leave reviews.
- **Account Access:** Secure login and signup with password toggle for better user experience.

### Seller Operations
- **Order Management:** Sellers can view, filter, and update order statuses (e.g., "On the Way", "Order Delayed").
- **Customer Management:** Sellers can access customer details, track frequent buyers, and delete inactive accounts.
- **Payment Insights:** Track payment methods and trends, view payment details, and analyze product performance.

### Manager Operations
- **Seller Management:** Add, update, delete, and search for seller information.
- **Analytics Dashboards:** Visual insights include revenue trends, customer satisfaction, and delivery performance.
- **Product Monitoring:** Analyze sales by category, payment preferences, and order statuses.
- **Operational Insights:** Track key metrics like total sales, top-performing products, and delivery efficiency.

### Technical Implementation
- **Database Design:** Utilized MySQL with operational and analytical databases (star schema).
- **User Interfaces:** Developed intuitive portals for customers, sellers, and managers using PyQt5.
- **Data Visualization:** Used Pandas, NumPy, Matplotlib, and Seaborn for visualizing trends and insights.
- **ETL Processes:** Designed pipelines to transform and load data between operational and analytical databases.

## Installation:

### Prerequisties:
Before running the project, ensure the following software is installed and configured:
1. Cisco Secure Client (VPN)
- Install Cisco’s VPN client software to connect to the SJSU school’s database.
- Download and install it from [link instruction](https://www.sjsu.edu/it/services/network/vpn.php)
- Configure it with SJSU school’s VPN credentials to access the database
  
2. Python 3.8 or Higher: 
- Ensure you have Python installed on your system [Download here](https://www.python.org/downloads/).

4. MySQL Database Access
- You must have access credentials to the school’s database. Contact your instructor or IT department for details.
*This VPN only accessible for SJSU falcuty, students*.
  
### Guidance:
1. Clone the repository:
```
git clone git@github.com:lamtran13/ecommerce_management-system.git
```
2. Navigate to the project directory:
```
cd 1_code
```
2. Install the required Python packages:
```
pip install -r requirements.txt
```

## Usage
```
python login_page.py
```
- Customer account:
  - username: ```sandyhsy@gmail.com```
  - password: ```sandy0318```
- Seller account:
  - username: ```lam.n.tran@sjsu.edu```
  - password: ```employee1234```
- Manager account:
  - username: ```khacminhdai.vo@sjsu.edu```
  - password: ```manager1234```

## Acknowledgements:
- This project is a group effort completed as part of the [DATA 201](https://www.cs.sjsu.edu/~mak/DATA201/) Database Technologies for Data Analytics course with professor Ronald Mak at SJSU during Fall 2024.
- Team members who contributed to this project: Shao-Yu Huang, Khac Minh Dai Vo, Lam Tran.

### Work Cited
- Terencicp. “E-Commerce Dataset by Olist as an SQLite Database.” Kaggle, [2024],
[View Dataset](https://www.kaggle.com/datasets/terencicp/e-commerce-dataset-by-olist-as-an-sqlite-database?select=olist.sqlite)
- Mockaroo. Mockaroo - Random Data Generator. Mockaroo, 2023, [Visit Mockaroo](https://www.mockaroo.com/)
- SimpleMaps. ZIP Code Visualizations. SimpleMaps, 2023, [Visit SimpleMaps](https://simplemaps.com/resources/zip-code-visualizations)
- Adobe. Logo Design Software [Learn More](https://www.adobe.com/products/illustrator/logo-design-software.html)

### Application Design
The tools and libraries used during the development process include the following:
#### Development Tools:
- Python: Primary programming language
- MySQL Workbench: Database management
- PyQt Designer: GUI development
- ERD Plus: ER diagram design
- Visual Studio Code: Code editor and IDE

#### Additional Python Packages:
- Pandas: For data manipulation and analysis
- NumPy: For numerical computations
- Matplotlib: For data visualization
- Seaborn: For advanced statistical visualizations
- PyQt5 and PyQt5-Tools: For building graphical user interfaces
- MySQL Connector for Python: To connect Python with MySQL databases
