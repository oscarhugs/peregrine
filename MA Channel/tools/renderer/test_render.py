"""Fast checks for renderer planning and interchange files."""

import json
import shutil
import tempfile
import unittest
import wave
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlparse

import render


def beat(identifier: str, section: str, words: str, kind: str = "stock") -> render.Beat:
    return render.Beat({"id": identifier, "section": section, "vo": words,
                        "est_sec": 2, "visual": {"type": kind, "brief": "A test visual"}})


class RendererTests(unittest.TestCase):
    def test_allocate_preserves_section_duration(self):
        counts = render.allocate(151, [2, 6, 2])
        self.assertEqual(sum(counts), 151)
        self.assertGreater(counts[1], counts[0])
        self.assertTrue(all(item > render.FADE for item in counts))

    def test_nested_storyboard_fields(self):
        item = beat("00-01", "00 Opening", "hello")
        item.visual["on_screen_text"] = "THE DEAL"
        item.visual["source"] = "S25"
        self.assertEqual(item.field("on_screen_text"), "THE DEAL")
        self.assertEqual(item.field("source"), "S25")

    def test_chart_adapter_rejects_invented_comparison(self):
        item = beat("00-02", "00 Opening", "hello", "chart")
        item.visual["chart_spec"] = {"type": "bar_compare", "bars": [{"label": "Only", "value": 10}]}
        with self.assertRaisesRegex(ValueError, "without inventing data"):
            render.normalize_chart(item, Path("chart.mp4"), 5)

    def test_caption_groups_fit_two_short_lines(self):
        groups = render.caption_groups("The board described the transaction and explained how the cash moved between the companies and their lenders before closing.")
        self.assertGreater(len(groups), 0)
        self.assertTrue(all(len(caption.splitlines()) <= 2 for caption, _, _ in groups))
        self.assertTrue(all(len(line) <= 42 for caption, _, _ in groups for line in caption.splitlines()))

    def test_manifest_duration_controls_beat_weights(self):
        with tempfile.TemporaryDirectory() as directory:
            video = Path(directory)
            (video / "vo").mkdir()
            with wave.open(str(video / "vo/opening.wav"), "wb") as sound:
                sound.setnchannels(1)
                sound.setsampwidth(2)
                sound.setframerate(48000)
                sound.writeframes(b"\x00\x00" * (48000 * 4))
            (video / "vo/manifest.json").write_text(json.dumps({"sections": [
                {"title": "Opening", "file": "opening.wav", "duration": 4.0}]}), encoding="utf-8")
            section = render.Section("00 Opening", [beat("00-01", "00 Opening", "few words"),
                                                   beat("00-02", "00 Opening", "many more words in this second beat")])
            render.map_narration(video, [section])
            self.assertEqual(section.frames, 120)
            self.assertGreater(section.beats[1].frames, section.beats[0].frames)

    def test_fcpxml_has_four_linked_lanes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            visual = root / "base.mp4"
            overlay = root / "text.png"
            voice = root / "voice.wav"
            music = root / "music.wav"
            for path in (visual, overlay, voice, music):
                path.touch()
            item = beat("00-01", "00 Opening", "test words")
            item.frames = 60
            item.base = visual
            item.overlay = overlay
            section = render.Section("00 Opening", [item], frames=60, audio=voice)
            target = root / "timeline.fcpxml"
            render.write_fcpxml([section], music, target, (1280, 720))
            xml = ET.parse(target).getroot()
            clips = xml.findall(".//spine/asset-clip")
            self.assertEqual({clip.attrib.get("lane", "0") for clip in clips},
                             {"0", "1", "-1", "-2"})
            for asset in xml.findall("./resources/asset"):
                location = Path(unquote(urlparse(asset.attrib["src"]).path).lstrip("/"))
                self.assertTrue(location.is_file(), location)

    def test_external_still_renders_ken_burns(self):
        if not shutil.which("ffmpeg"):
            self.skipTest("FFmpeg is not installed")
        with tempfile.TemporaryDirectory() as directory:
            video = Path(directory)
            (video / "assets").mkdir()
            sample = render.CHANNEL / "tools/thumbnails/sample_hero_plate.png"
            shutil.copyfile(sample, video / "assets/00-01.png")
            item = beat("00-01", "00 Opening", "a test sentence")
            item.frames = 30
            render.render_beat(video, item, True, video / "build", {}, (1280, 720), True)
            self.assertTrue(item.base.is_file())
            self.assertGreater(render.probe_duration(item.base), 0.9)


if __name__ == "__main__":
    unittest.main()
