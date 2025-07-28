"""
Detector for identifying unusual encoding in PDF content.
"""

import logging
from pathlib import Path
import re
from typing import Dict, List, Any, Optional, Union
import pikepdf

from ..findings import Finding, FindingType, Severity
from .base_detector import BaseDetector

logger = logging.getLogger(__name__)


class EncodingDetector(BaseDetector):
    def __init__(self, pdf_path: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(pdf_path, config)
        self._load_config()
    """Detector for identifying unusual encoding in PDF content."""
    
    def _load_config(self) -> None:
        """Load configuration with default values."""
        self.max_hex_ratio = self.config.get("max_hex_ratio", 0.3)  # Maximum ratio of hex-encoded characters
        
    def detect(self) -> List[Finding]:
        """
        Run the detector and return any findings.
        
        Returns:
            List of findings from the detector
        """
        findings = []
        
        try:
            with pikepdf.open(self.pdf_path) as pdf:
                # Check each page
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    
                    # Extract content streams
                    content_streams = []
                    if '/Contents' in page:
                        contents = page['/Contents']
                        if isinstance(contents, pikepdf.Array):
                            for item in contents:
                                content_streams.append(item)
                        else:
                            content_streams.append(contents)
                    
                    # Process each content stream
                    for stream_index, content in enumerate(content_streams):
                        try:
                            stream_data = content.read_bytes().decode('utf-8', errors='replace')
                            
                            # Check for unusual encoding
                            encoding_findings = self._check_unusual_encoding(stream_data, page_number, stream_index)
                            findings.extend(encoding_findings)
                            
                            # Check for obfuscated operators
                            operator_findings = self._check_obfuscated_operators(stream_data, page_number, stream_index)
                            findings.extend(operator_findings)
                            
                        except Exception as e:
                            logger.warning(f"Error processing stream {stream_index} on page {page_number}: {str(e)}")
                            
                # Check for unusual object encodings
                try:
                    # Iterate over all PDF objects
                    for obj in pdf.objects:
                        try:
                            obj_num = getattr(obj, "objgen", None)
                            # Check for embedded files
                            if isinstance(obj, pikepdf.Stream) and obj.get("/Type") == "/EmbeddedFile":
                                finding = Finding(
                                    finding_type=FindingType.ENCODING_ANOMALY,
                                    description=f"Embedded file detected in PDF",
                                    severity=Severity.MEDIUM,
                                    metadata={
                                        "object_id": str(obj_num),
                                    }
                                )
                                findings.append(finding)
                        except Exception as e:
                            logger.warning(f"Error processing object {obj_num}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Error processing PDF objects: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error in EncodingDetector: {str(e)}")
                
        return findings
    
    def _check_unusual_encoding(self, content: str, page_number: int, stream_index: int) -> List[Finding]:
        """
        Check for unusual encoding patterns in content stream.
        
        Args:
            content: Content stream as string
            page_number: Page number
            stream_index: Stream index
            
        Returns:
            List of findings
        """
        findings = []
        
        # Check for hex-encoded text (excessive use of <...> notation)
        hex_matches = re.findall(r'<[0-9A-Fa-f]+>', content)
        hex_chars = sum(len(m) - 2 for m in hex_matches)  # -2 for the brackets
        total_chars = len(content)
        
        if total_chars > 0:
            hex_ratio = hex_chars / total_chars
            
            if hex_ratio > self.max_hex_ratio:
                severity = Severity.MEDIUM
                if hex_ratio > 0.7:
                    severity = Severity.HIGH
                elif hex_ratio > 0.5:
                    severity = Severity.MEDIUM
                else:
                    severity = Severity.LOW
                    
                finding = Finding(
                    finding_type=FindingType.ENCODING_ANOMALY,
                    description=f"Unusual amount of hex-encoded content detected",
                    severity=severity,
                    page_number=page_number,
                    metadata={
                        "hex_ratio": hex_ratio,
                        "stream_index": stream_index
                    }
                )
                findings.append(finding)
        
        # Check for unusual Unicode escapes
        unicode_matches = re.findall(r'\\u[0-9A-Fa-f]{4}', content)
        if len(unicode_matches) > 20:  # Arbitrary threshold
            finding = Finding(
                finding_type=FindingType.ENCODING_ANOMALY,
                description=f"Unusual amount of Unicode escape sequences detected",
                severity=Severity.MEDIUM,
                page_number=page_number,
                metadata={
                    "unicode_escapes": len(unicode_matches),
                    "stream_index": stream_index
                }
            )
            findings.append(finding)
            
        return findings
    
    def _check_obfuscated_operators(self, content: str, page_number: int, stream_index: int) -> List[Finding]:
        """
        Check for obfuscated operators in content stream.
        
        Args:
            content: Content stream as string
            page_number: Page number
            stream_index: Stream index
            
        Returns:
            List of findings
        """
        findings = []
        
        # Check for unusual text operators
        tm_operator_count = len(re.findall(r'\bTm\b', content))
        tj_operator_count = len(re.findall(r'\bTj\b', content))
        tj_star_operator_count = len(re.findall(r'\bT\*\b', content))
        
        # High frequency of text positioning could indicate text being placed in unusual ways
        if tm_operator_count > 100:  # Arbitrary threshold
            finding = Finding(
                finding_type=FindingType.ENCODING_ANOMALY,
                description=f"Unusually high frequency of text positioning operators",
                severity=Severity.MEDIUM,
                page_number=page_number,
                metadata={
                    "tm_operator_count": tm_operator_count,
                    "stream_index": stream_index
                }
            )
            findings.append(finding)
            
        # Check for unusual escapable characters in strings
        unusual_escapes_count = len(re.findall(r'\\[^nrtbf\\()]', content))
        if unusual_escapes_count > 20:  # Arbitrary threshold
            finding = Finding(
                finding_type=FindingType.ENCODING_ANOMALY,
                description=f"Unusual escape sequences in text content",
                severity=Severity.MEDIUM,
                page_number=page_number,
                metadata={
                    "unusual_escapes": unusual_escapes_count,
                    "stream_index": stream_index
                }
            )
            findings.append(finding)
            
        return findings
