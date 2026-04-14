from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.routes.businesses import router as businesses_router

app = FastAPI(
    title="Marketplace API",
    description="A digital marketplace for local service businesses.",
    version="0.1.0",
)

os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(businesses_router)

@app.get("/", tags=["health"])
def root():
    """Health check — confirms the API is alive."""
    return {"status": "ok", "message": "Marketplace API is running"}