# 🌐 Relational Databases & API Rest Development
A RESTful API built with Flask and SQLAlchemy for managing users, products, and orders with a MySQL database.
 
## Features
 
- **User Management**: Create, read, update, and delete users
- **Product Catalog**: Manage products with pricing
- **Order Management**: Create orders, add/remove products, track order history
- **Data Validation**: Input validation using Marshmallow schemas
- **CORS Enabled**: Cross-origin requests supported
- **Environment Variables**: Secure credential management with `.env`
## Prerequisites
 
- Python 3.7+
- MySQL Server
- Virtual environment (recommended)
## Setup
 
### 1. Clone and Navigate to Project
 
```bash
cd my-ecommerce-api
```
 
### 2. Create Virtual Environment
 
```bash
python3 -m venv venv
```
 
### 3. Activate Virtual Environment
 
**Mac/Linux:**
```bash
source venv/bin/activate
```
 
**Windows:**
```bash
venv\Scripts\activate
```
 
### 4. Install Dependencies
 
```bash
pip install -r requirements.txt
```
 
### 5. Create `.env` File
 
```bash
cp .env.example .env
```
 
Edit `.env` and add your MySQL credentials:
```
DATABASE_URL=mysql+mysqlconnector://root:YOUR_PASSWORD@localhost:3306/ecommerce_api
FLASK_ENV=development
```
 
### 6. Create MySQL Database
 
In MySQL Workbench or command line:
```sql
CREATE DATABASE IF NOT EXISTS ecommerce_api;
```
 
### 7. Run the Application
 
```bash
python app.py
```
 
You should see:
```
 * Running on http://127.0.0.1:5000
```
 
The application will automatically create all tables on startup.
 
---
 
## Database Schema
 
### User Table
```
id (Integer, Primary Key, Auto-increment)
name (String, 100 chars, Required)
address (String, 255 chars, Optional)
email (String, 100 chars, Unique, Required)
```
 
### Product Table
```
id (Integer, Primary Key, Auto-increment)
product_name (String, 100 chars, Required)
price (Float, Required)
```
 
### Order Table
```
id (Integer, Primary Key, Auto-increment)
order_date (DateTime, Default: Current UTC Time, Required)
user_id (Integer, Foreign Key → User, Required)
```
 
### OrderProduct Association Table
```
order_id (Integer, Primary Key, Foreign Key → Order)
product_id (Integer, Primary Key, Foreign Key → Product)
unique_order_product (Unique Constraint: prevents duplicate products in same order)
```
 
---
 
## API Endpoints
 
### User Endpoints
 
#### GET /users
Retrieve all users.
 
**Request:**
```
GET http://localhost:5000/users
```
 
**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "address": "123 Main St"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "address": "456 Oak Ave"
  }
]
```