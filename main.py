import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import create_db_and_tables
from routers import songs, audio

app = FastAPI(
    title="Moises Local API",
    description="API for audio stem separation and pitch shifting",
    version="1.0.0"
)

# Ensure storage directory exists
os.makedirs("storage", exist_ok=True)

# Mount static files for audio playback
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Mount static files for frontend
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(songs.router)
app.include_router(audio.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

from fastapi.responses import FileResponse

@app.get("/")
def root():
    return FileResponse("static/index.html")
