# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status


app = FastAPI(
    title="cloud-storage-app",
    version="0.1.0",
)

# Incluir os roteadores da API
# app.include_router(users_router.router, prefix="/api/v1")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "API está no online!"}