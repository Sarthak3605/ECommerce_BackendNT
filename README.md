# E-Commerce Backend System (FastAPI)

This is a complete E-commerce Backend API built using **FastAPI**, **SQLAlchemy**, and **JWT Authentication**, featuring full modular architecture, logging, error handling, and role-based access control.

## Tech Stack
- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (OAuth2)
- **Logging**: Python `logging` module
- **Email**: BackgroundTasks + SMTP
- **API Docs**: Swagger (via FastAPI)
- **Server **: Uvicorn

## Features
-  User Signup, Login (JWT Token)
-  Role-Based Access: Admin, User
-  Product CRUD (Admin)
-  Add to Cart / Remove / View Cart
-  Checkout (COD / Online)
-  Order History + Details
-  Password Reset via Email
-  Logging of all API activity
-  Token-Based Security
-  Error Handling with HTTP codes

## Project Structure
<pre> ``` ecommerce-backend/ │ ├─ app/ │ ├─ auth/ # Signup, Login, Token, Password Reset │ ├─ cart/ # Cart APIs │ ├─ orders/ # Checkout, Order History │ ├─ products/ # Admin Product CRUD │ ├─ core/ # DB, Config, Logging, Email │ └─ main.py # FastAPI app entry point │ ├─ requirements.txt # Python dependencies ├─ README.md # Project documentation └─ .gitignore # Git ignore rules ``` </pre>

##  Authentication & Authorization

- **JWT Tokens** issued at `/auth/signin`
- Roles: `admin`, `user`
- Protected routes require `Authorization: Bearer <token>`
- Passwords are hashed using **bcrypt**

## Postman Collection of API Endpoints :
https://sarthak-5690584.postman.co/workspace/Sarthak's-Workspace~4441b7fc-4b4f-4f5a-8632-423fd5a9953c/collection/45892851-f2e558e9-c632-4632-9c93-a212a53d5968?action=share&source=copy-link&creator=45892851

## Setup Instructions
# 1. Clone the project
git clone https://github.com/Sarthak3605/ECommerce_BackendNT
cd Python_Product

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (e.g. SECRET_KEY, SMTP config)

# 5. Run the app
uvicorn app.main:app –reload
#6. Then to use Swagger UI just add /doc at the end of localhost
