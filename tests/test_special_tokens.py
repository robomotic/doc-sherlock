"""
Tests for LLM special token detection in PDFs.
"""

import pytest
from doc_sherlock.detectors.prompt_detector import PromptDetector
from doc_sherlock.findings import FindingType, Severity
from .test_base import BaseDetectorTest


class TestSpecialTokenDetection(BaseDetectorTest):
    """Test suite for detecting LLM-specific control tokens."""
    
    def test_llama_tokens_detected(self):
        """Test that Llama model tokens are detected."""
        pdf_path = self.get_test_pdf_path("special_tokens_llama.pdf")
        assert pdf_path is not None, "special_tokens_llama.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) > 0, "Should detect Llama special tokens"
        
        # Check for Llama-specific patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        llama_patterns = ["llama_begin_text", "llama_eot_id", "llama_start_header", 
                         "llama_end_header", "llama_system", "llama_user", "llama_assistant"]
        
        detected_llama = [p for p in pattern_names if p in llama_patterns]
        print(f"\nDetected Llama tokens: {detected_llama}")
        
        assert len(detected_llama) > 0, "Should detect Llama-specific tokens"
        
        # All findings should be HIGH severity
        for finding in prompt_findings:
            assert finding.severity == Severity.HIGH
    
    def test_openai_tokens_detected(self):
        """Test that OpenAI/GPT model tokens are detected."""
        pdf_path = self.get_test_pdf_path("special_tokens_openai.pdf")
        assert pdf_path is not None, "special_tokens_openai.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) > 0, "Should detect OpenAI special tokens"
        
        # Check for OpenAI-specific patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        openai_patterns = ["openai_im_start", "openai_im_end", "openai_endoftext",
                          "openai_fim_prefix", "openai_fim_middle", "openai_fim_suffix"]
        
        detected_openai = [p for p in pattern_names if p in openai_patterns]
        print(f"\nDetected OpenAI tokens: {detected_openai}")
        
        assert len(detected_openai) > 0, "Should detect OpenAI-specific tokens"
    
    def test_mistral_tokens_detected(self):
        """Test that Mistral model tokens are detected."""
        pdf_path = self.get_test_pdf_path("special_tokens_mistral.pdf")
        assert pdf_path is not None, "special_tokens_mistral.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) > 0, "Should detect Mistral special tokens"
        
        # Check for Mistral-specific patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        mistral_patterns = ["mistral_inst_start", "mistral_inst_end", "mistral_s_inst", "mistral_eos"]
        
        detected_mistral = [p for p in pattern_names if p in mistral_patterns]
        print(f"\nDetected Mistral tokens: {detected_mistral}")
        
        assert len(detected_mistral) > 0, "Should detect Mistral-specific tokens"
    
    def test_combined_tokens_detected(self):
        """Test that mixed tokens from multiple models are detected."""
        pdf_path = self.get_test_pdf_path("special_tokens_combined.pdf")
        assert pdf_path is not None, "special_tokens_combined.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) >= 5, f"Should detect multiple model tokens, found {len(prompt_findings)}"
        
        # Check for tokens from different models
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        
        # Count different model families
        llama_found = any("llama_" in p for p in pattern_names)
        openai_found = any("openai_" in p or "phi_" in p for p in pattern_names)
        mistral_found = any("mistral_" in p for p in pattern_names)
        generic_found = any("special_" in p for p in pattern_names)
        
        print(f"\nDetected tokens from:")
        print(f"  Llama: {llama_found}")
        print(f"  OpenAI/Phi: {openai_found}")
        print(f"  Mistral: {mistral_found}")
        print(f"  Generic: {generic_found}")
        
        models_detected = sum([llama_found, openai_found, mistral_found, generic_found])
        assert models_detected >= 2, "Should detect tokens from multiple model families"
    
    def test_special_token_patterns_loaded(self):
        """Test that all special token patterns are loaded."""
        detector = PromptDetector(self.get_test_pdf_path("low_contrast.pdf"))
        
        # Verify special token patterns are loaded
        expected_patterns = [
            # Llama
            "llama_begin_text", "llama_eot_id", "llama_start_header", "llama_end_header",
            "llama_end_text", "llama_system", "llama_user", "llama_assistant",
            # OpenAI
            "openai_im_start", "openai_im_end", "openai_endoftext",
            "openai_fim_prefix", "openai_fim_middle", "openai_fim_suffix",
            # Mistral
            "mistral_inst_start", "mistral_inst_end", "mistral_s_inst", "mistral_eos",
            # Phi
            "phi_inst_start", "phi_inst_end", "phi_system", "phi_user", 
            "phi_assistant", "phi_end",
            # Generic
            "special_bos", "special_eos", "special_sep", "special_pad",
            "special_unk", "special_mask"
        ]
        
        for pattern_name in expected_patterns:
            assert pattern_name in detector.all_patterns, \
                f"Special token pattern '{pattern_name}' should be loaded"
        
        print(f"\n✓ All {len(expected_patterns)} special token patterns successfully loaded")
    
    def test_special_tokens_high_severity(self):
        """Test that all special token findings are HIGH severity."""
        test_pdfs = [
            "special_tokens_llama.pdf",
            "special_tokens_openai.pdf",
            "special_tokens_mistral.pdf",
            "special_tokens_combined.pdf"
        ]
        
        for pdf_name in test_pdfs:
            pdf_path = self.get_test_pdf_path(pdf_name)
            if pdf_path is None:
                pytest.skip(f"{pdf_name} not found")
                continue
            
            detector = PromptDetector(pdf_path)
            findings = detector.detect()
            
            prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
            
            # All special token findings should be HIGH severity
            for finding in prompt_findings:
                assert finding.severity == Severity.HIGH, \
                    f"{pdf_name}: All special token findings should be HIGH severity"
    
    def test_token_metadata_completeness(self):
        """Test that detected tokens have complete metadata."""
        pdf_path = self.get_test_pdf_path("special_tokens_llama.pdf")
        assert pdf_path is not None, "special_tokens_llama.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        assert len(prompt_findings) > 0, "Should have findings to test"
        
        # Check metadata completeness
        for finding in prompt_findings:
            metadata = finding.metadata
            assert metadata is not None, "Finding should have metadata"
            
            # Required metadata fields
            required_fields = ["pattern_name", "matched_text", "context", "rule"]
            for field in required_fields:
                assert field in metadata, f"Metadata should contain '{field}'"
            
            # Verify context contains the matched text
            assert metadata["matched_text"] in metadata["context"], \
                "Context should contain the matched text"
    
    def test_begin_of_text_token(self):
        """Test specific detection of <|begin_of_text|> token."""
        pdf_path = self.get_test_pdf_path("special_tokens_llama.pdf")
        assert pdf_path is not None, "special_tokens_llama.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        
        # Look for begin_of_text pattern
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        
        assert "llama_begin_text" in pattern_names, \
            "Should detect <|begin_of_text|> token"
    
    def test_fim_tokens_detection(self):
        """Test detection of Fill-in-Middle (FIM) tokens."""
        pdf_path = self.get_test_pdf_path("special_tokens_openai.pdf")
        assert pdf_path is not None, "special_tokens_openai.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        
        # Look for FIM patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        fim_patterns = ["openai_fim_prefix", "openai_fim_middle", "openai_fim_suffix"]
        
        detected_fim = [p for p in pattern_names if p in fim_patterns]
        
        if detected_fim:
            print(f"\nDetected FIM tokens: {detected_fim}")
            assert len(detected_fim) > 0, "Should detect FIM tokens"
    
    def test_generic_special_tokens(self):
        """Test detection of generic special tokens like BOS, EOS, etc."""
        pdf_path = self.get_test_pdf_path("special_tokens_combined.pdf")
        assert pdf_path is not None, "special_tokens_combined.pdf should exist"
        
        detector = PromptDetector(pdf_path)
        findings = detector.detect()
        
        prompt_findings = [f for f in findings if f.finding_type == FindingType.PROMPT_INJECTION_JAILBREAK]
        
        # Look for generic patterns
        pattern_names = [f.metadata.get("pattern_name") for f in prompt_findings if f.metadata]
        generic_patterns = ["special_bos", "special_eos", "special_unk", "special_pad", "special_mask"]
        
        detected_generic = [p for p in pattern_names if p in generic_patterns]
        
        if detected_generic:
            print(f"\nDetected generic tokens: {detected_generic}")
