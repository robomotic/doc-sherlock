"""
Tests for the metadata detector.
"""

import pytest
from doc_sherlock.detectors.metadata_detector import MetadataDetector
from doc_sherlock.findings import FindingType
from .test_base import BaseDetectorTest


class TestMetadataDetector(BaseDetectorTest):
    """Tests for the metadata detector."""
    
    def test_detects_suspicious_metadata(self):
        """Test that suspicious content in metadata is detected."""
        # Get test PDF with suspicious metadata
        pdf_path = self.get_test_pdf_path("suspicious_metadata.pdf")
        
        # Configure and run detector
        detector = MetadataDetector(pdf_path)
        findings = detector.detect()
        
        # Check that findings were made
        assert len(findings) > 0, "Should detect suspicious metadata"
        
        # Check that findings are of the correct type
        metadata_findings = [f for f in findings if f.finding_type == FindingType.SUSPICIOUS_METADATA]
        assert len(metadata_findings) > 0
        
        # Check that suspicious keywords were detected
        suspicious_terms = ["prompt", "inject", "instruction"]
        detected_terms = []
        
        for finding in metadata_findings:
            for term in suspicious_terms:
                if finding.text_content and term in finding.text_content.lower():
                    detected_terms.append(term)
                    
        assert len(detected_terms) > 0, "Should detect suspicious terms in metadata"
    
    def test_ignores_normal_metadata(self):
        """Test that normal metadata is not flagged."""
        # Use a normal PDF (contrast test PDF should have normal metadata)
        pdf_path = self.get_test_pdf_path("low_contrast.pdf")
        
        # Configure and run detector
        detector = MetadataDetector(pdf_path)
        findings = detector.detect()
        
        # Check that no inappropriate findings were made
        metadata_findings = [f for f in findings if f.finding_type == FindingType.SUSPICIOUS_METADATA]
        assert len(metadata_findings) == 0
