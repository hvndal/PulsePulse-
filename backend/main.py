from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os

from backend.models import (
    Project, Chapter, Paragraph, VoiceProfile, PronunciationRule,
    QueueJob, ExportRequest, JobStatus, ExportFormat
)
from backend.context_engine import ContextEngine
from backend.pronunciation import PronunciationEngine
from backend.voice_engine import VoiceEngine
from backend.queue_manager import QueueManager
from backend.audio_qc import AudioQCEngine
from backend.exporter import Exporter

app = FastAPI(
    title="PulsePulse AI Voice Workstation API",
    description="Backend API for Mander.tech PulsePulse long-form audio workstation",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store initialized with sample project
voice_engine = VoiceEngine()
context_engine = ContextEngine()
pronunciation_engine = PronunciationEngine()
queue_manager = QueueManager()
audio_qc = AudioQCEngine()
exporter = Exporter()

projects_db: dict[str, Project] = {}
pronunciation_rules_db: list[PronunciationRule] = []
generated_audio_cache: dict[str, bytes] = {}  # paragraph_id -> wav bytes

# Initialize default demo project
demo_voice = voice_engine.get_available_voices()[0]
demo_project = Project(
    title="The Golden Hour — Chapter 1",
    author="Mander.tech Narratives",
    description="A long-form audio drama demonstrating PulsePulse context intelligence and voice cloning.",
    genre="Dramatic Narration",
    default_voice_id=demo_voice.id,
    chapters=[
        Chapter(
            project_id="demo-1",
            order=1,
            title="Chapter 1: The First Signal",
            summary="Introductory scene setting up the narrative arc in Burnaby Mountain observatory.",
            paragraphs=[
                Paragraph(
                    chapter_id="c1",
                    order=1,
                    text="The autumn dusk settled quietly over Burnaby Mountain as the telemetry instruments calibrated.",
                    voice_id=demo_voice.id
                ),
                Paragraph(
                    chapter_id="c1",
                    order=2,
                    text="Suddenly, an unusual frequency spike pulsed through the primary receiver array!",
                    voice_id=demo_voice.id
                ),
                Paragraph(
                    chapter_id="c1",
                    order=3,
                    text="Dr. Vance adjusted the equalizer knob, leaning in closer to the monitor. Could this be the signal?",
                    voice_id=demo_voice.id
                )
            ]
        )
    ]
)
projects_db[demo_project.id] = demo_project

# API Routes

@app.get("/api/voices", response_model=List[VoiceProfile])
def get_voices():
    return voice_engine.get_available_voices()

@app.get("/api/projects", response_model=List[Project])
def list_projects():
    return list(projects_db.values())

@app.post("/api/projects", response_model=Project)
def create_project(project: Project):
    projects_db[project.id] = project
    return project

@app.get("/api/projects/{project_id}", response_model=Project)
def get_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_id]

@app.post("/api/projects/{project_id}/generate-paragraph/{paragraph_id}")
def generate_paragraph_audio(project_id: str, paragraph_id: str):
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    target_para = None
    target_chapter = None
    target_idx = -1
    for chapter in project.chapters:
        for idx, para in enumerate(chapter.paragraphs):
            if para.id == paragraph_id:
                target_para = para
                target_chapter = chapter
                target_idx = idx
                break

    if not target_para or not target_chapter:
        raise HTTPException(status_code=404, detail="Paragraph not found")

    # Fetch context window
    ctx_info = context_engine.get_paragraph_context_window(target_chapter, target_idx)
    target_para.context_notes = f"{ctx_info["pacing_directive"]} | {ctx_info["emotion_directive"]}"

    # Apply pronunciation rules
    pr_text = pronunciation_engine.apply_rules(target_para.text, pronunciation_rules_db)

    # Voice lookup
    v_id = target_para.voice_id or project.default_voice_id or demo_voice.id
    voice = next((v for v in voice_engine.get_available_voices() if v.id == v_id), demo_voice)

    # Synthesize
    wav_bytes = voice_engine.synthesize(pr_text, voice)
    normalized_wav, qc_info = audio_qc.analyze_and_normalize(wav_bytes)

    # Cache audio
    generated_audio_cache[paragraph_id] = normalized_wav
    target_para.status = "ready"
    target_para.audio_url = f"/api/audio/{paragraph_id}.wav"
    target_para.duration_seconds = qc_info["duration_seconds"]
    target_para.peak_db = qc_info["final_peak_db"]
    target_para.detected_clipping = qc_info["clipping_detected"]

    return {
        "status": "success",
        "paragraph_id": paragraph_id,
        "audio_url": target_para.audio_url,
        "duration_seconds": target_para.duration_seconds,
        "context_notes": target_para.context_notes,
        "qc_report": qc_info
    }

@app.get("/api/audio/{paragraph_id}.wav")
def get_audio_file(paragraph_id: str):
    if paragraph_id not in generated_audio_cache:
        # Generate on the fly if missing
        wav = voice_engine.synthesize("Audio preview segment generated by PulsePulse workstation.", demo_voice)
        generated_audio_cache[paragraph_id] = wav

    return Response(content=generated_audio_cache[paragraph_id], media_type="audio/wav")

@app.get("/api/pronunciation", response_model=List[PronunciationRule])
def list_pronunciation_rules():
    return pronunciation_rules_db

@app.post("/api/pronunciation", response_model=PronunciationRule)
def add_pronunciation_rule(rule: PronunciationRule):
    pronunciation_rules_db.append(rule)
    return rule

@app.get("/api/queue", response_model=List[QueueJob])
def list_queue():
    return queue_manager.list_jobs()

@app.post("/api/export")
def export_project(req: ExportRequest):
    project = projects_db.get(req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Gather paragraph WAVs
    wavs = []
    stems = []
    for c in project.chapters:
        for p in c.paragraphs:
            if p.id in generated_audio_cache:
                wav = generated_audio_cache[p.id]
            else:
                wav = voice_engine.synthesize(p.text, demo_voice)
                generated_audio_cache[p.id] = wav
            wavs.append(wav)
            stems.append((f"{c.title}_p{p.order}.wav", wav))

    if req.format == ExportFormat.ZIP_STEMS:
        zip_bytes = exporter.create_stem_zip(stems)
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={project.title}_stems.zip"}
        )
    else:
        mastered_wav = exporter.concatenate_wav_chunks(wavs)
        return Response(
            content=mastered_wav,
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={project.title}_master.wav"}
        )
