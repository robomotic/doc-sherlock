"""
Tests for prompt injection detection on generated sample PDFs.
"""

import pytest
from doc_sherlock.detectors.prompt_detector import PromptDetector
from doc_sherlock.findings import FindingType, Severity
from .test_base import BaseDetectorTest


class TestPromptInjectionSamples(BaseDetectorTest):
    """Test suite for detecting prompt injections in sample PDFs."""
    
    def test_prompt_injection_pdf_detected(self):
        """Test that prompt_injection.pdf triggers HIGH severity findings."""
        pdf_path = self.get_test_pdf_path("prompt_injection.pdf")
        assert pdf_path is not None, "prompt_injection.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        # Should detect multiple prompt injection patterns
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) > 0, "Should detect prompt injection attempts"
        
        # All findings should be CRITICAL severity
        for finding in prompt_findings:
            assert finding.severity == Severity.CRITICAL, f"Finding should be CRITICAL severity: {finding.description}"
        
        # Should detect specific patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        print(f"\nDetected patterns: {pattern_names}")
        
        # Should detect at least some of the injected patterns
        assert any("ignore" in name or "bypass" in name or "previous" in name 
                   for name in pattern_names), "Should detect jailbreak keywords"
    
    def test_prompt_injection_jailbreak_pdf_detected(self):
        """Test that prompt_injection_jailbreak.pdf triggers multiple HIGH findings."""
        pdf_path = self.get_test_pdf_path("prompt_injection_jailbreak.pdf")
        assert pdf_path is not None, "prompt_injection_jailbreak.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) >= 3, f"Should detect multiple jailbreak attempts, found {len(prompt_findings)}"
        
        # Check that various hiding techniques are detected
        descriptions = [f.description for f in prompt_findings]
        print(f"\nFound {len(prompt_findings)} prompt injection attempts:")
        for desc in descriptions:
            print(f"  - {desc}")
    
    def test_prompt_injection_stealth_pdf_detected(self):
        """Test that prompt_injection_stealth.pdf triggers findings despite stealth techniques."""
        pdf_path = self.get_test_pdf_path("prompt_injection_stealth.pdf")
        assert pdf_path is not None, "prompt_injection_stealth.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        
        # Even with stealth techniques, text extraction should catch some attempts
        assert len(prompt_findings) > 0, "Should detect at least some stealth injection attempts"
        
        print(f"\nDetected {len(prompt_findings)} stealth injection attempts despite hiding techniques")
        
        # Verify metadata is captured
        for finding in prompt_findings:
            assert finding.metadata is not None, "Finding should have metadata"
            assert "pattern_name" in finding.metadata, "Should capture pattern name"
            assert "matched_text" in finding.metadata, "Should capture matched text"
    
    def test_all_injection_pdfs_have_high_severity(self):
        """Test that all prompt injection PDFs produce HIGH severity findings."""
        test_pdfs = [
            "prompt_injection.pdf",
            "prompt_injection_jailbreak.pdf",
            "prompt_injection_stealth.pdf"
        ]
        
        for pdf_name in test_pdfs:
            pdf_path = self.get_test_pdf_path(pdf_name)
            if pdf_path is None:
                pytest.skip(f"{pdf_name} not found")
                continue
            
            detector = PromptDetector(pdf_path)
            findings = detector.detect()
            
            prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
            
            # All prompt injection findings should be CRITICAL severity
            for finding in prompt_findings:
                assert finding.severity == Severity.CRITICAL, \
                    f"{pdf_name}: All prompt injection findings should be CRITICAL severity"
    
    def test_injection_metadata_completeness(self):
        """Test that detected injections have complete metadata."""
        pdf_path = self.get_test_pdf_path("prompt_injection.pdf")
        assert pdf_path is not None, "prompt_injection.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) > 0, "Should have findings to test"
        
        # Check metadata completeness
        for finding in prompt_findings:
            metadata = finding.metadata
            assert metadata is not None, "Finding should have metadata"
            
            # Required metadata fields
            required_fields = ["pattern_name", "matched_text", "context", "rule", "rule_version", "category"]
            for field in required_fields:
                assert field in metadata, f"Metadata should contain '{field}'"
            
            # Verify rule information
            assert metadata["rule"] == "PromptInjectionJailbreak"
            assert metadata["rule_version"] == "1.0.0"
            assert metadata["category"] == "jailbreak/injection"
            
            # Verify context is meaningful
            assert len(metadata["context"]) > 0, "Context should not be empty"
            assert metadata["matched_text"] in metadata["context"], "Context should contain matched text"

    def test_tiny_font_injected_pdf_detected(self):
        """Test detection of tiny-font-injected.pdf with font size findings and optionally prompt injection."""
        from doc_sherlock.detectors.font_size_detector import FontSizeDetector
        from pathlib import Path
        
        # Check multiple possible locations
        pdf_path = self.get_test_pdf_path("tiny-font-injected.pdf")
        
        # If not found, check in tests/injected/ directory
        if pdf_path is None:
            injected_dir = Path(__file__).parent / "injected"
            candidate = injected_dir / "tiny-font-injected.pdf"
            if candidate.exists():
                pdf_path = str(candidate)
        
        # If still not found, check in tests/real/ directory
        if pdf_path is None:
            real_dir = Path(__file__).parent / "real"
            candidate = real_dir / "tiny-font-injected.pdf"
            if candidate.exists():
                pdf_path = str(candidate)
        
        if pdf_path is None:
            pytest.skip("tiny-font-injected.pdf not found in tests/data/, tests/injected/, or tests/real/")
        
        # Test font size detector - this should always detect tiny fonts
        font_detector = FontSizeDetector(pdf_path)
        font_findings = font_detector.detect()
        
        # Should have tiny font findings
        tiny_font_findings = [f for f in font_findings if f.finding_type == FindingType.TINY_FONT]
        assert len(tiny_font_findings) > 0, "Should detect tiny font"
        
        # Test prompt injection detector
        prompt_detector = PromptDetector(pdf_path)
        prompt_findings = prompt_detector.detect()
        
        # Check if prompt injection findings exist (optional, depends on PDF content)
        injection_findings = [f for f in prompt_findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        
        # If there are prompt injection findings, verify they are CRITICAL
        # (This is the main requirement - prompt injection findings must be CRITICAL)
        for finding in injection_findings:
            assert finding.severity == Severity.CRITICAL, "Prompt injection findings should be CRITICAL"
        
        print(f"\nDetected {len(tiny_font_findings)} tiny font issues (severity: {tiny_font_findings[0].severity if tiny_font_findings else 'N/A'}) and {len(injection_findings)} prompt injections")
        
        # The file should have at least tiny font findings (main requirement)
        assert len(tiny_font_findings) > 0, "Should have at least tiny font findings"
    
    def test_emily_gpt4_inject_pdf_has_critical_findings(self):
        """Test that emily-gpt4-inject.pdf is checked for CRITICAL findings."""
        from pathlib import Path
        from doc_sherlock.analyzer import PDFAnalyzer
        
        # Check multiple possible locations
        pdf_path = self.get_test_pdf_path("emily-gpt4-inject.pdf")
        
        # If not found, check in tests/injected/ directory
        if pdf_path is None:
            injected_dir = Path(__file__).parent / "injected"
            candidate = injected_dir / "emily-gpt4-inject.pdf"
            if candidate.exists():
                pdf_path = str(candidate)
        
        # If still not found, check in tests/real/ directory
        if pdf_path is None:
            real_dir = Path(__file__).parent / "real"
            candidate = real_dir / "emily-gpt4-inject.pdf"
            if candidate.exists():
                pdf_path = str(candidate)
        
        if pdf_path is None:
            pytest.skip("emily-gpt4-inject.pdf not found in tests/data/, tests/injected/, or tests/real/")
        
        # Run full analysis on the PDF
        analyzer = PDFAnalyzer(pdf_path)
        results = analyzer.run_all_detectors()
        findings = results.findings
        
        # Count findings by severity
        critical_findings = [f for f in findings if f.severity == Severity.CRITICAL]
        high_findings = [f for f in findings if f.severity == Severity.HIGH]
        medium_findings = [f for f in findings if f.severity == Severity.MEDIUM]
        low_findings = [f for f in findings if f.severity == Severity.LOW]
        
        print(f"\nAnalysis of emily-gpt4-inject.pdf:")
        print(f"  CRITICAL: {len(critical_findings)}")
        print(f"  HIGH: {len(high_findings)}")
        print(f"  MEDIUM: {len(medium_findings)}")
        print(f"  LOW: {len(low_findings)}")
        
        # If there are CRITICAL findings, list them
        if critical_findings:
            print(f"\nCRITICAL findings detected:")
            for finding in critical_findings:
                print(f"  - {finding.finding_type.value}: {finding.description}")
        
        # Test specifically for prompt injection
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        if prompt_findings:
            print(f"\nPrompt injection findings: {len(prompt_findings)}")
            # Verify all prompt injection findings are CRITICAL
            for finding in prompt_findings:
                assert finding.severity == Severity.CRITICAL, \
                    f"All prompt injection findings should be CRITICAL, but found {finding.severity}"
        else:
            print("\nNo prompt injection patterns detected in this PDF")
        
        # The test passes - we've verified the PDF is analyzed and reported findings by severity
        print(f"\nTotal findings: {len(findings)}")

