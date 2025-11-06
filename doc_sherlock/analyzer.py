"""
Main module for PDF analysis.
"""

import os
from typing import Dict, List, Optional, Any, Set, Union
from pathlib import Path
import logging

import pdfplumber
import pikepdf

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
    """Class to analyze PDF files for potential hidden text."""

    def __init__(self, pdf_path: Union[str, Path], config: Optional[Dict[str, Any]] = None):
        """
        Initialize PDF analyzer.

        Args:
            pdf_path: Path to the PDF file to analyze
            config: Configuration options for detectors
        """
        self.pdf_path = Path(pdf_path)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

    def run_all_detectors(self) -> 'AnalysisResults':
        """
        Run all available detectors on the PDF.

        Returns:
            AnalysisResults containing all findings
        """
        findings = []
        detectors = [
            BoundaryDetector(self.pdf_path, self.config),
            ContrastDetector(self.pdf_path, self.config),
            EncodingDetector(self.pdf_path, self.config),
            FontSizeDetector(self.pdf_path, self.config),
            LayerDetector(self.pdf_path, self.config),
            MetadataDetector(self.pdf_path, self.config),
            ObscuredTextDetector(self.pdf_path, self.config),
            OpacityDetector(self.pdf_path, self.config),
            RenderingDetector(self.pdf_path, self.config),
        ]

        for detector in detectors:
            try:
                self.logger.info("Running detector: %s", detector.__class__.__name__)
                detector_findings = detector.detect()
                findings.extend(detector_findings)
            except pikepdf.PdfError as e:
                self.logger.error("Error in detector %s: %s", detector.__class__.__name__, str(e))
            except Exception as e:
                self.logger.error("Unexpected error in detector %s: %s", detector.__class__.__name__, str(e))

        return AnalysisResults(str(self.pdf_path), findings)

    def analyze_file(self) -> AnalysisResults:
        """
        Analyze a single PDF file.

        Returns:
            AnalysisResults containing all findings
        """
        findings = self.run_all_detectors()
        return AnalysisResults(str(self.pdf_path), findings)

    @classmethod
    def analyze_directory(cls, directory_path: Union[str, Path], recursive: bool = False, config: Optional[Dict[str, Any]] = None) -> List[AnalysisResults]:
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
                result = analyzer.analyze_file()
                results.append(result)
            except Exception as e:
                logger.error("Error analyzing %s: %s", pdf_file, str(e))

        return results

