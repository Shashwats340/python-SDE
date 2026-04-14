# FastAPI
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home ():
    return {"message": "API is working"}
# now need to run this server using uvicorn in terminal
# python -m uvicorn main:app --reload
# FastAPI automatically generates API docs

# ADD OOP ( bank system  )

class BankCustomer:
    def __init__(self, name: str, balance: float =0):
        self.name = name
        self._balance = balance  # private attribute
    def deposit(self, amount: float):
        self._balance += amount
        return self._balance
    
    def withdraw(self, amount: float):
        if amount > self._balance:
            return "Insufficient funds"
        self._balance -= amount
        return self._balance
    
    # store data ( temporary DB  )
customers = {}
# create API endpoints  
#1. Create customer POST
from pydantic import BaseModel
class CustomerCreate(BaseModel):
    name: str
    balance: float = 0

@app.post("/create")
def create_customer(data: CustomerCreate):
    customer = BankCustomer(data.name, data.balance)
    customers[data.name] = customer
    return {"message": f"{data.name} created"}

# 2. Deposit money POST
class Transaction(BaseModel):
    name: str
    amount: float
@app.post("/deposit")
def deposit_money(data: Transaction):
    customer = customers.get(data.name)
    if not customer:
        return {"error": "Customer not found"}
    new_balance = customer.deposit(data.amount)
    return {"balance": new_balance}

# 3. Withdraw money POST
@app.post("/withdraw")
def withdraw_money(data: Transaction):
    customer = customers.get(data.name)
    if not customer:
        return {"error": "Customer not found"}
    result = customer.withdraw(data.amount)
    return {"result": result}

# 4. Get customer details GET
@app.get("/customer/{name}")
def get_customer(name: str):
    customer = customers.get(name)
    if not customer:
        return {"error": "Customer not found"}
    return {
        "name": customer.name,
        "balance": customer._balance
    }

# 🧪 How to Test (IMPORTANT)
# Go to:
# http://127.0.0.1:8000/docs



# WHAT WE JUST BUILT 
# we created a real backend API with -
# OOP classes
# Json request/response
# Type validation(pydantic)
# API routes 
# In-memory database (dict)