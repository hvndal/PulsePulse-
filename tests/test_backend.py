import unittest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import Project, Chapter, Paragraph, VoiceProfile, PronunciationRule
from backend.context_engine import ContextEngine
from backend.pronunciation import PronunciationEngine
from backend.voice_engine import VoiceEngine
from backend.queue_manager import QueueManager
from backend.audio_qc import AudioQCEngine
from backend.exporter import Exporter

class TestPulsePulseBackend(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_api_get_voices(self):
        response = self.client.get("/api/voices")
        self.assertEqual(response.status_code, 200)
        voices = response.json()
        self.assertGreaterEqual(len(voices), 3)
        self.assertEqual(voices[0]["id"], "v1-narrator-male")

    def test_api_get_projects(self):
        response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, 200)
        projects = response.json()
        self.assertGreaterEqual(len(projects), 1)

    def test_context_engine_analysis(self):
        engine = ContextEngine()
        project = Project(title="Test Project", author="Mander.tech", chapters=[
            Chapter(project_id="p1", order=1, title="Ch1", paragraphs=[
                Paragraph(chapter_id="c1", order=1, text="Hello world!"),
                Paragraph(chapter_id="c1", order=2, text="How are you doing today?")
            ])
        ])

        ctx = engine.get_paragraph_context_window(project.chapters[0], 0)
        self.assertEqual(ctx["paragraph_id"], project.chapters[0].paragraphs[0].id)
        self.assertIn("preceding_context", ctx)
        self.assertIn("following_context", ctx)

    def test_pronunciation_engine(self):
        engine = PronunciationEngine(global_rules=[
            PronunciationRule(original_word="Mander", replacement_phonetic="MAN-der")
        ])
        res = engine.apply_rules("Welcome to Mander.tech audio suite.")
        self.assertIn("MAN-der", res)

    def test_voice_engine_synthesis(self):
        engine = VoiceEngine()
        voice = engine.get_available_voices()[0]
        wav_bytes = engine.synthesize("Testing voice synthesis output.", voice)
        self.assertGreater(len(wav_bytes), 44)
        self.assertEqual(wav_bytes[:4], b"RIFF")

    def test_audio_qc_normalization(self):
        qc = AudioQCEngine()
        engine = VoiceEngine()
        voice = engine.get_available_voices()[0]
        wav_bytes = engine.synthesize("QC normalization test.", voice)

        normalized, report = qc.analyze_and_normalize(wav_bytes, target_peak_db=-3.0)
        self.assertTrue(report["normalized"])
        self.assertEqual(report["final_peak_db"], -3.0)

    def test_exporter_concatenation(self):
        exporter = Exporter()
        engine = VoiceEngine()
        voice = engine.get_available_voices()[0]
        wav1 = engine.synthesize("Chunk 1.", voice)
        wav2 = engine.synthesize("Chunk 2.", voice)

        mastered = exporter.concatenate_wav_chunks([wav1, wav2])
        self.assertEqual(mastered[:4], b"RIFF")
        self.assertGreater(len(mastered), len(wav1))

if __name__ == "__main__":
    unittest.main()
