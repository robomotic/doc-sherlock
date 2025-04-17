"""
Module for representing detection findings and results.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class FindingType(Enum):
    """Types of suspicious content that can be found in PDFs."""
    
    LOW_CONTRAST = "low_contrast"
    TINY_FONT = "tiny_font"
    OUTSIDE_BOUNDARY = "outside_boundary"
    LOW_OPACITY = "low_opacity"
    HIDDEN_LAYER = "hidden_layer"
    OBSCURED_TEXT = "obscured_text"
    SUSPICIOUS_METADATA = "suspicious_metadata"
    RENDERING_DISCREPANCY = "rendering_discrepancy"
    ENCODING_ANOMALY = "encoding_anomaly"


class Severity(Enum):
    """Severity levels for findings."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    """Represents a single suspicious finding in a PDF document."""
    
    finding_type: FindingType
    description: str
    severity: Severity
    page_number: Optional[int] = None
    location: Optional[Dict[str, Any]] = None
    text_content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        result = {
            "type": self.finding_type.value,
            "description": self.description,
            "severity": self.severity.value,
        }
        
        if self.page_number is not None:
            result["page_number"] = self.page_number
            
        if self.location:
            result["location"] = self.location
            
        if self.text_content:
            result["text_content"] = self.text_content
            
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result


@dataclass
class AnalysisResults:
    """Represents the complete results of a PDF analysis."""
    
    filename: str
    findings: List[Finding] = field(default_factory=list)
    analysis_time: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the results."""
        self.findings.append(finding)
        
    def has_findings(self) -> bool:
        """Check if there are any findings."""
        return len(self.findings) > 0
    
    def severity_counts(self) -> Dict[Severity, int]:
        """Count findings by severity."""
        counts = {severity: 0 for severity in Severity}
        for finding in self.findings:
            counts[finding.severity] += 1
        return counts
    
    def type_counts(self) -> Dict[FindingType, int]:
        """Count findings by type."""
        counts = {finding_type: 0 for finding_type in FindingType}
        for finding in self.findings:
            counts[finding.finding_type] += 1
        return counts
    
    def summary(self) -> str:
        """Generate a textual summary of the results."""
        severity_counts = self.severity_counts()
        type_counts = self.type_counts()
        
        summary_lines = [
            f"Analysis results for: {self.filename}",
            f"Analysis time: {self.analysis_time.isoformat()}",
            f"Total findings: {len(self.findings)}",
            "\nSeverity counts:",
        ]
        
        for severity, count in severity_counts.items():
            if count > 0:
                summary_lines.append(f"  - {severity.value.title()}: {count}")
                
        summary_lines.append("\nFinding types:")
        
        for finding_type, count in type_counts.items():
            if count > 0:
                summary_lines.append(f"  - {finding_type.value.replace('_', ' ').title()}: {count}")
                
        if self.findings:
            summary_lines.append("\nTop findings:")
            sorted_findings = sorted(
                self.findings, 
                key=lambda f: ["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(f.severity.value.upper()),
                reverse=True
            )
            
            for i, finding in enumerate(sorted_findings[:5]):
                summary_lines.append(
                    f"  {i+1}. [{finding.severity.value.upper()}] {finding.description}"
                    f"{f' (Page {finding.page_number})' if finding.page_number is not None else ''}"
                )
            
            if len(self.findings) > 5:
                summary_lines.append(f"  ... and {len(self.findings) - 5} more findings.")
        
        return "\n".join(summary_lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary."""
        return {
            "filename": self.filename,
            "analysis_time": self.analysis_time.isoformat(),
            "findings": [finding.to_dict() for finding in self.findings],
            "metadata": self.metadata,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert results to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save_json(self, filepath: str, indent: int = 2) -> None:
        """Save results to JSON file."""
        with open(filepath, "w") as f:
            f.write(self.to_json(indent=indent))
