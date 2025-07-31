"""
Base test class for doc-sherlock detectors.
"""

import os
import pytest
import tempfile
from pathlib import Path

from .pdf_generator import generate_all_test_pdfs

class BaseDetectorTest:
    """Base class for detector tests."""
    
    @classmethod
    def setup_class(cls):
        """Set up test class by generating all test PDFs."""
        cls.test_pdfs = generate_all_test_pdfs()
        
    def get_test_pdf_path(self, pdf_name):
        """Get the path to a test PDF file. Checks generated and manually added files."""
        path = self.test_pdfs.get(pdf_name)
        if path:
            return path
        # Check in the data directory for manually added files
        from pathlib import Path
        data_dir = Path(__file__).parent / "data"
        candidate = data_dir / pdf_name
        if candidate.exists():
            return str(candidate)
        return None
