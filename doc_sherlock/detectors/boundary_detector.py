"""
Detector for identifying text positioned outside page boundaries.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import pypdf
import pdfplumber

from ..findings import Finding, FindingType, Severity
from .base_detector import BaseDetector

logger = logging.getLogger(__name__)


class BoundaryDetector(BaseDetector):
    """Detector for identifying text positioned outside normal page boundaries."""
    
    def _load_config(self) -> None:
        """Load configuration with default values."""
        # Margin thresholds as percentage of page dimensions
        self.margin_thresholds = {
            "left": self.config.get("left_margin", 0.0),  # Left margin
            "right": self.config.get("right_margin", 1.0),  # Right margin
            "top": self.config.get("top_margin", 0.0),  # Top margin
            "bottom": self.config.get("bottom_margin", 1.0),  # Bottom margin
        }
        
    def detect(self) -> List[Finding]:
        """
        Run the detector and return any findings.
        
        Returns:
            List of findings from the detector
        """
        findings = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Check each page
                for i, page in enumerate(pdf.pages):
                    page_width = float(page.width)
                    page_height = float(page.height)
                    page_number = i + 1
                    
                    # Define page boundaries
                    left_boundary = self.margin_thresholds["left"] * page_width
                    right_boundary = self.margin_thresholds["right"] * page_width
                    top_boundary = self.margin_thresholds["top"] * page_height
                    bottom_boundary = self.margin_thresholds["bottom"] * page_height
                    
                    # Extract text with positioning info
                    words = page.extract_words(
                        x_tolerance=3, 
                        y_tolerance=3,
                        keep_blank_chars=True,
                        use_text_flow=True
                    )
                    
                    # Check each word for boundary violations
                    for word in words:
                        x0 = word.get("x0", 0)
                        y0 = word.get("top", 0)
                        x1 = word.get("x1", 0)
                        y1 = word.get("bottom", 0)
                        text = word.get("text", "")
                        
                        # Skip empty text
                        if not text.strip():
                            continue
                        
                        # Check if outside boundaries
                        outside_left = x0 < left_boundary
                        outside_right = x1 > right_boundary
                        outside_top = y0 < top_boundary
                        outside_bottom = y1 > bottom_boundary
                        
                        if outside_left or outside_right or outside_top or outside_bottom:
                            # Determine which boundaries are violated
                            violations = []
                            if outside_left:
                                violations.append("left")
                            if outside_right:
                                violations.append("right")
                            if outside_top:
                                violations.append("top")
                            if outside_bottom:
                                violations.append("bottom")
                                
                            # Determine severity based on how far outside
                            severity = Severity.MEDIUM
                            
                            # Calculate how far outside as percentage of page dimension
                            outside_percentages = {
                                "left": abs(x0 - left_boundary) / page_width if outside_left else 0,
                                "right": abs(x1 - right_boundary) / page_width if outside_right else 0,
                                "top": abs(y0 - top_boundary) / page_height if outside_top else 0,
                                "bottom": abs(y1 - bottom_boundary) / page_height if outside_bottom else 0,
                            }
                            
                            max_outside = max(outside_percentages.values())
                            
                            # Adjust severity based on how far outside
                            if max_outside > 0.5:
                                severity = Severity.CRITICAL
                            elif max_outside > 0.2:
                                severity = Severity.HIGH
                            elif max_outside > 0.05:
                                severity = Severity.MEDIUM
                            else:
                                severity = Severity.LOW
                                
                            # Create finding
                            finding = Finding(
                                finding_type=FindingType.OUTSIDE_BOUNDARY,
                                description=f"Text outside {', '.join(violations)} page boundary",
                                severity=severity,
                                page_number=page_number,
                                location={
                                    "x0": x0 / page_width,
                                    "y0": y0 / page_height,
                                    "x1": x1 / page_width,
                                    "y1": y1 / page_height,
                                },
                                text_content=text,
                                metadata={
                                    "violations": violations,
                                    "outside_percentages": outside_percentages,
                                }
                            )
                            
                            findings.append(finding)
        except Exception as e:
            logger.error(f"Error in BoundaryDetector: {str(e)}")
                
        return findings
