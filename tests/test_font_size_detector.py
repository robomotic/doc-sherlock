"""
Tests for the font size detector.
"""

import pytest
from doc_sherlock.detectors.font_size_detector import FontSizeDetector
from doc_sherlock.findings import FindingType
from .test_base import BaseDetectorTest


class TestFontSizeDetector(BaseDetectorTest):
    """Tests for the font size detector."""
    
    def test_detects_tiny_font(self):
        """Test that tiny font text is detected."""
        # Get test PDF with tiny font text
        pdf_path = self.get_test_pdf_path("tiny_font.pdf")
        
        # Configure and run detector
        detector = FontSizeDetector(pdf_path, {"min_font_size": 4.0})
        findings = detector.detect()
        
        # Check that findings were made
        assert len(findings) > 0, "Should detect tiny font text"
        
        # Check that findings are of the correct type
        assert any(finding.finding_type == FindingType.TINY_FONT for finding in findings)
        
        # Check that the text was identified (even if just partially due to tiny font)
        # We'll check for a subset of words since tiny text extraction can be partial
        assert any("tiny" in (finding.text_content or "").lower() for finding in findings)
    
    def test_ignores_normal_font(self):
        """Test that normal font size text is not flagged."""
        # Use a normal PDF (metadata test PDF should have normal font sizes)
        pdf_path = self.get_test_pdf_path("suspicious_metadata.pdf")
        
        # Configure and run detector
        detector = FontSizeDetector(pdf_path, {"min_font_size": 4.0})
        findings = detector.detect()
        
        # Check that no inappropriate findings were made
        assert all(finding.finding_type != FindingType.TINY_FONT for finding in findings)
    
    def test_severity_levels(self):
        """Test that font size severity levels are assigned correctly."""
        pdf_path = self.get_test_pdf_path("tiny_font.pdf")
        
        # Set a reasonable threshold
        detector = FontSizeDetector(pdf_path, {"min_font_size": 4.0})
        findings = detector.detect()
        
        # Filter to only tiny font findings
        tiny_font_findings = [f for f in findings if f.finding_type == FindingType.TINY_FONT]
        assert len(tiny_font_findings) > 0
        
        # For our test PDFs, we should have at least one high or critical severity finding (1pt text)
        assert any(finding.severity.value in ["high", "critical"] for finding in tiny_font_findings)
