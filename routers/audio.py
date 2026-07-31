from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from database import get_session
from models import Song
from services.audio_service import apply_pitch_shift

router = APIRouter(prefix="/api/songs", tags=["audio"])

@router.post("/{song_id}/pitch-shift")
def pitch_shift(
    song_id: str,
    semitones: int = Query(..., description="Number of semitones to shift (e.g., +2, -3)"),
    stem: str = Query("all", description="Stem to process: 'vocals', 'drums', 'bass', 'other', or 'all'"),
    session: Session = Depends(get_session)
):
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
        
    if stem != "all" and not song.has_stems:
        raise HTTPException(status_code=400, detail="Stems are not ready yet or processing failed")

    valid_stems = ["all", "vocals", "drums", "bass", "other"]
    if stem not in valid_stems:
        raise HTTPException(status_code=400, detail=f"Invalid stem. Must be one of {valid_stems}")

    try:
        file_url = apply_pitch_shift(song_id, semitones, stem)
        return {"message": "Pitch shift successful", "url": file_url}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
