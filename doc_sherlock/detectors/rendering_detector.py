"""
Detector for identifying discrepancies between text extraction and visual rendering.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
import pdfplumber
import pytesseract
from difflib import SequenceMatcher

from ..findings import Finding, FindingType, Severity
from .base_detector import BaseDetector

logger = logging.getLogger(__name__)


class RenderingDetector(BaseDetector):
    """Detector for identifying discrepancies between text extraction and visual rendering."""
    
    def _load_config(self) -> None:
        """Load configuration with default values."""
        self.similarity_threshold = self.config.get("similarity_threshold", 0.7)  # Minimum similarity ratio
        self.ocr_resolution = self.config.get("ocr_resolution", 300)  # DPI for OCR
        
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
                    
                    # Extract text directly from PDF
                    pdf_text = page.extract_text() or ""
                    pdf_text = self._normalize_text(pdf_text)
                    
                    if not pdf_text.strip():
                        continue  # Skip empty pages
                    
                    try:
                        # Render page to image
                        img = page.to_image(resolution=self.ocr_resolution)
                        pil_img = img.original
                        
                        # Extract text via OCR
                        ocr_text = pytesseract.image_to_string(pil_img) or ""
                        ocr_text = self._normalize_text(ocr_text)
                        
                        if not ocr_text.strip():
                            # If OCR couldn't extract any text but PDF has text
                            if len(pdf_text.strip()) > 0:
                                finding = Finding(
                                    finding_type=FindingType.RENDERING_DISCREPANCY,
                                    description=f"Page contains text in PDF that is not visible in rendered image",
                                    severity=Severity.HIGH,
                                    page_number=page_number,
                                    text_content=pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text,
                                    metadata={
                                        "pdf_text_length": len(pdf_text),
                                        "ocr_text_length": 0
                                    }
                                )
                                findings.append(finding)
                            continue
                        
                        # Compare texts
                        similarity = self._calculate_similarity(pdf_text, ocr_text)
                        
                        # Check if similarity is below threshold
                        if similarity < self.similarity_threshold:
                            # Find text chunks that appear in PDF but not in OCR
                            unique_to_pdf = self._find_unique_text(pdf_text, ocr_text)
                            
                            # Skip if no significant unique content
                            if len(unique_to_pdf) < 10:
                                continue
                                
                            severity = Severity.MEDIUM
                            if similarity < 0.3:
                                severity = Severity.HIGH
                            elif similarity < 0.5:
                                severity = Severity.MEDIUM
                            else:
                                severity = Severity.LOW
                                
                            finding = Finding(
                                finding_type=FindingType.RENDERING_DISCREPANCY,
                                description=f"Discrepancy between rendered text and actual content (similarity: {similarity:.2f})",
                                severity=severity,
                                page_number=page_number,
                                text_content=unique_to_pdf[:500] + "..." if len(unique_to_pdf) > 500 else unique_to_pdf,
                                metadata={
                                    "similarity_ratio": similarity,
                                    "pdf_text_length": len(pdf_text),
                                    "ocr_text_length": len(ocr_text),
                                    "unique_content_length": len(unique_to_pdf)
                                }
                            )
                            findings.append(finding)
                            
                    except Exception as e:
                        logger.warning(f"OCR analysis failed on page {page_number}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error in RenderingDetector: {str(e)}")
                
        return findings
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison by removing extra whitespace, etc.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Remove extra whitespace
        text = " ".join(text.split())
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation if needed
        # text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity ratio between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity ratio (0.0-1.0)
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _find_unique_text(self, text1: str, text2: str) -> str:
        """
        Find text that appears in text1 but not in text2.
        This is a simplified approach and may not catch all differences.
        
        Args:
            text1: Text to check for unique content
            text2: Text to compare against
            
        Returns:
            Text unique to text1
        """
        # Split into words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        # Find words unique to text1
        unique_words = words1 - words2
        
        # Join back into a string
        if not unique_words:
            return ""
            
        # Try to find contiguous chunks in the original text
        unique_text = []
        for word in unique_words:
            # Find the word and some context
            idx = text1.find(word)
            if idx >= 0:
                # Get a chunk of text around this word
                start = max(0, idx - 20)
                end = min(len(text1), idx + len(word) + 20)
                chunk = text1[start:end]
                unique_text.append(chunk)
                
        return "\n".join(unique_text)
