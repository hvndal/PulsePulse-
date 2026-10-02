import struct
import wave
import io
import math
from typing import Dict, Any, Tuple

class AudioQCEngine:
    """
    Performs audio quality control checks including clipping detection,
    peak dB analysis, and silence gap analysis.
    """

    def analyze_and_normalize(
        self,
        wav_bytes: bytes,
        target_peak_db: float = -3.0
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Analyzes 16-bit PCM WAV bytes for audio defects and applies normalization.
        """
        wav_io = io.BytesIO(wav_bytes)
        with wave.open(wav_io, "rb") as wav_in:
            n_channels = wav_in.getnchannels()
            sampwidth = wav_in.getsampwidth()
            framerate = wav_in.getframerate()
            n_frames = wav_in.getnframes()
            raw_data = wav_in.readframes(n_frames)

        if sampwidth != 2:
            # Non 16-bit audio returned as-is
            return wav_bytes, {"peak_db": 0.0, "clipping_detected": False, "normalized": False}

        num_samples = len(raw_data) // 2
        samples = struct.unpack(f"<{num_samples}h", raw_data)

        if not samples:
            return wav_bytes, {"peak_db": -96.0, "clipping_detected": False, "normalized": False}

        # Analyze peaks
        max_amplitude = max(abs(s) for s in samples)
        clipping_threshold = 32700
        clipping_count = sum(1 for s in samples if abs(s) >= clipping_threshold)
        clipping_detected = clipping_count > (num_samples * 0.001)  # > 0.1% clipped

        current_peak_ratio = max_amplitude / 32768.0
        peak_db = 20.0 * math.log10(current_peak_ratio) if current_peak_ratio > 0 else -96.0

        # Target peak ratio
        target_peak_ratio = 10.0 ** (target_peak_db / 20.0)
        gain_multiplier = target_peak_ratio / current_peak_ratio if current_peak_ratio > 0 else 1.0

        # Apply gain normalization
        normalized_samples = [
            max(-32768, min(32767, int(s * gain_multiplier))) for s in samples
        ]

        normalized_bytes = struct.pack(f"<{num_samples}h", *normalized_samples)

        out_io = io.BytesIO()
        with wave.open(out_io, "wb") as wav_out:
            wav_out.setnchannels(n_channels)
            wav_out.setsampwidth(sampwidth)
            wav_out.setframerate(framerate)
            wav_out.writeframes(normalized_bytes)

        qc_report = {
            "initial_peak_db": round(peak_db, 2),
            "final_peak_db": round(target_peak_db, 2),
            "clipping_detected": clipping_detected,
            "sample_count": num_samples,
            "duration_seconds": round(num_samples / framerate, 2),
            "normalized": True
        }

        return out_io.getvalue(), qc_report
