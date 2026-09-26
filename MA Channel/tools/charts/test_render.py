"""Small validation and still-render tests; full MP4 smoke test is in README."""

import json
import tempfile
import unittest
from pathlib import Path

import render


EXAMPLES = Path(__file__).parent / "examples"


class ChartTests(unittest.TestCase):
    def test_all_examples_validate(self):
        specs = [json.loads(path.read_text(encoding="utf-8")) for path in EXAMPLES.glob("*.json")]
        self.assertEqual({spec["type"] for spec in specs}, render.KINDS)
        for spec in specs:
            with self.subTest(spec=spec["type"]):
                self.assertIs(render.validate(spec), spec)

    def test_easing_and_final_hold_progress(self):
        self.assertEqual(render.ease(-1), 0)
        self.assertEqual(render.ease(1), 1)
        self.assertGreater(render.ease(0.5), 0.5)
        self.assertEqual(render.reveal(1, 0.85, 1), 1)

    def test_bad_common_fields(self):
        base = json.loads((EXAMPLES / "number_counter.json").read_text(encoding="utf-8"))
        for field, value in (("theme", "blue"), ("duration", 3), ("decimals", 9),
                             ("type", "pie"), ("source", "")):
            with self.subTest(field=field):
                spec = {**base, field: value}
                with self.assertRaises(ValueError):
                    render.validate(spec)

    def test_bad_flow_endpoints(self):
        base = json.loads((EXAMPLES / "deal_flow.json").read_text(encoding="utf-8"))
        spec = {**base, "edges": [{"from": "missing", "to": "brand", "label": "buys"}]}
        with self.assertRaisesRegex(ValueError, "endpoints"):
            render.validate(spec)
        spec = {**base, "nodes": [base["nodes"][0], base["nodes"][0]]}
        with self.assertRaisesRegex(ValueError, "duplicate"):
            render.validate(spec)

    def test_final_frame_png_dimensions(self):
        spec = json.loads((EXAMPLES / "timeline.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spec.json"
            spec["out"] = "timeline.mp4"
            path.write_text(json.dumps(spec), encoding="utf-8")
            result = render.render(path, still=True)
            from PIL import Image

            with Image.open(result) as image:
                self.assertEqual(image.size, (1920, 1080))


if __name__ == "__main__":
    unittest.main()
