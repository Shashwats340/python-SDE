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

def demo(*args, **kwargs):
    print ("Args:", args)
    print ("Kwargs:", kwargs)
demo(1, 2, 3, name="shashwat", age = 26)

