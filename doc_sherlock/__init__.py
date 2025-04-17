"""
Doc-Sherlock: A tool to detect hidden text in PDF documents.
"""

from .analyzer import PDFAnalyzer
from .findings import Finding, FindingType, Severity, AnalysisResults

__version__ = "0.1.0"
__all__ = ["PDFAnalyzer", "Finding", "FindingType", "Severity", "AnalysisResults"]
