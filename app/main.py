from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="ml_service")

@app.get("/")
async def root():
    return {"message": "Hello gng"}



