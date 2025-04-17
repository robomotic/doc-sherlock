"""
Base class for PDF detectors.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..findings import Finding


class BaseDetector(ABC):
    """Base class for all PDF detectors."""
    
    def __init__(self, pdf_path: Union[str, Path], config: Optional[Dict[str, Any]] = None):
        """
        Initialize detector.
        
        Args:
            pdf_path: Path to the PDF file to analyze
            config: Configuration options for the detector
        """
        self.pdf_path = Path(pdf_path)
        self.config = config or {}
        
        # Validate PDF path
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        # Load configuration with defaults
        self._load_config()
        
    def _load_config(self) -> None:
        """Load configuration with default values."""
        # Each detector should override this to set detector-specific defaults
        pass
        
    @abstractmethod
    def detect(self) -> List[Finding]:
        """
        Run the detector and return any findings.
        
        Returns:
            List of findings from the detector
        """
        pass
