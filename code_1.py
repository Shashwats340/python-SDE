# def add_numbers(*args):
#     print (args)
# add_numbers(1, 2, 3, 4, 5)

# def print_user(**kwargs):
#     print (kwargs)
# print_user(name="shashwat", age = 26 )

# def create_user(**data):
#     return data
# user = create_user(name="shashwat", age = 26, city = "delhi")
# print (user)

# *args + **kwargs

# def demo(*args, **kwargs):
#     print ("Args:", args)
#     print ("Kwargs:", kwargs)
# demo(1, 2, 3, name="shashwat", age = 26)

# lambda function
# short operator used inside a function like map() , filter(), sorted()

# numbers = [1,2,3,4,5,6]
# evens = list(filter(lambda x: x % 2 == 0, numbers) )
# print (evens)

# numbers = [1, 2, 3, 4, 5, 6]

# evens = list(filter(lambda x: x % 2 == 0, numbers))
# print(evens)

# don't overuse lambda fn , use it only when it improves readability and reduces code length.

# optional[int] - values can be int OR None

from gettext import install
from typing import Optional

import pip

def get_age(age: Optional[int]) -> str:
    if age is None :
        return "Age is not provided"
    return f"Age is {age}"                          #formatted string (f-string)
print(get_age(26))
print(get_age(None))

# Union[int, str] - values can be int OR str

# from typing import Union
# def process_id(user_id: Union[int,str]):
#     print(user_id)

# process_id(123)
# process_id("abc123")

#combined example 
# from typing import Optional, Union, List
# def create_product(
#         name: str,
#         price: float,
#         tags: List[str],
#         discount: Optional[int] = None,
#         product_id: Union[int, str] = 0
# ):
#     return {
#         "name": name,
#         "price": price,
#         "tags": tags,
#         "discount": discount,
#         "product_id": product_id
#     }

# cLASS - blueprint / OBJECTS - instance created from that class
# class User:
#    def __init__(self, name, email):
#       self.name = name
#       self.email = email

#    def greet(self):
#       return f"Hello, {self.name}!"      

# user1 = User("shashwat", "shashwat@email.com")

# print(user1.name)
# print(user1.email)
# print(user1.greet())

# concept of inheritance

# class User:
#     def __init__(self, name):
#         self.name = name

#     def greet(self):
#         return f"Hello, {self.name}!"
    
# user1 = User("shashwat")
# print(user1.greet())

#CHILD CLASS
# class Admin(User):
#     def __init__(self, name, role):
#         super().__init__(name)  
    
    
# admin1 = Admin("shashwat", "superadmin")

# POLYMORPHISM - same method name but different implementation in different classes
class User :
    def greet(self):
        return "Hello, User!"
class Admin(User):
    def greet(self):
        return "Hello, Admin!"

u = User()
a = Admin()
print(u.greet())  # Output: Hello, User!
print(a.greet())  # Output: Hello, Admin!

#same method but different output


# WEB DEV CONNEXTION -
# This is EXACTLY how:
# database models work
# API responses are structured
# business logic is organized
# class ContentPost:
#     def __init__(self, title, content):
#         self.title = title
#         self.content = content
    
#     def preview(self):
#         return f"{self.title}: {self.content[:50]}..."  # returns first 50 characters of content
    
# class VideoPost(ContentPost):
#     def __init__(self, title, content, video_url):
#         super().__init__(title, content)
#         self.video_url = video_url

#     def preview(self):
#         return f"WATCH: {self.title} at {self.video_url}"
    
# PRACTICE SOLUTION (BANK SYSTEM )

# Step1: define a base class 
# class BankCustomer:
#     def __init__(self, name, balance=0):
#         self.name = name
#         self._balance = balance  # protected 

#     # Step 2: deposit and withdraw 
#     def deposit(self, amount) -> str:
#         if amount > 0:
#             self._balance += amount 
#             return f"{amount} deposited. New balance: {self._balance}"
#         return "Invalid amount"

#     def withdraw(self, amount):
#         if amount > self._balance:
#             return "Insufficient funds"
#         self._balance -= amount
#         return f"{amount} withdrawn. New balance: {self._balance}"

#     # Step 3: Getter (Encapsulation)
#     @property
#     def balance(self):
#         return self._balance


# # Step 4: Premium Customer (Inheritance)
# class PremiumCustomer(BankCustomer):
#     def __init__(self, name, balance=0, bonus_rate=0.1):
#         super().__init__(name, balance)
#         self.bonus_rate = bonus_rate

#     # override deposit (Polymorphism)
#     def deposit(self, amount):
#         bonus = amount * self.bonus_rate
#         total = amount + bonus
#         self._balance += total
#         return f"{amount} deposited with bonus {bonus}. New balance: {self._balance}"


# # Step 5: Testing
# user1 = BankCustomer("Aman", 1000)
# print(user1.deposit(500))
# print(user1.withdraw(300))
# print(user1.balance)

# premium = PremiumCustomer("Shashwat", 1000)
# print(premium.deposit(500))  # gets bonus
# print(premium.balance)

# common mistakes 
# def deposit(amount):  # wrong
# def deposit(self, amount): # correct - missing self parameter in method definition

# In real backend systems:

# BankCustomer → Model
# deposit() → Business logic
# PremiumCustomer → Specialized behavior

# This is exactly how frameworks like FastAPI + ORMs work

# FAST API 

# pip install fastapi uvicorn - in terminal now working on main.py
