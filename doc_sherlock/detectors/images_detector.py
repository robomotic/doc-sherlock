"""
Detector for identifying PDFs with many images but little or no text.
"""

import logging
from typing import Dict, List, Any, Optional
import pikepdf
import pdfplumber
from ..findings import Finding, FindingType, Severity
from .base_detector import BaseDetector

logger = logging.getLogger(__name__)

class ImagesDetector(BaseDetector):
    """Detects if a PDF has many images but very little or no text."""
    def __init__(self, pdf_path: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(pdf_path, config)
        self._load_config()

    def _load_config(self) -> None:
        self.min_images = self.config.get("min_images", 1)  # Minimum images to trigger
        self.max_text_chars = self.config.get("max_text_chars", 100)  # Max text chars to consider as 'little text'

    def detect(self) -> List[Finding]:
        findings = []
        try:
            # Count images using pikepdf
            with pikepdf.open(self.pdf_path) as pdf:
                total_images = 0
                for i, page in enumerate(pdf.pages):
                    resources = page.get("/Resources", {})
                    xobjects = resources.get("/XObject", {})
                    if hasattr(xobjects, 'items'):
                        for objname, obj in xobjects.items():
                            try:
                                if obj.get("/Subtype") == "/Image":
                                    total_images += 1
                            except Exception:
                                continue
            # Count actual extractable text using pdfplumber
            total_text = 0
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    total_text += len(text.strip())
            # Debug output
            logger.info(f"ImagesDetector: total_images={total_images}, total_text={total_text}")
            self._last_debug = (total_images, total_text)
            if total_images >= self.min_images and total_text <= self.max_text_chars:
                findings.append(Finding(
                    finding_type=FindingType.SUSPICIOUS_CONTENT,
                    description=f"PDF contains {total_images} images but only {total_text} text characters.",
                    severity=Severity.MEDIUM,
                    page_number=None,
                    metadata={
                        "total_images": total_images,
                        "total_text_chars": total_text
                    }
                ))
        except Exception as e:
            logger.error(f"Error in ImagesDetector: {str(e)}")
        return findings
