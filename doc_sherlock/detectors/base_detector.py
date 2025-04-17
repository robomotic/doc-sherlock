"""Base class for PDF detectors."""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

import pdfplumber
import pikepdf

from ..findings import Finding, FindingType, Severity


class BaseDetector:
    """Base class for all PDF detectors."""

    def __init__(self, pdf_path: Path, config: Optional[Dict[str, Any]] = None):
        """
        Initialize detector.

        Args:
            pdf_path: Path to PDF file to analyze
            config: Optional configuration options
        """
        self.pdf_path = Path(pdf_path)
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def _load_config(self) -> None:
        """Load detector-specific configuration."""
        raise NotImplementedError("Detectors must implement _load_config")

    def create_finding(
        self,
        finding_type: FindingType,
        severity: Severity,
        description: str,
        page_number: int,
        location: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Finding:
        """
        Create a finding with standardized structure.

        Args:
            finding_type: Type of the finding
            severity: Severity level
            description: Description of the finding
            page_number: Page number where the finding was detected
            location: Optional normalized coordinates of the finding
            metadata: Optional additional metadata

        Returns:
            Finding object
        """
        return Finding(
            finding_type=finding_type,
            severity=severity,
            description=description,
            page_number=page_number,
            location=location,
            metadata=metadata
        )

    def normalize_coordinates(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        page_width: float,
        page_height: float
    ) -> Dict[str, float]:
        """
        Normalize coordinates relative to page dimensions.

        Args:
            x0, y0: Top-left coordinates
            x1, y1: Bottom-right coordinates
            page_width: Width of the page
            page_height: Height of the page

        Returns:
            Dictionary with normalized coordinates
        """
        return {
            "x0": x0 / page_width,
            "y0": y0 / page_height,
            "x1": x1 / page_width,
            "y1": y1 / page_height,
        }

    def detect(self) -> List[Finding]:
        """
        Run the detector and return any findings.

        Returns:
            List of findings from the detector
        """
        raise NotImplementedError("Detectors must implement detect")
