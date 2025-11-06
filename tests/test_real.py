"""
Tests for real-world PDF files in the tests/clean folder.
This test suite validates that clean PDFs do not trigger CRITICAL findings.
"""

import os
import pytest
from pathlib import Path
from collections import Counter

from doc_sherlock.analyzer import PDFAnalyzer
from doc_sherlock.findings import Severity


class TestRealPDFs:
    """Test suite for real PDF files."""
    
    @pytest.fixture
    def clean_pdf_dir(self):
        """Get the path to the clean PDFs directory."""
        return Path(__file__).parent / "clean"
    
    @pytest.fixture
    def clean_pdfs(self, clean_pdf_dir):
        """Get list of all PDF files in the clean directory."""
        if not clean_pdf_dir.exists():
            pytest.skip(f"Clean PDF directory not found: {clean_pdf_dir}")
        
        pdf_files = list(clean_pdf_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip(f"No PDF files found in: {clean_pdf_dir}")
        
        return pdf_files
    
    def test_clean_pdfs_no_critical_findings(self, clean_pdfs):
        """
        Test that clean PDFs do not trigger CRITICAL severity findings.
        
        This test:
        1. Lists all PDF files in tests/clean folder
        2. Runs all detections on each PDF
        3. Counts findings by severity level
        4. Prints total severity counts
        5. Fails if any CRITICAL findings are detected
        """
        print(f"\n{'='*70}")
        print(f"Testing {len(clean_pdfs)} PDF file(s) from tests/clean directory")
        print(f"{'='*70}\n")
        
        # Track overall severity counts across all PDFs
        total_severity_counts = Counter()
        
        # Track per-file results
        file_results = []
        
        for pdf_path in clean_pdfs:
            print(f"Analyzing: {pdf_path.name}")
            print("-" * 70)
            
            try:
                # Initialize analyzer and run all detectors
                analyzer = PDFAnalyzer(pdf_path)
                results = analyzer.run_all_detectors()
                
                # Count severities for this file
                severity_counts = Counter()
                for finding in results.findings:
                    severity_counts[finding.severity] += 1
                    total_severity_counts[finding.severity] += 1
                
                # Print findings for this file
                print(f"  Total findings: {len(results.findings)}")
                for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
                    count = severity_counts.get(severity, 0)
                    if count > 0:
                        print(f"    {severity.value.upper()}: {count}")
                
                # Store results
                file_results.append({
                    'file': pdf_path.name,
                    'total': len(results.findings),
                    'counts': severity_counts,
                    'critical': severity_counts.get(Severity.CRITICAL, 0)
                })
                
                print()
                
            except Exception as e:
                print(f"  ERROR: Failed to analyze {pdf_path.name}: {e}")
                print()
                # Still continue with other files
        
        # Print summary
        print(f"{'='*70}")
        print("SUMMARY - Total Severity Counts Across All Files")
        print(f"{'='*70}")
        print(f"Total PDFs analyzed: {len(file_results)}")
        print(f"Total findings: {sum(total_severity_counts.values())}")
        print()
        
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            count = total_severity_counts.get(severity, 0)
            print(f"  {severity.value.upper()}: {count}")
        
        print(f"{'='*70}\n")
        
        # Check for CRITICAL findings
        critical_count = total_severity_counts.get(Severity.CRITICAL, 0)
        
        if critical_count > 0:
            # Print which files had CRITICAL findings
            print("Files with CRITICAL findings:")
            for result in file_results:
                if result['critical'] > 0:
                    print(f"  - {result['file']}: {result['critical']} CRITICAL finding(s)")
            print()
            
            pytest.fail(
                f"Found {critical_count} CRITICAL severity finding(s) in clean PDFs. "
                f"Clean PDFs should not have CRITICAL findings."
            )
        
        # Test passes if no CRITICAL findings
        print("✓ All clean PDFs passed: No CRITICAL findings detected")
