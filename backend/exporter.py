import zipfile
import io
import wave
from typing import List, Tuple, Dict, Any
from backend.audio_qc import AudioQCEngine

class Exporter:
    """
    Generates single-track mastered WAV audio files and multi-track ZIP stem bundles.
    """

    def __init__(self):
        self.qc = AudioQCEngine()

    def concatenate_wav_chunks(self, wav_chunks: List[bytes], crossfade_ms: int = 50) -> bytes:
        """
        Concatenates multiple WAV audio chunks into a seamless single master track.
        """
        if not wav_chunks:
            return b""

        if len(wav_chunks) == 1:
            mastered, _ = self.qc.analyze_and_normalize(wav_chunks[0])
            return mastered

        # Read samples from all chunks
        all_samples = []
        sample_rate = 24000
        channels = 1
        sampwidth = 2

        for chunk in wav_chunks:
            wav_io = io.BytesIO(chunk)
            with wave.open(wav_io, "rb") as w:
                sample_rate = w.getframerate()
                channels = w.getnchannels()
                sampwidth = w.getsampwidth()
                raw = w.readframes(w.getnframes())
                import struct
                num_s = len(raw) // 2
                all_samples.extend(struct.unpack(f"<{num_s}h", raw))

        import struct
        packed_bytes = struct.pack(f"<{len(all_samples)}h", *all_samples)

        out_io = io.BytesIO()
        with wave.open(out_io, "wb") as wav_out:
            wav_out.setnchannels(channels)
            wav_out.setsampwidth(sampwidth)
            wav_out.setframerate(sample_rate)
            wav_out.writeframes(packed_bytes)

        mastered, _ = self.qc.analyze_and_normalize(out_io.getvalue())
        return mastered

    def create_stem_zip(self, paragraph_audios: List[Tuple[str, bytes]]) -> bytes:
        """
        Packages individual paragraph WAV audio stems into a structured ZIP archive.
        """
        zip_io = io.BytesIO()
        with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, wav_data in paragraph_audios:
                zf.writestr(filename, wav_data)
        return zip_io.getvalue()
