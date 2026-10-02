# PulsePulse
### AI Voice & Long-Form Audio Workstation

**Developed by Mander.tech**
*Vancouver / Burnaby, British Columbia, Canada*

---

## Product Overview

**PulsePulse** is a professional-grade AI voice workstation designed for high-fidelity audio production, voice cloning, and long-form speech synthesis. Built to support multi-chapter audiobooks, voiceovers, podcasts, and localized narrative production, PulsePulse combines contextual speech understanding with fine-grained audio quality control and deterministic queue execution.

Unlike simple text-to-speech (TTS) interfaces, PulsePulse treats long-form audio generation as an integrated engineering workflow—maintaining cross-paragraph voice consistency, semantic pacing, custom pronunciation rules, and automated audio repair.

---

## Core Capabilities

- **Context Intelligence Engine**: Hierarchical context awareness (global project, chapter-level, and neighboring paragraph context) ensuring consistent tone, pacing, and dynamic delivery across multi-hour audio projects.
- **High-Fidelity Voice Cloning**: Few-shot speaker cloning with zero-shot adaptation, fine-tuned pitch matching, and provider-agnostic voice embedding management.
- **Long-Form Generation Workflow**: Chunked speech synthesis with automated sentence boundary alignment and smooth transition crossfading.
- **Pronunciation & Phoneme Memory**: Project-scoped and global pronunciation dictionaries using IPA (International Phonetic Alphabet) and custom phonetic overrides.
- **Resilient Generation Queue**: State-persistent generation queue with pause, resume, selective paragraph regeneration, and failure-recovery mechanisms.
- **Audio QC & Repair**: Automated audio quality checks for clipping, baseline noise, unnatural pauses, and speech artifact detection.
- **Multi-Format Export System**: Flexible export pipelines supporting MP3, WAV, FLAC, single-track chapter mastering, and stem-separated zip archives.

---

## Architecture Overview

PulsePulse follows a modular, decoupled pipeline architecture where text content passes through contextual enrichment, speech direction, voice synthesis, queue scheduling, quality control, and export mastering:

```
User Input
   │
   ▼
Project Workspace
   │
   ▼
Context Engine (Global / Chapter / Paragraph Analysis)
   │
   ▼
Speech Director (Prosody & Intent Classification)
   │
   ▼
Voice Engine (Cloning & Provider-Agnostic TTS Synthesis)
   │
   ▼
Generation Queue (Job Scheduling & Resumable Tasks)
   │
   ▼
Audio QC & Repair (Artifact Detection & Level Normalization)
   │
   ▼
Export System (Mastering & Multi-Format Rendering)
```

For detailed architectural specifications and design rationale, see [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## Subsystems

### Context Intelligence
Maintains global narrative context, character voice mappings, chapter emotional arcs, and local paragraph flow to prevent tone drift during batch generation.

### Voice Cloning & Synthesis
Provides a uniform abstraction layer over voice providers (e.g., ElevenLabs, Bark, Coqui/XTTS, Azure Speech), enabling seamlessly swapped backends and local neural synthesis.

### Pronunciation System
Allows creators to manage custom dictionaries, acronym expansions, and explicit IPA phoneme overrides across projects.

### Generation Queue
Executes non-blocking background rendering with persistent job state, enabling browser refreshes and recovery from network interruptions.

### Audio QC & Repair
Analyzes generated waveforms for silent gaps, plosives, digital clipping, and pacing anomalies, offering automated level adjustments and targeted paragraph regeneration.

### Export System
Handles chapter-level mastering, metadata tagging (ID3v2), peak/RMS loudness normalization (LUFS targeting), and archive bundling.

---

## Technology Stack

- **Frontend / UI**: React, TypeScript, Tailwind CSS, Web Audio API / WaveSurfer.js
- **Backend API**: Python / FastAPI, Pydantic, AsyncIO
- **Audio Processing**: FFmpeg, SoundFile, Librosa, PyTorch (for neural synthesis inference)
- **State & Queue**: SQLite / PostgreSQL, Redis / Persistent Queue state
- **Voice Providers**: Modular adapter pattern supporting cloud APIs and local ONNX/PyTorch TTS models

---

## Development Setup

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- `ffmpeg` installed and available in system PATH

### Installation & Local Execution

1. **Clone repository and set up environment:**
   See project documentation for configuring virtual environments and node dependencies.

2. **Starting API Server:**
   Launch backend service with fast API server runner.

3. **Starting Frontend Interface:**
   Launch web application client interface.

---

## Testing

Run unit and integration test suites as configured in backend and frontend package manifests.

---

## Roadmap

- [x] Initial core synthesis and workstation architecture (`v0.1.0`)
- [ ] Voice cloning pipeline with speaker embeddings (`v0.2.0`)
- [ ] Long-form audio queueing and chunk recovery (`v0.3.0`)
- [ ] Hierarchical context intelligence engine (`v0.4.0`)
- [ ] Production export mastering and multi-track stems (`v0.5.0`)

---

## License & Credits

Developed by **Mander.tech**
Vancouver / Burnaby, British Columbia, Canada
*All rights reserved.*
