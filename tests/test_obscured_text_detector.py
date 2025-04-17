"""
Tests for the obscured text detector.
"""

import pytest
from doc_sherlock.detectors.obscured_text_detector import ObscuredTextDetector
from doc_sherlock.findings import FindingType
from .test_base import BaseDetectorTest


class TestObscuredTextDetector(BaseDetectorTest):
    """Tests for the obscured text detector."""
    
    def test_detects_obscured_text(self):
        """Test that text obscured by shapes or images is detected."""
        # Get test PDF with obscured text
        pdf_path = self.get_test_pdf_path("obscured_text.pdf")
        
        # Configure and run detector
        detector = ObscuredTextDetector(pdf_path)
        findings = detector.detect()
        
        # Check that findings were made
        assert len(findings) > 0, "Should detect obscured text"
        
        # Check that findings are of the correct type
        obscured_findings = [f for f in findings if f.finding_type == FindingType.OBSCURED_TEXT]
        assert len(obscured_findings) > 0
        
        # Check that we detected the correct type of obscured text
        obscured_by_types = []
        for finding in obscured_findings:
            if finding.metadata and "obscured_by" in finding.metadata:
                obscured_by_types.append(finding.metadata["obscured_by"])
        
        # Our test PDF should have rectangle obscuring
        assert "rectangle" in obscured_by_types
    
    def test_ignores_normal_text(self):
        """Test that normal text without obscuring is not flagged."""
        # Use a normal PDF (metadata test PDF should have normal text)
        pdf_path = self.get_test_pdf_path("suspicious_metadata.pdf")
        
        # Configure and run detector
        detector = ObscuredTextDetector(pdf_path)
        findings = detector.detect()
        
        # Check that no inappropriate findings were made
        obscured_findings = [f for f in findings if f.finding_type == FindingType.OBSCURED_TEXT]
        assert len(obscured_findings) == 0
