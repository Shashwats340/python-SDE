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

from typing import Optional

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


