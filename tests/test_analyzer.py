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
    """Tests for the main PDFAnalyzer class."""
    
    def test_analyzer_initialization(self):
        """Test that the analyzer initializes properly."""
        # Get a test PDF
        pdf_path = self.get_test_pdf_path("low_contrast.pdf")
        
        # Initialize analyzer
        analyzer = PDFAnalyzer(pdf_path)
        
        # Check that analyzer is properly initialized
        assert analyzer.pdf_path == Path(pdf_path)
        assert hasattr(analyzer, "detectors")
        assert len(analyzer.detectors) > 0
    
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
    
    def test_individual_detector_methods(self):
        """Test the individual detector methods on the analyzer."""
        pdf_path = self.get_test_pdf_path("low_contrast.pdf")
        analyzer = PDFAnalyzer(pdf_path)
        
        # Test the low contrast detector method
        contrast_results = analyzer.detect_low_contrast()
        assert contrast_results is not None
        assert hasattr(contrast_results, "findings")
        
        # There should be low contrast findings in this test PDF
        contrast_findings = [f for f in contrast_results.findings if f.finding_type == FindingType.LOW_CONTRAST]
        assert len(contrast_findings) > 0
    
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
