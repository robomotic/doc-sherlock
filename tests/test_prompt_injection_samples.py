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
        
        # All findings should be HIGH severity
        for finding in prompt_findings:
            assert finding.severity == Severity.HIGH, f"Finding should be HIGH severity: {finding.description}"
        
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
            
            # All prompt injection findings should be HIGH severity
            for finding in prompt_findings:
                assert finding.severity == Severity.HIGH, \
                    f"{pdf_name}: All prompt injection findings should be HIGH severity"
    
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
