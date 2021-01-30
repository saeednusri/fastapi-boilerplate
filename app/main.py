from fastapi import FastAPI
from app.trading.hqm import gethqm

app = FastAPI(
    title="Algorithmic Trading",
    description="App to pull daily HQM",
    version="0.1"
)

@app.post("/publish")
async def root():
    gethqm()
    return "Success!"