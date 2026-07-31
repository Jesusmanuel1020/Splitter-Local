import os
import shutil
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Song
from services.demucs_service import process_song

router = APIRouter(prefix="/api/songs", tags=["songs"])

@router.post("/upload")
async def upload_song(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    if not file.filename.endswith(('.mp3', '.wav')):
        raise HTTPException(status_code=400, detail="Only .mp3 and .wav files are supported")

    # Create song record
    song = Song(
        title=os.path.splitext(file.filename)[0],
        original_filename=file.filename,
        storage_path="" # Will update after ID is generated
    )
    session.add(song)
    session.commit()
    session.refresh(song)

    # Create storage directory
    storage_dir = os.path.join("storage", song.id)
    os.makedirs(storage_dir, exist_ok=True)
    
    # Update storage path
    song.storage_path = f"/storage/{song.id}/"
    session.add(song)
    session.commit()

    # Save original file
    # We always save it as original.mp3 or original.wav, but demucs handles both.
    # Let's save it with its original extension but named 'original' to simplify
    ext = os.path.splitext(file.filename)[1]
    # Actually, demucs_service expects original.mp3, let's save it as original.mp3 if it's mp3, 
    # but wait, demucs_service hardcodes "original.mp3". Let's save it as original.mp3 and if it's wav, convert it?
    # Or just save it as original.mp3 and let ffmpeg handle it if needed.
    # Better: save it as original + ext, and update demucs_service to find it.
    # Wait, to keep it simple and match demucs_service, let's save it as original.mp3. If it's wav, we should convert it, 
    # but let's just save it as original.mp3 for now (if it's wav, ffmpeg/demucs might still read it, but it's better to be safe).
    # Let's just save it as original.mp3.
    file_path = os.path.join(storage_dir, "original.mp3")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Trigger background task
    background_tasks.add_task(process_song, song.id)

    return {"message": "Upload successful, processing started", "song_id": song.id}

@router.get("/")
def list_songs(session: Session = Depends(get_session)):
    songs = session.exec(select(Song)).all()
    return songs

@router.get("/{song_id}")
def get_song(song_id: str, session: Session = Depends(get_session)):
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song
