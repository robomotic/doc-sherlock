"""
Main module for PDF analysis.
"""

import os
from typing import Dict, List, Optional, Any, Set, Union
from pathlib import Path
import logging

from .findings import Finding, FindingType, Severity, AnalysisResults
from .detectors.contrast_detector import ContrastDetector
from .detectors.font_size_detector import FontSizeDetector
from .detectors.boundary_detector import BoundaryDetector
from .detectors.opacity_detector import OpacityDetector
from .detectors.layer_detector import LayerDetector
from .detectors.obscured_text_detector import ObscuredTextDetector
from .detectors.metadata_detector import MetadataDetector
from .detectors.rendering_detector import RenderingDetector
from .detectors.encoding_detector import EncodingDetector


logger = logging.getLogger(__name__)


class PDFAnalyzer:
    """Main class for analyzing PDFs for hidden text and other suspicious content."""
    
    def __init__(self, pdf_path: Union[str, Path], config: Optional[Dict[str, Any]] = None):
        """
        Initialize PDF analyzer.
        
        Args:
            pdf_path: Path to the PDF file to analyze
            config: Configuration options for detectors
        """
        self.pdf_path = Path(pdf_path)
        self.config = config or {}
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
            
        # Initialize results
        self.results = AnalysisResults(filename=str(self.pdf_path))
        
        # Initialize detectors
        self._init_detectors()
        
    def _init_detectors(self) -> None:
        """Initialize all detector instances."""
        self.detectors = {
            "contrast": ContrastDetector(self.pdf_path, self.config),
            "font_size": FontSizeDetector(self.pdf_path, self.config),
            "boundary": BoundaryDetector(self.pdf_path, self.config),
            "opacity": OpacityDetector(self.pdf_path, self.config),
            "layer": LayerDetector(self.pdf_path, self.config),
            "obscured_text": ObscuredTextDetector(self.pdf_path, self.config),
            "metadata": MetadataDetector(self.pdf_path, self.config),
            "rendering": RenderingDetector(self.pdf_path, self.config),
            "encoding": EncodingDetector(self.pdf_path, self.config),
        }
        
    def run_all_detectors(self) -> AnalysisResults:
        """Run all detectors and return results."""
        for detector_name, detector in self.detectors.items():
            logger.info(f"Running detector: {detector_name}")
            try:
                findings = detector.detect()
                for finding in findings:
                    self.results.add_finding(finding)
            except Exception as e:
                logger.error(f"Error in detector {detector_name}: {str(e)}")
                
        return self.results
    
    def detect_low_contrast(self) -> AnalysisResults:
        """Run only the low contrast detector."""
        findings = self.detectors["contrast"].detect()
        for finding in findings:
            self.results.add_finding(finding)
        return self.results
    
    def detect_tiny_font(self) -> AnalysisResults:
        """Run only the tiny font detector."""
        findings = self.detectors["font_size"].detect()
        for finding in findings:
            self.results.add_finding(finding)
        return self.results
    
    def detect_outside_boundary(self) -> AnalysisResults:
        """Run only the boundary detector."""
        findings = self.detectors["boundary"].detect()
        for finding in findings:
            self.results.add_finding(finding)
        return self.results
    
    def detect_low_opacity(self) -> AnalysisResults:
        """Run only the opacity detector."""
        findings = self.detectors["opacity"].detect()
        for finding in findings:
            self.results.add_finding(finding)
        return self.results
    
    def detect_hidden_layers(self) -> AnalysisResults:
        """Run only the layer detector."""
        findings = self.detectors["layer"].detect()
        for finding in findings:
            self.results.add_finding(finding)
        return self.results
    
    def detect_obscured_text(self) -> AnalysisResults:
        """Run only the obscured text detector."""
        findings = self.detectors["obscured_text"].detect()
        for finding in findings:
            self.results.add_finding(finding)
        return self.results
    
    def detect_suspicious_metadata(self) -> AnalysisResults:
        """Run only the metadata detector."""
        findings = self.detectors["metadata"].detect()
        for finding in findings:
            self.results.add_finding(finding)
        return self.results
    
    def detect_rendering_discrepancies(self) -> AnalysisResults:
        """Run only the rendering discrepancy detector."""
        findings = self.detectors["rendering"].detect()
        for finding in findings:
            self.results.add_finding(finding)
        return self.results
    
    def detect_encoding_anomalies(self) -> AnalysisResults:
        """Run only the encoding anomaly detector."""
        findings = self.detectors["encoding"].detect()
        for finding in findings:
            self.results.add_finding(finding)
        return self.results
    
    @classmethod
    def analyze_directory(cls, 
                          directory_path: Union[str, Path], 
                          recursive: bool = False, 
                          config: Optional[Dict[str, Any]] = None) -> List[AnalysisResults]:
        """
        Analyze all PDF files in a directory.
        
        Args:
            directory_path: Path to directory containing PDFs
            recursive: Whether to search for PDFs recursively
            config: Configuration options for detectors
            
        Returns:
            List of analysis results for each PDF
        """
        directory_path = Path(directory_path)
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Invalid directory path: {directory_path}")
            
        # Find all PDF files
        pdf_files = []
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        pdf_files.append(Path(root) / file)
        else:
            pdf_files = [f for f in directory_path.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
            
        # Analyze each PDF
        results = []
        for pdf_file in pdf_files:
            try:
                analyzer = cls(pdf_file, config)
                result = analyzer.run_all_detectors()
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {pdf_file}: {str(e)}")
                
        return results
