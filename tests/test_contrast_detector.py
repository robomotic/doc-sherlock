"""
Tests for the contrast detector.
"""

import pytest
from doc_sherlock.detectors.contrast_detector import ContrastDetector
from doc_sherlock.findings import FindingType
from .test_base import BaseDetectorTest


class TestContrastDetector(BaseDetectorTest):
    """Tests for the contrast detector."""
    
    def test_detects_low_contrast(self):
        """Test that low contrast text is detected."""
        # Get test PDF with low contrast text
        pdf_path = self.get_test_pdf_path("low_contrast.pdf")
        
        # Configure and run detector
        detector = ContrastDetector(pdf_path, {"min_contrast_ratio": 4.5})
        findings = detector.detect()
        
        # Check that findings were made
        assert len(findings) > 0, "Should detect low contrast text"
        
        # Check that findings are of the correct type
        assert any(finding.finding_type == FindingType.LOW_CONTRAST for finding in findings)
        
        # Check that the text was identified
        assert any("hidden white text" in (finding.text_content or "").lower() for finding in findings)
    
    def test_ignores_good_contrast(self):
        """Test that good contrast text is not flagged."""
        # Use a normal PDF (metadata test PDF should have normal contrast text)
        pdf_path = self.get_test_pdf_path("suspicious_metadata.pdf")
        
        # Configure and run detector with low threshold to ensure we're not getting false positives
        detector = ContrastDetector(pdf_path, {"min_contrast_ratio": 3.0})
        findings = detector.detect()
        
        # Check that no inappropriate findings were made
        assert all(finding.finding_type != FindingType.LOW_CONTRAST for finding in findings)
    
    def test_severity_levels(self):
        """Test that contrast severity levels are assigned correctly."""
        pdf_path = self.get_test_pdf_path("low_contrast.pdf")
        
        # Set a very low threshold to ensure we get findings
        detector = ContrastDetector(pdf_path, {"min_contrast_ratio": 1.01})
        findings = detector.detect()
        
        # Filter to only low contrast findings
        contrast_findings = [f for f in findings if f.finding_type == FindingType.LOW_CONTRAST]
        assert len(contrast_findings) > 0
        
        # We should have varying severity levels based on the contrast ratios in the test file
        severity_levels = {finding.severity.value for finding in contrast_findings}
        
        # We should have at least one high or critical severity finding
        assert any(level in severity_levels for level in ["high", "critical"])
