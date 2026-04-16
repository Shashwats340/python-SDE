from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

todos =[]

class Todo(BaseModel):
    title: str
    completed: bool = False

#create todo
@app.post("/todos")
def create_todo(todo: Todo):
    todos.append(todo)
    return {"message": "Todo added"}

# here @ is the decorator. its a way to " wrap " the function below it and give extra powers #get all todos
#app this refers to your fastAPI application instance usually created earlier in the code with app = FastAPI() .get() is a method provided by FastAPI to define a GET endpoint. It takes the path of the endpoint as an argument in this case "/todos" and the function get_todos() will be called whenever a GET request is made to that endpoint.
# .get this tells fastAPI that this specific function should only respond to HTTP GET requests. It is a standard method used when you want to read or retrieve data from the server
# def is the standard python keyword to define a function 

@app.get("/todos")
def get_todos():
    return todos

# create todo
@app.post ("/todos")
def create_todo(todo: Todo):
    todos.append(todo)
    return {"message": "Todo added"}

#get all todos
@app.get("/todos")
def get_todos():
    return todos

#delete todo (by index)

@app.delete("/todos/{index}")
def delete_todo(index: int):
    if index >= len(todos):
        return {"error": "Invalid index"}
    
    todos.pop(index)
    return {"message": "Deleted"}

# what PUT does - update existing resource ( by index )
@app.put("/todos/{index}")
def update_todo(index: int, updated_todo: Todo):
    # check if index is valid
    if index >= len(todos):
        return {"error": "Invalid index"}

    # update the todo
    todos[index] = updated_todo

    return {
        "message": "Todo updated",
        "todo": updated_todo
    }
# continue ---