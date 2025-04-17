"""
Tests for the boundary detector.
"""

import pytest
from doc_sherlock.detectors.boundary_detector import BoundaryDetector
from doc_sherlock.findings import FindingType
from .test_base import BaseDetectorTest


class TestBoundaryDetector(BaseDetectorTest):
    """Tests for the boundary detector."""
    
    def test_detects_outside_boundary(self):
        """Test that text outside normal boundaries is detected."""
        # Get test PDF with text outside boundaries
        pdf_path = self.get_test_pdf_path("outside_boundary.pdf")
        
        # Configure and run detector
        detector = BoundaryDetector(pdf_path)
        findings = detector.detect()
        
        # Check that findings were made
        assert len(findings) > 0, "Should detect text outside boundaries"
        
        # Check that findings are of the correct type
        assert any(finding.finding_type == FindingType.OUTSIDE_BOUNDARY for finding in findings)
        
        # Check that the findings contain information about which boundaries were violated
        boundaries = []
        for finding in findings:
            if finding.metadata and "violations" in finding.metadata:
                boundaries.extend(finding.metadata["violations"])
        
        # Our test PDF should have right and bottom boundary violations
        assert "right" in boundaries or "bottom" in boundaries
    
    def test_ignores_normal_text(self):
        """Test that text within boundaries is not flagged."""
        # Use a normal PDF (metadata test PDF should have normal text positions)
        pdf_path = self.get_test_pdf_path("suspicious_metadata.pdf")
        
        # Configure detector with standard margins
        detector = BoundaryDetector(pdf_path)
        findings = detector.detect()
        
        # Check that no inappropriate findings were made
        assert all(finding.finding_type != FindingType.OUTSIDE_BOUNDARY for finding in findings)
