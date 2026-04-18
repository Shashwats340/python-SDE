from fastapi import FastAPI
from typing import Optional

app = FastAPI()
# create a backend server for my main application 
#fake database - a list of dictionaries , each dictionary represent one product


products = [
    {"id": 1, "name": "Shirt", "price": 500, "category": "fashion"},
    {"id": 2, "name": "Laptop", "price": 50000, "category": "electronics"},
    {"id": 3, "name": "Shoes", "price": 2000, "category": "fashion"},
    {"id": 4, "name": "Headphones", "price": 3000, "category": "electronics"},

]

@app.get("/products")  # @app.get is a decorator that creates an api endpoint ; /products - URL route ; category: str - query parameter
def get_products(category: Optional[str] = None):
    if category:
        return [p for p in products if p["category"] == category]
    return products
# for p in products → loop through all products
# if p["category"] == category → check condition
# [ ... ] → create a new list

@app.get("/products/filter")
def filter_products(min_price: int, max_price: int):
    filtered = [p for p in products if min_price <= p["price"] <= max_price]
    return filtered
#returns products between given price range 

#optional filters - value can exist OR be none 
@app.get("/products/search")
def search_products(
    category: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None
):
    result = products
    if category is not None:
        result = [p for p in result if p["category"] == category]

    if min_price is not None and max_price is not None:
        result = [p for p in result if min_price <= p["price"] <= max_price]

    

    return result
# search products with optional filters - category and price range
#continued tom 
#apis are a way for different software applications to communicate with each other. They allow one application to access the functionality or data of another application in a standardized way. In the context of web development, APIs are often used to create endpoints that can be accessed over the internet, allowing clients (like web browsers or mobile apps) to interact with a server and perform actions like retrieving data, creating new records, updating existing records, or deleting records.s

    

