# app/main.py
from fastapi import FastAPI
from app.api.v1 import users_router

app = FastAPI(
    title="",
    version="0.1.0",
)

# Incluir os roteadores da API
app.include_router(users_router.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "API está no ar!"}