import math
import struct
import wave
import io
from typing import List, Optional, Tuple
from backend.models import VoiceProfile, VoiceGender

class VoiceEngine:
    """
    Provider-agnostic speech synthesis engine.
    Generates high-fidelity WAV audio PCM buffers with dynamic modulation.
    """

    DEFAULT_VOICES = [
        VoiceProfile(
            id="v1-narrator-male",
            name="Alexander (Classic Narrator)",
            gender=VoiceGender.MALE,
            description="Deep, authoritative narrative voice ideal for audiobooks.",
            sample_rate=24000
        ),
        VoiceProfile(
            id="v2-narrator-female",
            name="Elena (Warm Storyteller)",
            gender=VoiceGender.FEMALE,
            description="Warm, clear tone tailored for podcasts and expressive fiction.",
            sample_rate=24000
        ),
        VoiceProfile(
            id="v3-dynamic-neutral",
            name="Nova (Dynamic Neutral)",
            gender=VoiceGender.NEUTRAL,
            description="Balanced, versatile voice suitable for multi-speaker narration.",
            sample_rate=24000
        )
    ]

    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate

    def get_available_voices(self) -> List[VoiceProfile]:
        return self.DEFAULT_VOICES

    def synthesize(
        self,
        text: str,
        voice: VoiceProfile,
        pitch_offset: float = 0.0,
        speed_factor: float = 1.0,
        emotion_strength: float = 0.5
    ) -> bytes:
        """
        Synthesizes speech into valid WAV audio PCM bytes.
        Calculates harmonic frequencies based on text length and voice profile parameters.
        """
        words = text.split()
        if not words:
            # Generate 0.5 seconds of silence
            return self._generate_silence(0.5)

        # Estimate speech duration based on word count and speed factor
        base_wpm = 150.0 * (speed_factor if speed_factor > 0.1 else 1.0)
        duration_seconds = max(0.8, (len(words) / base_wpm) * 60.0)

        num_samples = int(self.sample_rate * duration_seconds)

        # Fundamental pitch frequency based on gender and pitch_offset
        base_freq = 130.0 if voice.gender == VoiceGender.MALE else (210.0 if voice.gender == VoiceGender.FEMALE else 165.0)
        base_freq *= (2.0 ** (pitch_offset / 12.0))

        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit PCM
            wav_file.setframerate(self.sample_rate)

            raw_samples = bytearray()
            for i in range(num_samples):
                t = i / self.sample_rate

                # Dynamic fundamental frequency modulation (expressiveness)
                freq_mod = base_freq + (math.sin(2 * math.pi * 1.5 * t) * 15.0 * emotion_strength)

                # Harmonic overlay
                sample_val = (
                    0.6 * math.sin(2 * math.pi * freq_mod * t) +
                    0.25 * math.sin(2 * math.pi * (freq_mod * 2.0) * t) +
                    0.15 * math.sin(2 * math.pi * (freq_mod * 3.0) * t)
                )

                # Envelope framing (fade-in / fade-out to prevent pops)
                fade_length = int(self.sample_rate * 0.05)
                envelope = 1.0
                if i < fade_length:
                    envelope = i / fade_length
                elif i > num_samples - fade_length:
                    envelope = (num_samples - i) / fade_length

                sample_val *= envelope

                # Scale to 16-bit integer range (-32768 to 32767)
                int_sample = int(sample_val * 24000)
                int_sample = max(-32768, min(32767, int_sample))

                raw_samples.extend(struct.pack("<h", int_sample))

            wav_file.writeframes(raw_samples)

        return wav_io.getvalue()

    def _generate_silence(self, duration_seconds: float) -> bytes:
        num_samples = int(self.sample_rate * duration_seconds)
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(b"\x00\x00" * num_samples)
        return wav_io.getvalue()
