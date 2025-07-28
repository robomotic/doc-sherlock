"""
Detector for identifying text that is obscured by other elements.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import pdfplumber
from PIL import Image
import pytesseract

from ..findings import Finding, FindingType, Severity
from .base_detector import BaseDetector

logger = logging.getLogger(__name__)


class ObscuredTextDetector(BaseDetector):
    """Detector for identifying text that is obscured by other elements."""
    
    def __init__(self, pdf_path: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(pdf_path, config)
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration with default values."""
        self.min_overlap_ratio = self.config.get("min_overlap_ratio", 0.5)
        
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
                    page_number = i + 1
                    
                    # Extract text and their bounding boxes
                    words = page.extract_words(
                        x_tolerance=3, 
                        y_tolerance=3,
                        keep_blank_chars=True,
                        use_text_flow=True
                    )
                    
                    # Extract images and their bounding boxes
                    images = page.images
                    
                    # Extract vector graphics (rects, lines, curves)
                    rects = page.rects
                    
                    # Check for text overlapping with images
                    for word in words:
                        word_bbox = (
                            word.get("x0", 0),
                            word.get("top", 0),
                            word.get("x1", 0),
                            word.get("bottom", 0)
                        )
                        
                        text = word.get("text", "")
                        if not text.strip():
                            continue
                        
                        # Check overlap with images
                        for img in images:
                            img_bbox = (
                                img.get("x0", 0),
                                img.get("top", 0),
                                img.get("x1", 0),
                                img.get("bottom", 0)
                            )
                            
                            overlap = self._calculate_bbox_overlap(word_bbox, img_bbox)
                            
                            if overlap > self.min_overlap_ratio:
                                finding = Finding(
                                    finding_type=FindingType.OBSCURED_TEXT,
                                    description=f"Text potentially obscured by image",
                                    severity=Severity.MEDIUM,
                                    page_number=page_number,
                                    location={
                                        "x0": word_bbox[0] / float(page.width),
                                        "y0": word_bbox[1] / float(page.height),
                                        "x1": word_bbox[2] / float(page.width),
                                        "y1": word_bbox[3] / float(page.height),
                                    },
                                    text_content=text,
                                    metadata={
                                        "overlap_ratio": overlap,
                                        "obscured_by": "image",
                                    }
                                )
                                
                                findings.append(finding)
                        
                        # Check overlap with rectangles
                        for rect in rects:
                            # Skip small decorative rectangles
                            if (rect.get("width", 0) < 10 or rect.get("height", 0) < 10):
                                continue
                                
                            rect_bbox = (
                                rect.get("x0", 0),
                                rect.get("top", 0),
                                rect.get("x1", 0),
                                rect.get("bottom", 0)
                            )
                            
                            overlap = self._calculate_bbox_overlap(word_bbox, rect_bbox)
                            
                            if overlap > self.min_overlap_ratio:
                                # Check if the rectangle has fill
                                has_fill = rect.get("fill", False)
                                if not has_fill:
                                    continue
                                
                                finding = Finding(
                                    finding_type=FindingType.OBSCURED_TEXT,
                                    description=f"Text potentially obscured by shape",
                                    severity=Severity.MEDIUM,
                                    page_number=page_number,
                                    location={
                                        "x0": word_bbox[0] / float(page.width),
                                        "y0": word_bbox[1] / float(page.height),
                                        "x1": word_bbox[2] / float(page.width),
                                        "y1": word_bbox[3] / float(page.height),
                                    },
                                    text_content=text,
                                    metadata={
                                        "overlap_ratio": overlap,
                                        "obscured_by": "rectangle",
                                    }
                                )
                                
                                findings.append(finding)
                    
                    # Optional: Perform OCR vs. text extraction analysis
                    # This compares what text is visible through OCR versus what text is actually in the PDF
                    # Significant discrepancies could indicate hidden text
                    # Note: This is computationally expensive and could be made optional
                    try:
                        # Render page to image
                        img = page.to_image(resolution=150)
                        pil_img = img.original
                        
                        # Extract text via OCR
                        ocr_text = pytesseract.image_to_string(pil_img)
                        
                        # Get all text from PDF extraction
                        pdf_text = page.extract_text()
                        
                        # Simple comparison: check if there's significantly more text in the PDF than what OCR sees
                        # This is a very simplified approach and can have many false positives/negatives
                        if len(pdf_text) > len(ocr_text) * 1.5:
                            # There's significantly more text in the PDF than what's visible to OCR
                            finding = Finding(
                                finding_type=FindingType.OBSCURED_TEXT,
                                description=f"Page contains more text in PDF than visible through OCR",
                                severity=Severity.HIGH,
                                page_number=page_number,
                                metadata={
                                    "pdf_text_length": len(pdf_text),
                                    "ocr_text_length": len(ocr_text),
                                    "ratio": len(pdf_text) / max(1, len(ocr_text)),
                                }
                            )
                            
                            findings.append(finding)
                    except Exception as e:
                        logger.warning(f"OCR comparison failed: {str(e)}")
                            
        except Exception as e:
            logger.error(f"Error in ObscuredTextDetector: {str(e)}")
                
        return findings
    
    def _calculate_bbox_overlap(self, bbox1, bbox2):
        """
        Calculate the overlap ratio between two bounding boxes.
        
        Args:
            bbox1: First bounding box as (x0, y0, x1, y1)
            bbox2: Second bounding box as (x0, y0, x1, y1)
            
        Returns:
            Overlap ratio (0.0-1.0) of bbox1 covered by bbox2
        """
        # Calculate intersection
        x0 = max(bbox1[0], bbox2[0])
        y0 = max(bbox1[1], bbox2[1])
        x1 = min(bbox1[2], bbox2[2])
        y1 = min(bbox1[3], bbox2[3])
        
        # Check if there is an intersection
        if x0 >= x1 or y0 >= y1:
            return 0.0
            
        # Calculate area of intersection
        intersection_area = (x1 - x0) * (y1 - y0)
        
        # Calculate area of bbox1
        bbox1_area = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        
        # Calculate overlap ratio
        if bbox1_area == 0:
            return 0.0
            
        return intersection_area / bbox1_area
