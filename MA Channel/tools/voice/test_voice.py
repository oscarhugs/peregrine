"""Focused parser and audio-pipeline checks that do not load a TTS model."""

import argparse
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import voice


class ScriptTests(unittest.TestCase):
    def test_sample_sections_and_markup(self):
        path = voice.CHANNEL_ROOT / "videos" / "_test" / "script.md"
        sections = voice.parse_script(path)
        self.assertEqual(len(sections), 2)
        self.assertNotIn("[SOURCE:", sections[0].text)
        self.assertNotIn("[VISUAL:", sections[0].text)
        self.assertTrue(all(len(chunk) <= 250 for section in sections for paragraph in section.paragraphs for chunk in paragraph.chunks))

    def test_reference_affects_cache_key(self):
        first = voice.cache_key("Test.", "a", 0.4, 0.5)
        self.assertNotEqual(first, voice.cache_key("Test.", "b", 0.4, 0.5))
        self.assertNotEqual(first, voice.cache_key("Test.", "a", 0.7, 0.5))

    def test_real_script_removes_source_ids_and_notes(self):
        path = voice.CHANNEL_ROOT / "videos" / "001-red-lobster" / "script.md"
        sections = voice.parse_script(path)
        self.assertEqual(len(sections), 8)
        self.assertNotIn("OSCAR:", " ".join(section.text for section in sections))
        self.assertNotIn("[S25]", " ".join(section.text for section in sections))


class AudioTests(unittest.TestCase):
    def test_reference_clip_selection(self):
        import numpy as np
        from prepare_reference import select_clip

        sample_rate = 24000
        signal = np.zeros(sample_rate * 30, dtype=np.float32)
        t = np.arange(sample_rate * 20, dtype=np.float32) / sample_rate
        signal[sample_rate * 5:sample_rate * 25] = 0.08 * np.sin(2 * np.pi * 220 * t)
        clip = select_clip(signal, sample_rate)
        self.assertGreaterEqual(len(clip) / sample_rate, 10)
        self.assertLessEqual(len(clip) / sample_rate, 20)
        self.assertGreater(float(np.sqrt(np.mean(clip * clip))), 0.03)

    def test_render_and_cache_without_gpu(self):
        import numpy as np
        import soundfile as sf

        class FakeTensor:
            def __init__(self, data):
                self.data = data

            def detach(self):
                return self

            def cpu(self):
                return self

            def numpy(self):
                return self.data

        class FakeModel:
            sr = 24000
            calls = 0

            def generate(self, text, **kwargs):
                self.calls += 1
                t = np.arange(24000, dtype=np.float32) / self.sr
                return FakeTensor((0.08 * np.sin(2 * np.pi * 220 * t))[None, :])

        section = voice.Section(1, "Test", [voice.Paragraph("One. Two.", ["One.", "Two."]),
                                                  voice.Paragraph("Three.", ["Three."])])
        model = FakeModel()
        args = argparse.Namespace(exaggeration=0.4, cfg_weight=0.5, reference=Path("synthetic-reference.wav"))
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            with patch.object(voice, "CACHE", out / "cache"):
                manifest = voice.render_section(section, model, "reference-hash", args, out)
                self.assertEqual(model.calls, 3)
                self.assertEqual(manifest["file"], "01_test.wav")
                self.assertAlmostEqual(manifest["duration"], 3.5, places=2)
                self.assertAlmostEqual(manifest["actual_lufs"], -16, delta=0.2)
                self.assertLessEqual(manifest["peak"], 0.999)
                audio, rate = sf.read(out / "01_test.wav")
                self.assertEqual(rate, 48000)
                self.assertEqual(len(audio), round(manifest["duration"] * rate))
                voice.render_section(section, model, "reference-hash", args, out)
                self.assertEqual(model.calls, 3)


if __name__ == "__main__":
    unittest.main()
