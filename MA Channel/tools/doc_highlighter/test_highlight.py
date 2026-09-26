"""Offline quote-safety and local render checks."""

import tempfile
import unittest
from pathlib import Path

import pymupdf
from PIL import Image

import highlight


QUOTE = "The board approved the transaction after reviewing the expected cash flows"


def sample_pdf(path: Path, duplicate: bool = False, fact_line: str | None = None) -> None:
    document = pymupdf.open()
    page = document.new_page(width=595, height=842)
    page.insert_text((72, 100), "Example Company - Form 8-K", fontsize=13)
    page.insert_text((72, 130), "Management described several options for the business.", fontsize=12)
    page.insert_textbox(pymupdf.Rect(72, 150, 520, 235),
                        QUOTE + " and discussing the risks with its advisers.", fontsize=12)
    page.insert_text((72, 260), "The transaction remained subject to closing conditions.", fontsize=12)
    if fact_line:
        page.insert_textbox(pymupdf.Rect(72, 440, 520, 510), fact_line, fontsize=12)
    if duplicate:
        page.insert_textbox(pymupdf.Rect(72, 320, 520, 405),
                            QUOTE + " and discussing the risks with its advisers.", fontsize=12)
    document.save(path)
    document.close()


class HighlightTests(unittest.TestCase):
    def test_whitespace_and_hyphen_normalization(self):
        self.assertEqual(highlight.tokenize("Cash-flow\nreview"), ["cash", "flow", "review"])
        self.assertEqual(highlight.tokenize("cash  flow review"), ["cash", "flow", "review"])
        self.assertNotEqual(highlight.numeric_signature("$1.5 billion"),
                            highlight.numeric_signature("$2.5 billion"))

    def test_only_edgar_hosts_are_allowed(self):
        self.assertTrue(highlight.sec_host("https://www.sec.gov/Archives/edgar/data/1/a.htm"))
        self.assertFalse(highlight.sec_host("https://sec.gov.evil.example/Archives/edgar/data/1/a.htm"))
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "Archives/edgar/data"):
                highlight.fetch_edgar("https://www.sec.gov/about", Path(directory))

    def test_local_pdf_render(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "sample.pdf"
            output = root / "receipt.png"
            sample_pdf(source)
            still, movie = highlight.render(source, QUOTE, output, "8-K · Example Co. · 2025", False)
            self.assertIsNone(movie)
            with Image.open(still) as image:
                self.assertEqual(image.size, (1920, 1080))

    def test_ambiguous_duplicate_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "duplicate.pdf"
            sample_pdf(source, duplicate=True)
            with pymupdf.open(source) as document:
                with self.assertRaisesRegex(ValueError, "Three closest passages"):
                    highlight.choose_match(document, QUOTE)

    def test_absent_quote_fails_with_suggestions(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.pdf"
            sample_pdf(source)
            with pymupdf.open(source) as document:
                with self.assertRaisesRegex(ValueError, "Three closest passages"):
                    highlight.choose_match(document, "The shareholders rejected every proposed acquisition offer")

    def test_wrong_number_and_negation_never_highlight(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.pdf"
            fact = "The company did not receive $1.5 billion from the property sale in 2025."
            sample_pdf(source, fact_line=fact)
            with pymupdf.open(source) as document:
                correct, _ = highlight.choose_match(document, fact)
                self.assertTrue(correct.exact)
                for wrong in (fact.replace("$1.5", "$2.5"), fact.replace("did not", "did")):
                    with self.subTest(wrong=wrong):
                        with self.assertRaisesRegex(ValueError, "Three closest passages"):
                            highlight.choose_match(document, wrong)

    def test_label_from_header_when_available(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.pdf"
            sample_pdf(source)
            with pymupdf.open(source) as document:
                self.assertEqual(highlight.infer_label(document, "Fallback"),
                                 "8-K · Example Company")

    def test_installed_browser_prints_local_html(self):
        try:
            highlight.browser()
        except RuntimeError:
            self.skipTest("Chrome or Edge is not installed")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "sample.html"
            source.write_text("<html><body><h1>Example filing</h1><p>" + QUOTE +
                              " and discussing the risks with its advisers.</p></body></html>", encoding="utf-8")
            printed = highlight.print_html(source, root)
            with pymupdf.open(printed) as document:
                match, _ = highlight.choose_match(document, QUOTE)
                self.assertGreaterEqual(match.score, 94)
            still, _ = highlight.render(source, QUOTE, root / "html_receipt.png", None, False)
            with Image.open(still) as image:
                self.assertEqual(image.size, (1920, 1080))


if __name__ == "__main__":
    unittest.main()
