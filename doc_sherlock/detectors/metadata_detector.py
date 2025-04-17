"""
Detector for identifying suspicious content in PDF metadata.
"""

import logging
from pathlib import Path
import re
from typing import Dict, List, Any, Optional, Union
import pypdf

from ..findings import Finding, FindingType, Severity
from .base_detector import BaseDetector

logger = logging.getLogger(__name__)


class MetadataDetector(BaseDetector):
    """Detector for identifying suspicious content in PDF metadata."""
    
    def _load_config(self) -> None:
        """Load configuration with default values."""
        self.max_metadata_length = self.config.get("max_metadata_length", 1000)  # Characters
        self.suspicious_patterns = self.config.get("suspicious_patterns", [
            r"prompt",
            r"inject",
            r"system",
            r"ignore",
            r"instructions",
            r"llm",
            r"language\s*model",
            r"hidden",
            r"secret",
            r"password",
            r"ai",
            r"gpt",
            r"chatgpt",
            r"claude",
            r"gemini",
            r"bard",
            r"openai",
            r"anthropic",
            r"invisible",
            r"jailbreak"
        ])
        
    def detect(self) -> List[Finding]:
        """
        Run the detector and return any findings.
        
        Returns:
            List of findings from the detector
        """
        findings = []
        
        try:
            with open(self.pdf_path, "rb") as f:
                pdf = pypdf.PdfReader(f)
                
                # Check document info dictionary
                if pdf.metadata:
                    for key, value in pdf.metadata.items():
                        if not value:
                            continue
                            
                        # Skip standard keys with expected values
                        if key in ['/Producer', '/Creator'] and any(s in value for s in 
                                                                 ["Adobe", "Microsoft", "Apple", "LibreOffice", 
                                                                  "Google", "Acrobat", "Word", "LaTeX"]):
                            continue
                            
                        # Check for unusually long metadata
                        if len(value) > self.max_metadata_length:
                            finding = Finding(
                                finding_type=FindingType.SUSPICIOUS_METADATA,
                                description=f"Unusually long metadata in field '{key}'",
                                severity=Severity.MEDIUM,
                                metadata={
                                    "field": key,
                                    "length": len(value),
                                    "excerpt": value[:100] + "..." if len(value) > 100 else value
                                }
                            )
                            findings.append(finding)
                            
                        # Check for suspicious patterns
                        for pattern in self.suspicious_patterns:
                            if re.search(pattern, value, re.IGNORECASE):
                                finding = Finding(
                                    finding_type=FindingType.SUSPICIOUS_METADATA,
                                    description=f"Suspicious content in metadata field '{key}'",
                                    severity=Severity.HIGH,
                                    text_content=value[:200] + "..." if len(value) > 200 else value,
                                    metadata={
                                        "field": key,
                                        "matched_pattern": pattern,
                                        "length": len(value)
                                    }
                                )
                                findings.append(finding)
                                break
                
                # Check XMP metadata
                if hasattr(pdf, "xmp_metadata") and pdf.xmp_metadata:
                    xmp_content = pdf.xmp_metadata
                    
                    # Check for suspicious patterns in XMP
                    for pattern in self.suspicious_patterns:
                        if re.search(pattern, xmp_content, re.IGNORECASE):
                            finding = Finding(
                                finding_type=FindingType.SUSPICIOUS_METADATA,
                                description=f"Suspicious content in XMP metadata",
                                severity=Severity.HIGH,
                                metadata={
                                    "field": "XMP",
                                    "matched_pattern": pattern,
                                }
                            )
                            findings.append(finding)
                            break
                            
                    # Check for unusually long XMP
                    if len(xmp_content) > self.max_metadata_length * 2:  # XMP is typically longer
                        finding = Finding(
                            finding_type=FindingType.SUSPICIOUS_METADATA,
                            description=f"Unusually long XMP metadata",
                            severity=Severity.MEDIUM,
                            metadata={
                                "field": "XMP",
                                "length": len(xmp_content)
                            }
                        )
                        findings.append(finding)
                
                # Check document-level JavaScript actions
                if "/Names" in pdf.trailer["/Root"]:
                    names = pdf.trailer["/Root"]["/Names"]
                    if names and "/JavaScript" in names:
                        finding = Finding(
                            finding_type=FindingType.SUSPICIOUS_METADATA,
                            description=f"Document contains JavaScript",
                            severity=Severity.HIGH,
                            metadata={
                                "type": "JavaScript"
                            }
                        )
                        findings.append(finding)
                        
        except Exception as e:
            logger.error(f"Error in MetadataDetector: {str(e)}")
                
        return findings
