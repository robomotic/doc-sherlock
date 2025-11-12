"""
Module for representing detection findings and results.
"""

from dataclasses import dataclass
from enum import Enum
import json
from typing import Dict, List, Optional, Any


class FindingType(str, Enum):
    """Types of findings that can be reported."""
    SUSPICIOUS_CONTENT = "suspicious_content"
    BOUNDARY = "boundary"
    CONTRAST = "contrast"
    ENCODING = "encoding"
    FONT_SIZE = "font_size"
    LAYER = "layer"
    METADATA = "metadata"
    OBSCURED = "obscured"
    OPACITY = "opacity"
    RENDERING = "rendering"
    PROMPT = "prompt"
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
    PROMPT_INJECTION_JAILBREAK = "prompt_injection_jailbreak"


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
    text_content: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary format."""
        result = {
            "type": self.finding_type,
            "severity": self.severity,
            "description": self.description,
            "page_number": self.page_number,
            "location": self.location,
            "metadata": self.metadata
        }
        if self.text_content is not None:
            result["text_content"] = self.text_content
        return result


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
        self.actions = self._determine_actions()

    def _determine_actions(self) -> str:
        """
        Determine the recommended actions based on findings.
        
        Returns:
            str: Recommended action string
        """
        if not self.findings:
            return "This document is clean"
        
        # Check for critical prompt injection/jailbreak findings
        for finding in self.findings:
            if finding.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK:
                return "This document should be blocked and reviewed by a human analyst"
        
        # If there are findings but no critical ones
        return "This document is potentially risky and should be reviewed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary format."""
        return {
            "pdf_path": self.pdf_path,
            "findings": [finding.to_dict() for finding in self.findings],
            "actions": self.actions
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

    def summary(self) -> str:
        """Return a human-readable summary of findings."""
        if not self.findings:
            return f"No findings for {self.pdf_path}."
        summary_lines = [f"Findings for {self.pdf_path}:"]
        for finding in self.findings:
            summary_lines.append(f"- [{finding.severity}] {finding.finding_type}: {finding.description}")
        summary_lines.append(f"\nRecommended action: {self.actions}")
        return "\n".join(summary_lines)

    def has_findings(self) -> bool:
        """Return True if there are any findings."""
        return bool(self.findings)
