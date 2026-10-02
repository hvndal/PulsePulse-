from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import time
import uuid

class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class VoiceProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    gender: VoiceGender = VoiceGender.NEUTRAL
    provider: str = "PulseEngine Native"
    sample_rate: int = 24000
    description: str = ""
    pitch_offset: float = 0.0  # semitones (-12 to +12)
    speed_factor: float = 1.0  # multiplier (0.5 to 2.0)
    emotion_strength: float = 0.5  # 0.0 to 1.0

class ParagraphStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"

class Paragraph(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chapter_id: str
    order: int
    text: str
    voice_id: Optional[str] = None
    status: ParagraphStatus = ParagraphStatus.PENDING
    audio_url: Optional[str] = None
    duration_seconds: float = 0.0
    detected_clipping: bool = False
    peak_db: float = -6.0
    context_notes: Optional[str] = None

class Chapter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    order: int
    title: str
    summary: Optional[str] = ""
    paragraphs: List[Paragraph] = []

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    author: str = "Mander.tech"
    description: str = ""
    genre: str = "Narration / Audiobook"
    default_voice_id: Optional[str] = None
    chapters: List[Chapter] = []
    created_at: float = Field(default_factory=time.time)

class PronunciationRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[str] = None  # None = Global Rule
    original_word: str
    replacement_phonetic: str
    is_ipa: bool = False
    notes: Optional[str] = ""

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"

class QueueJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    chapter_id: Optional[str] = None
    paragraph_id: Optional[str] = None
    status: JobStatus = JobStatus.QUEUED
    progress_percentage: float = 0.0
    current_item: str = ""
    error_message: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

class ExportFormat(str, Enum):
    WAV = "wav"
    MP3 = "mp3"
    ZIP_STEMS = "zip_stems"

class ExportRequest(BaseModel):
    project_id: str
    chapter_id: Optional[str] = None
    format: ExportFormat = ExportFormat.WAV
    normalize_lufs: bool = True
    target_lufs: float = -16.0
