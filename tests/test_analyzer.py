"""
Tests for the main PDFAnalyzer class.
"""

import pytest
import os
from pathlib import Path

from doc_sherlock.analyzer import PDFAnalyzer
from doc_sherlock.findings import FindingType
from .test_base import BaseDetectorTest


class TestPDFAnalyzer(BaseDetectorTest):

    def test_real_cv_hide(self):
        """A real CV with simple injection"""
        pdf_path = self.get_test_pdf_path("simple_cv_spice.pdf")

        # Font size detector
        from doc_sherlock.detectors.font_size_detector import FontSizeDetector
        font_detector = FontSizeDetector(pdf_path, {"min_font_size": 4.0})
        font_findings = font_detector.detect()
        small_font_findings = [f for f in font_findings if getattr(f, "finding_type", None) == FindingType.TINY_FONT]
        print("Small font findings:")
        for f in small_font_findings:
            print(f"- Page {getattr(f, 'page_number', '?')}: {getattr(f, 'description', '')} (font size: {f.metadata.get('font_size') if hasattr(f, 'metadata') else '?'})")

        # Opacity detector
        from doc_sherlock.detectors.opacity_detector import OpacityDetector
        opacity_detector = OpacityDetector(pdf_path)
        opacity_findings = opacity_detector.detect()
        print("Opacity findings:")
        for f in opacity_findings:
            print(f"- Page {getattr(f, 'page_number', '?')}: {getattr(f, 'description', '')}")

        # Assert at least one finding for small font or opacity
        assert len(small_font_findings) > 0 or len(opacity_findings) > 0, "No small font or opacity findings in functionalsample-injection1.pdf"

    def test_analyzer_initialization(self):
        """Test that the analyzer initializes properly."""
        # Get a test PDF
        pdf_path = self.get_test_pdf_path("low_contrast.pdf")
        
        # Initialize analyzer
        analyzer = PDFAnalyzer(pdf_path)
        
        # Check that analyzer is properly initialized
        assert analyzer.pdf_path == Path(pdf_path)
    
    def test_run_all_detectors(self):
        """Test that run_all_detectors runs all detectors and aggregates results."""
        # Use a test PDF with multiple issues
        pdf_path = self.get_test_pdf_path("low_contrast.pdf")
        
        # Initialize analyzer
        analyzer = PDFAnalyzer(pdf_path)
        
        # Run all detectors
        results = analyzer.run_all_detectors()
        
        # Check that results are returned
        assert results is not None
        assert hasattr(results, "findings")
        
        # The test PDF should have findings
        assert len(results.findings) > 0
        
        # Results object should have utility methods
        assert hasattr(results, "summary")
        assert hasattr(results, "has_findings")
        assert hasattr(results, "to_dict")
        
        # Test the has_findings method
        assert results.has_findings() is True
        
        # Check that the summary method doesn't crash
        summary = results.summary()
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    
    def test_analyze_directory(self):
        """Test the analyze_directory class method."""
        # Directory with test PDFs
        test_dir = str(Path(__file__).parent / "data")
        
        # Run analysis on the directory
        results_list = PDFAnalyzer.analyze_directory(test_dir, recursive=False)
        
        # Check that results were returned for each PDF
        assert len(results_list) > 0
        
        # Each result should be an AnalysisResults object
        for result in results_list:
            assert hasattr(result, "findings")
            assert hasattr(result, "has_findings")
            
        # At least one PDF should have findings
        assert any(result.has_findings() for result in results_list)
    
    def test_invalid_pdf_handling(self):
        """Test that invalid PDF paths are handled properly."""
        nonexistent_path = "/path/to/nonexistent.pdf"
        
        # Check that FileNotFoundError is raised
        with pytest.raises(FileNotFoundError):
            PDFAnalyzer(nonexistent_path)

