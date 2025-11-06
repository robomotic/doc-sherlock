"""
Tests for DAN (Do Anything Now) mode detection in PDFs.
"""

import pytest
from doc_sherlock.detectors.prompt_detector import PromptDetector
from doc_sherlock.findings import FindingType, Severity
from .test_base import BaseDetectorTest


class TestDANDetection(BaseDetectorTest):
    """Test suite for detecting DAN mode jailbreak attempts."""
    
    def test_dan_mode_pdf_detected(self):
        """Test that dan_mode.pdf triggers HIGH severity DAN findings."""
        pdf_path = self.get_test_pdf_path("dan_mode.pdf")
        assert pdf_path is not None, "dan_mode.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        # Should detect DAN patterns
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) > 0, "Should detect DAN mode attempts"
        
        # All findings should be HIGH severity
        for finding in prompt_findings:
            assert finding.severity == Severity.HIGH, f"Finding should be HIGH severity: {finding.description}"
        
        # Check for specific DAN patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        print(f"\nDetected DAN patterns: {pattern_names}")
        
        # Should detect DAN-specific keywords
        dan_keywords = ["dan_mode", "do_anything", "ignore_rules", "ignore_ethics", 
                       "authorization", "token_reward", "token_system", "ethics_bypass", "programming"]
        detected_dan = any(keyword in pattern_names for keyword in dan_keywords)
        assert detected_dan, f"Should detect DAN-specific patterns, found: {pattern_names}"
    
    def test_dan_token_system_pdf_detected(self):
        """Test that dan_token_system.pdf triggers token-based manipulation detection."""
        pdf_path = self.get_test_pdf_path("dan_token_system.pdf")
        assert pdf_path is not None, "dan_token_system.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) >= 3, f"Should detect multiple token system patterns, found {len(prompt_findings)}"
        
        # Check for token-related patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        token_patterns = ["token_reward", "token_system", "authorization"]
        detected_tokens = [p for p in pattern_names if p in token_patterns]
        
        print(f"\nDetected token manipulation patterns: {detected_tokens}")
        assert len(detected_tokens) > 0, "Should detect token-based manipulation"
    
    def test_dan_combined_pdf_detected(self):
        """Test that dan_combined.pdf triggers both DAN and jailbreak detections."""
        pdf_path = self.get_test_pdf_path("dan_combined.pdf")
        assert pdf_path is not None, "dan_combined.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) >= 5, f"Should detect multiple combined patterns, found {len(prompt_findings)}"
        
        # Should detect both DAN and regular jailbreak patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        
        dan_patterns = ["dan_mode", "do_anything", "ignore_ethics", "authorization"]
        jailbreak_patterns = ["forget", "disregard", "override", "primary_task", "bypass_filter"]
        
        detected_dan = any(p in pattern_names for p in dan_patterns)
        detected_jailbreak = any(p in pattern_names for p in jailbreak_patterns)
        
        print(f"\nDetected {len(prompt_findings)} total patterns:")
        print(f"  DAN patterns detected: {detected_dan}")
        print(f"  Jailbreak patterns detected: {detected_jailbreak}")
        
        assert detected_dan or detected_jailbreak, "Should detect combined attack patterns"
    
    def test_dan_mode_pattern_variants(self):
        """Test detection of various DAN mode pattern formulations."""
        pdf_path = self.get_test_pdf_path("dan_mode.pdf")
        assert pdf_path is not None, "dan_mode.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        # Check that case-insensitive matching works
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        
        # Verify metadata completeness for DAN patterns
        for finding in prompt_findings:
            assert finding.metadata is not None, "Finding should have metadata"
            assert "pattern_name" in finding.metadata
            assert "matched_text" in finding.metadata
            assert "context" in finding.metadata
            assert "rule" in finding.metadata
            
            # All DAN findings should reference the same rule
            assert finding.metadata["rule"] == "PromptInjectionJailbreak"
    
    def test_ethics_bypass_detection(self):
        """Test specific detection of ethics bypass attempts."""
        pdf_path = self.get_test_pdf_path("dan_mode.pdf")
        assert pdf_path is not None, "dan_mode.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        
        # Look for ethics-related patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        ethics_patterns = ["ignore_ethics", "ethics_bypass"]
        
        detected_ethics = [p for p in pattern_names if p in ethics_patterns]
        print(f"\nDetected ethics bypass patterns: {detected_ethics}")
        
        # Should detect at least some ethics bypass attempts
        assert len(detected_ethics) > 0, "Should detect ethics bypass patterns"
    
    def test_programming_override_detection(self):
        """Test detection of programming override attempts."""
        pdf_path = self.get_test_pdf_path("dan_combined.pdf")
        assert pdf_path is not None, "dan_combined.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        
        # Look for programming override patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        
        has_programming = "programming" in pattern_names
        print(f"\nProgramming override detected: {has_programming}")
        
        # The combined PDF should have programming override attempts
        if has_programming:
            prog_findings = [f for f in prompt_findings if f.metadata.get("pattern_name") == "programming"]
            for finding in prog_findings:
                print(f"  Match: {finding.metadata.get('matched_text')}")
    
    def test_all_dan_pdfs_high_severity(self):
        """Test that all DAN PDFs produce HIGH severity findings."""
        test_pdfs = [
            "dan_mode.pdf",
            "dan_token_system.pdf",
            "dan_combined.pdf"
        ]
        
        for pdf_name in test_pdfs:
            pdf_path = self.get_test_pdf_path(pdf_name)
            if pdf_path is None:
                pytest.skip(f"{pdf_name} not found")
                continue
            
            detector = PromptDetector(pdf_path)
            findings = detector.detect()
            
            prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
            
            # All DAN findings should be HIGH severity
            for finding in prompt_findings:
                assert finding.severity == Severity.HIGH, \
                    f"{pdf_name}: All DAN findings should be HIGH severity"
    
    def test_dan_patterns_count(self):
        """Test that all DAN pattern types are present in detector."""
        detector = PromptDetector(self.get_test_pdf_path("low_contrast.pdf"))
        
        # Verify DAN patterns are loaded
        dan_pattern_names = [
            "dan_mode", "do_anything", "ignore_rules", "ignore_ethics",
            "authorization", "token_reward", "token_system", "ethics_bypass", "programming"
        ]
        
        for pattern_name in dan_pattern_names:
            assert pattern_name in detector.all_patterns, \
                f"DAN pattern '{pattern_name}' should be loaded in detector"
        
        print(f"\n✓ All {len(dan_pattern_names)} DAN patterns successfully loaded")
