from fastapi import FastAPI
from check import auth_check
app = FastAPI()



@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "Welcome to FastAPI!"}

app.include_router(auth_check)
