# FastAPI
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home ():
    return {"message": "API is working"}
# now need to run this server using uvicorn in terminal
# uvicorn main:app --reload
