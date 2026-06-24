from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import upload, generate, export

app = FastAPI(
    title="SoalAdaptif ID API",
    description="Automatic Question Generation untuk Bahasa Indonesia",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route API
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generate"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

# Health Check
@app.get("/")
async def root():
    return {
        "message": "SoalAdaptif ID API Running",
        "docs": "/docs"
    }