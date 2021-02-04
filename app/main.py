from fastapi import FastAPI
from app.functions.helloworld import hello

app = FastAPI(
    title="Fast API Service",
    description="Fast API Service",
    version="0.1"
)

@app.get("/publish")
async def root():
    call = hello()
    return call
