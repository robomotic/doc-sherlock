import os
import tempfile
import pytest
from doc_sherlock.detectors.images_detector import ImagesDetector
from doc_sherlock.findings import FindingType
from .test_base import BaseDetectorTest

class TestImageDetector(BaseDetectorTest):
    """Tests for the font size detector."""

    def test_images_detector_on_only_images_pdf(self):
        # Path to the static test file with only images
        test_pdf = self.get_test_pdf_path("only_images.pdf")

        detector = ImagesDetector(test_pdf, config={"min_images": 1, "max_text_chars": 100})
        findings = detector.detect()
        # Print debug info
        total_images, total_text = getattr(detector, '_last_debug', (None, None))
        print(f"DEBUG: total_images={total_images}, total_text={total_text}")
        assert any(f.finding_type == FindingType.SUSPICIOUS_CONTENT for f in findings), f"Should flag only_images.pdf as suspicious. Images: {total_images}, Text: {total_text}"


