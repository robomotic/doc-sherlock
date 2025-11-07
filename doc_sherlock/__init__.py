"""
Doc-Sherlock: A tool to detect hidden text in PDF documents that could be used for prompt injection attacks.
"""

__version__ = "0.1.1"

from .analyzer import PDFAnalyzer
from .findings import Finding, FindingType, Severity, AnalysisResults


def get_version():
    """Return the version of doc-sherlock."""
    return __version__


__all__ = [
    "__version__",
    "get_version",
    "PDFAnalyzer",
    "Finding",
    "FindingType",
    "Severity",
    "AnalysisResults",
]
