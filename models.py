from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
import uuid

class Song(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    original_filename: str
    bpm: Optional[float] = None
    status: str = Field(default="pending") # "pending", "processing", "completed", "error"
    progress: int = Field(default=0) # 0 to 100
    created_at: datetime = Field(default_factory=datetime.utcnow)
    storage_path: str
    has_stems: bool = Field(default=False)
