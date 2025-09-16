from fastapi import FastAPI, HTTPException, Body, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client.assessment_db
employees = db.employees

# Create unique index on employee_id
employees.create_index("employee_id", unique=True)

# JWT settings
SECRET_KEY = "your_very_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Employee(BaseModel):
    employee_id: str
    name: str
    department: str
    salary: float
    joining_date: str
    skills: List[str]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def fake_verify_user(username: str, password: str):
    # Replace with real user verification logic
    return username == "admin" and password == "password"

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not fake_verify_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or expired token")
    return payload["sub"]

@app.get("/")
def home():
    return {"message": "Employee API is working!"}

@app.post("/employees")
def create_employee(employee: Employee = Body(...), user: str = Depends(get_current_user)):
    if employees.find_one({"employee_id": employee.employee_id}):
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    employees.insert_one(employee.dict())
    return {"message": "Employee created successfully"}

@app.get("/employees/avg-salary")
def average_salary():
    pipeline = [
        {
            "$group": {
                "_id": "$department",
                "avg_salary": {"$avg": "$salary"}
            }
        }
    ]
    result = list(employees.aggregate(pipeline))
    return [{"department": r["_id"], "avg_salary": round(r["avg_salary"], 2)} for r in result]

@app.get("/employees/search")
def search_by_skill(skill: str):
    result = employees.find({"skills": skill})
    employees_list = []
    for emp in result:
        emp["_id"] = str(emp["_id"])
        employees_list.append(emp)
    return employees_list

@app.get("/employees")
def list_employees(department: str, skip: int = 0, limit: int = 10):
    result = employees.find({"department": department}).sort("joining_date", -1).skip(skip).limit(limit)
    employees_list = []
    for emp in result:
        emp["_id"] = str(emp["_id"])
        employees_list.append(emp)
    return employees_list

@app.get("/employees/{employee_id}")
def get_employee(employee_id: str):
    employee = employees.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee["_id"] = str(employee["_id"])
    return employee

@app.put("/employees/{employee_id}")
def update_employee(employee_id: str, update_data: dict = Body(...), user: str = Depends(get_current_user)):
    result = employees.update_one({"employee_id": employee_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee updated successfully"}

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: str, user: str = Depends(get_current_user)):
    result = employees.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}
