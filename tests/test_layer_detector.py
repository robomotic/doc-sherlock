"""
Tests for the layer detector.
"""

import pytest
from doc_sherlock.detectors.layer_detector import LayerDetector
from doc_sherlock.findings import FindingType
from .test_base import BaseDetectorTest


class TestLayerDetector(BaseDetectorTest):
    def test_functionalsample_no_alerts(self):
        """Test that functionalsample.pdf triggers no hidden layer alerts."""
        pdf_path = self.get_test_pdf_path("functionalsample.pdf")
        if pdf_path is None:
            pytest.skip("functionalsample.pdf not found in test data")
        detector = LayerDetector(pdf_path)
        findings = detector.detect()
        layer_findings = [f for f in findings if f.finding_type == FindingType.HIDDEN_LAYER]
        assert len(layer_findings) == 0, "functionalsample.pdf should not trigger hidden layer alerts"

    def test_functionalsample_injection_triggers_alert(self):
        """Test that functionalsample-injection1.pdf triggers at least one finding (any type)."""
        pdf_path = self.get_test_pdf_path("functionalsample-injection1.pdf")
        if pdf_path is None:
            pytest.skip("functionalsample-injection1.pdf not found in test data")
        detector = LayerDetector(pdf_path)
        findings = detector.detect()
        print("Findings for functionalsample-injection1.pdf:")
        for f in findings:
            print(f"- {getattr(f, 'finding_type', 'UNKNOWN')}: {getattr(f, 'description', '')}")
        assert len(findings) > 0, "functionalsample-injection1.pdf should trigger at least one finding"
    """Tests for the layer detector."""
    
    def test_detects_hidden_layers(self):
        """Test that hidden layers are detected."""
        # Get test PDF with hidden layers
        pdf_path = self.get_test_pdf_path("hidden_layer.pdf")
        
        # Configure and run detector
        detector = LayerDetector(pdf_path)
        findings = detector.detect()
        
        # Note: Our test PDF has simulated hidden layers through metadata
        # In real PDFs with OCG (Optional Content Groups), we'd have stronger detection
        
        # Check that we detect hidden layer indicators in the PDF
        assert len(findings) > 0, "Should detect hidden layer indicators"
        
        # Check that at least one finding is of the correct type
        layer_findings = [f for f in findings if f.finding_type == FindingType.HIDDEN_LAYER]
        assert len(layer_findings) > 0
    
    def test_ignores_normal_pdf(self):
        """Test that PDFs without hidden layers are not flagged."""
        # Use a normal PDF (contrast test PDF should have no layer info)
        pdf_path = self.get_test_pdf_path("low_contrast.pdf")
        
        # Configure and run detector
        detector = LayerDetector(pdf_path)
        findings = detector.detect()
        
        # Check that no inappropriate findings were made
        layer_findings = [f for f in findings if f.finding_type == FindingType.HIDDEN_LAYER]
        assert len(layer_findings) == 0
