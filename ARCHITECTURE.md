# PulsePulse System Architecture

**Product**: PulsePulse — AI Voice & Long-Form Audio Workstation
**Author**: Mander.tech
**Location**: Vancouver / Burnaby, British Columbia, Canada

---

## Architectural Principles

1. **Separation of Concerns & Modularity**: Decouple context processing, speech direction, voice synthesis, job execution, quality analysis, and audio mastering into distinct pipeline stages.
2. **Deterministic & Resilient Generation**: State persistence for long-running queue tasks allowing seamless pause, resume, and failure recovery without re-generating unchanged chunks.
3. **Provider-Agnostic Voice Abstraction**: Uniform interface for voice engines enabling seamless swapping between cloud APIs (e.g. ElevenLabs, Azure Speech) and local open-source models (e.g. Bark, Coqui/XTTS).
4. **Context Awareness**: Long-form narrative continuity achieved through multi-level context retrieval rather than uniform full-text prompt dumping.

---

## Pipeline Data Flow

```
User Input (Text / Script / Script Metadata)
   │
   ▼
1. Project Workspace Component
   │  - Manages chapters, paragraphs, custom voice maps, and pronunciation dictionaries
   ▼
2. Context Engine
   │  - Global Project Context (narrative genre, overall tone, character personas)
   │  - Chapter Context (scene emotional arc, chapter intent)
   │  - Local Context (immediate preceding/following paragraph window)
   ▼
3. Speech Director
   │  - Determines prosody, speaking rate, pitch modulation, and intent classification
   │  - Applies pronunciation & phoneme rules (IPA overrides)
   ▼
4. Voice Engine Adapter Layer
   │  - Routes request to active voice provider / model
   │  - Injects target voice embedding / reference audio
   ▼
5. Generation Queue Manager
   │  - Dispatches parallel or sequential chunk synthesis jobs
   │  - Tracks job progress, retry counters, and persistent job state
   ▼
6. Audio QC & Repair Subsystem
   │  - Peak/RMS loudness normalization
   │  - Artifact detection (clipping, unnatural silences, pops)
   │  - Boundary crossfading & concatenation
   ▼
7. Export & Mastering Engine
   │  - MP3 / WAV / FLAC encoding
   │  - ID3 metadata tagging & stem zip packaging
```

---

## Subsystem Details

### 1. Context Engine
- **Responsibility**: Retains multi-tier semantic context across long-form scripts.
- **Design Decision**: Uniform full-script context injection causes context degradation and high inference costs. The Context Engine utilizes hierarchical context caching (Global -> Chapter -> Local Paragraph) to provide relevant tone and flow directives while keeping token counts bounded.

### 2. Speech Director & Pronunciation Memory
- **Responsibility**: Translates raw text and context directives into structured synthesis instructions.
- **Design Decision**: Manages project-scoped and global IPA dictionaries to resolve acronyms, proper nouns, and dialectal pronunciations before text reaches the TTS engine.

### 3. Voice Engine Abstraction Layer
- **Responsibility**: Encapsulates external cloud API calls and local model execution.
- **Design Decision**: Standardized `VoiceProviderAdapter` interface defining `synthesize()`, `clone_voice()`, and `list_voices()`. Ensures the rest of PulsePulse remains completely independent of specific provider SDKs.

### 4. Generation Queue Manager
- **Responsibility**: Coordinates long-form batch synthesis jobs.
- **Design Decision**: Uses persistent SQLite/PostgreSQL task state backed by job IDs. Supports browser refresh persistence, pause/resume, and targeted paragraph regeneration without invalidating existing audio assets.

### 5. Audio QC & Repair
- **Responsibility**: Ensures professional output standards across concatenated audio segments.
- **Design Decision**: Performs waveform analysis to detect digital clipping, silence gaps exceeding thresholds, and sudden volume transitions. Applies automated equalization and crossfading at sentence boundaries.

### 6. Export System
- **Responsibility**: Formats and packages output assets for distribution.
- **Design Decision**: Exports multi-chapter audiobooks with proper cue markers, LUFS loudness standards (-16 LUFS for podcasts/audiobooks), and metadata tagging.

---

## Reliability & Error Handling Strategy

- **Retry with Exponential Backoff**: Transient provider API rate limits or network drops automatically retry up to 3 times before placing job in `FAILED_RECOVERABLE` state.
- **Chunk Recovery**: If long-form generation is interrupted, processing resumes from the exact failed paragraph chunk.
- **Sanitization & Validation**: Input scripts are sanitized for unsupported control characters prior to enqueueing.
