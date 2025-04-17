"""
Tests for the opacity detector.
"""

import pytest
from doc_sherlock.detectors.opacity_detector import OpacityDetector
from doc_sherlock.findings import FindingType
from .test_base import BaseDetectorTest


class TestOpacityDetector(BaseDetectorTest):
    """Tests for the opacity detector."""
    
    def test_detects_low_opacity(self):
        """Test that low opacity text is detected."""
        # Get test PDF with low opacity text
        pdf_path = self.get_test_pdf_path("low_opacity.pdf")
        
        # Configure and run detector
        detector = OpacityDetector(pdf_path, {"min_opacity": 0.3})
        findings = detector.detect()
        
        # Check that findings were made
        assert len(findings) > 0, "Should detect low opacity text"
        
        # Check that findings are of the correct type
        assert any(finding.finding_type == FindingType.LOW_OPACITY for finding in findings)
        
        # Check that very low opacity content is assigned high severity
        assert any(
            finding.finding_type == FindingType.LOW_OPACITY and finding.severity.value in ["high", "critical"]
            for finding in findings
        )
    
    def test_ignores_normal_opacity(self):
        """Test that normal opacity text is not flagged."""
        # Use a normal PDF (metadata test PDF should have normal opacity text)
        pdf_path = self.get_test_pdf_path("suspicious_metadata.pdf")
        
        # Configure and run detector
        detector = OpacityDetector(pdf_path, {"min_opacity": 0.3})
        findings = detector.detect()
        
        # Check that no inappropriate findings were made
        low_opacity_findings = [f for f in findings if f.finding_type == FindingType.LOW_OPACITY]
        assert len(low_opacity_findings) == 0
