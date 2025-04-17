"""
Module for representing detection findings and results.
"""

from dataclasses import dataclass
from enum import Enum
import json
from typing import Dict, List, Optional, Any


class FindingType(str, Enum):
    """Types of findings that can be reported."""
    BOUNDARY = "boundary"
    CONTRAST = "contrast"
    ENCODING = "encoding"
    FONT_SIZE = "font_size"
    LAYER = "layer"
    METADATA = "metadata"
    OBSCURED = "obscured"
    OPACITY = "opacity"
    RENDERING = "rendering"
    # Add specific subtypes
    OUTSIDE_BOUNDARY = "outside_boundary"
    LOW_CONTRAST = "low_contrast"
    ENCODING_ANOMALY = "encoding_anomaly"
    TINY_FONT = "tiny_font"
    HIDDEN_LAYER = "hidden_layer"
    SUSPICIOUS_METADATA = "suspicious_metadata"
    OBSCURED_TEXT = "obscured_text"
    LOW_OPACITY = "low_opacity"
    RENDERING_DISCREPANCY = "rendering_discrepancy"


class Severity(str, Enum):
    """Severity levels for findings."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    """A finding from a detector."""
    finding_type: FindingType
    severity: Severity
    description: str
    page_number: int
    location: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary format."""
        return {
            "type": self.finding_type,
            "severity": self.severity,
            "description": self.description,
            "page_number": self.page_number,
            "location": self.location,
            "metadata": self.metadata
        }


class AnalysisResults:
    """Container for all findings from analyzing a PDF."""

    def __init__(self, pdf_path: str, findings: List[Finding]):
        """
        Initialize analysis results.

        Args:
            pdf_path: Path to the analyzed PDF
            findings: List of findings from analysis
        """
        self.pdf_path = pdf_path
        self.findings = findings

    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary format."""
        return {
            "pdf_path": self.pdf_path,
            "findings": [finding.to_dict() for finding in self.findings]
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert results to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save_json(self, output_path: str, indent: int = 2) -> None:
        """
        Save results to JSON file.

        Args:
            output_path: Path to save JSON file
            indent: Number of spaces for JSON indentation
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=indent)
