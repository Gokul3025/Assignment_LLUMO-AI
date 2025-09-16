This project is a RESTful Employee Management API built using FastAPI and MongoDB. It supports CRUD operations on employee data with secure endpoints protected by JWT authentication.

Features
Create, read, update, and delete employees

List employees with pagination support

Search employees by skill

Get average salary by department (aggregation)

JWT-based authentication for protected routes

Swagger UI interactive API docs

Installation
Clone or download the project files.

Install Python dependencies:

bash
pip install -r requirements.txt
Ensure MongoDB is running locally on default port (mongodb://localhost:27017).

Running the Application
Start the FastAPI server with:

bash
python -m uvicorn main:app --reload
API will be available at:
http://127.0.0.1:8000

Authentication
Obtain JWT token by POST request to /token with form data:

username: admin

password: password

Use the returned token to authorize protected endpoints in Swagger UI (Authorize button) or include as Bearer token in request headers.

Usage
Access Swagger UI for API documentation and testing:
http://127.0.0.1:8000/docs

SURA GOKUL,
gokulsura2505@gmail.com


