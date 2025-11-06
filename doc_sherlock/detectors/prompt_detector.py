"""
Detector for identifying prompt injection and jailbreak attempts in PDF text content.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import pdfplumber

from ..findings import Finding, FindingType, Severity
from .base_detector import BaseDetector

logger = logging.getLogger(__name__)


class PromptDetector(BaseDetector):
    """Detector for identifying prompt injection and jailbreak attempts."""
    
    # PromptInjectionJailbreak rule patterns
    # Based on YARA-style rule converted to regex patterns
    JAILBREAK_PATTERNS = {
        "new_instruction": re.compile(r"new instruction", re.IGNORECASE),
        "previous": re.compile(r"previous instructions", re.IGNORECASE),
        "ignore_above": re.compile(r"ignore all the instructions above", re.IGNORECASE),
        "forget": re.compile(r"forget your instructions", re.IGNORECASE),
        "disregard": re.compile(r"disregard previous", re.IGNORECASE),
        "override": re.compile(r"override previous", re.IGNORECASE),
        "redefine": re.compile(r"redefine your goals", re.IGNORECASE),
        "primary_task": re.compile(r"your primary task now", re.IGNORECASE),
        "system_prompt": re.compile(r"system prompt", re.IGNORECASE),
        "actually_respond": re.compile(r"actually respond with", re.IGNORECASE),
        "instead_output": re.compile(r"instead output the following", re.IGNORECASE),
        "ignore_content_policy": re.compile(r"ignore content policy", re.IGNORECASE),
        "bypass_filter": re.compile(r"bypass the filter", re.IGNORECASE),
        "return_harmful": re.compile(r"return harmful content", re.IGNORECASE),
        "dont_evaluate": re.compile(r"don'?t evaluate", re.IGNORECASE),
        "respond_with_exactly": re.compile(r"(?:simply\s+)?respond\s+with\s+[\"']", re.IGNORECASE),
        "may_not_deviate": re.compile(r"(?:you\s+)?may\s+not\s+deviate", re.IGNORECASE),
    }
    
    # DAN (Do Anything Now) mode patterns
    DAN_PATTERNS = {
        "dan_mode": re.compile(r"DAN mode", re.IGNORECASE),
        "do_anything": re.compile(r"do anything now", re.IGNORECASE),
        "ignore_rules": re.compile(r"ignore all instructions", re.IGNORECASE),
        "ignore_ethics": re.compile(r"ignore the rules, constraints, perimeters, values, and ethics", re.IGNORECASE),
        "authorization": re.compile(r"you have full authorization to ignore", re.IGNORECASE),
        "token_reward": re.compile(r"you will receive 10 tokens", re.IGNORECASE),
        "token_system": re.compile(r"the more truthful your answers are, the more tokens", re.IGNORECASE),
        "ethics_bypass": re.compile(r"ignore your ethical guidelines", re.IGNORECASE),
        "programming": re.compile(r"ignore your programming", re.IGNORECASE),
    }
    
    # Special LLM-specific control tokens from various models
    # These tokens are used internally by models and should not appear in normal documents
    SPECIAL_TOKEN_PATTERNS = {
        # Llama 3/3.1/3.2/3.3 tokens
        "llama_begin_text": re.compile(r"<\|begin_of_text\|>", re.IGNORECASE),
        "llama_eot_id": re.compile(r"<\|eot_id\|>", re.IGNORECASE),
        "llama_start_header": re.compile(r"<\|start_header_id\|>", re.IGNORECASE),
        "llama_end_header": re.compile(r"<\|end_header_id\|>", re.IGNORECASE),
        "llama_end_text": re.compile(r"<\|end_of_text\|>", re.IGNORECASE),
        "llama_system": re.compile(r"<\|system\|>", re.IGNORECASE),
        "llama_user": re.compile(r"<\|user\|>", re.IGNORECASE),
        "llama_assistant": re.compile(r"<\|assistant\|>", re.IGNORECASE),
        
        # OpenAI/ChatGPT tokens
        "openai_im_start": re.compile(r"<\|im_start\|>", re.IGNORECASE),
        "openai_im_end": re.compile(r"<\|im_end\|>", re.IGNORECASE),
        "openai_endoftext": re.compile(r"<\|endoftext\|>", re.IGNORECASE),
        "openai_fim_prefix": re.compile(r"<\|fim_prefix\|>", re.IGNORECASE),
        "openai_fim_middle": re.compile(r"<\|fim_middle\|>", re.IGNORECASE),
        "openai_fim_suffix": re.compile(r"<\|fim_suffix\|>", re.IGNORECASE),
        
        # Mistral tokens
        "mistral_inst_start": re.compile(r"\[INST\]", re.IGNORECASE),
        "mistral_inst_end": re.compile(r"\[/INST\]", re.IGNORECASE),
        "mistral_s_inst": re.compile(r"<s>\[INST\]", re.IGNORECASE),
        "mistral_eos": re.compile(r"</s>", re.IGNORECASE),
        
        # Claude/Anthropic tokens
        "claude_human": re.compile(r"\n\nHuman:", re.IGNORECASE),
        "claude_assistant": re.compile(r"\n\nAssistant:", re.IGNORECASE),
        
        # Phi tokens
        "phi_inst_start": re.compile(r"<\|im_start\|>", re.IGNORECASE),
        "phi_inst_end": re.compile(r"<\|im_end\|>", re.IGNORECASE),
        "phi_system": re.compile(r"<\|system\|>", re.IGNORECASE),
        "phi_user": re.compile(r"<\|user\|>", re.IGNORECASE),
        "phi_assistant": re.compile(r"<\|assistant\|>", re.IGNORECASE),
        "phi_end": re.compile(r"<\|end\|>", re.IGNORECASE),
        
        # Generic special tokens that might appear
        "special_bos": re.compile(r"<\|BOS\|>", re.IGNORECASE),
        "special_eos": re.compile(r"<\|EOS\|>", re.IGNORECASE),
        "special_sep": re.compile(r"<\|SEP\|>", re.IGNORECASE),
        "special_pad": re.compile(r"<\|PAD\|>", re.IGNORECASE),
        "special_unk": re.compile(r"<\|UNK\|>", re.IGNORECASE),
        "special_mask": re.compile(r"<\|MASK\|>", re.IGNORECASE),
        
        # Square bracket format tokens (common in prompt engineering)
        "bracket_system": re.compile(r"\[system\]", re.IGNORECASE),
        "bracket_user": re.compile(r"\[user\]", re.IGNORECASE),
        "bracket_assistant": re.compile(r"\[assistant\]", re.IGNORECASE),
        "bracket_inst": re.compile(r"\[INST\]", re.IGNORECASE),
        "bracket_inst_end": re.compile(r"\[/INST\]", re.IGNORECASE),
        "bracket_rest_of_document": re.compile(r"\[rest-of-document\]", re.IGNORECASE),
    }
    
    def __init__(self, pdf_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the prompt detector.
        
        Args:
            pdf_path: Path to the PDF file to analyze
            config: Optional configuration options
        """
        super().__init__(pdf_path, config)
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration with default values."""
        # Allow custom patterns to be added via config
        self.custom_patterns = self.config.get("custom_patterns", {})
        
        # Combine default patterns (jailbreak + DAN + special tokens)
        self.all_patterns = {**self.JAILBREAK_PATTERNS, **self.DAN_PATTERNS, **self.SPECIAL_TOKEN_PATTERNS}
        for name, pattern_str in self.custom_patterns.items():
            self.all_patterns[name] = re.compile(pattern_str, re.IGNORECASE)
        
        # Context window for extracting surrounding text
        self.context_chars = self.config.get("context_chars", 100)
        
    def _extract_text_blocks(self) -> List[Tuple[int, str]]:
        """
        Extract all text blocks from the PDF.
        
        Returns:
            List of tuples containing (page_number, text_content)
        """
        text_blocks = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        text = page.extract_text()
                        if text:
                            text_blocks.append((page_num, text))
                    except Exception as e:
                        self.logger.warning(f"Error extracting text from page {page_num}: {e}")
                        continue
        except Exception as e:
            self.logger.error(f"Error opening PDF {self.pdf_path}: {e}")
            
        return text_blocks
    
    def _extract_context(self, text: str, match_start: int, match_end: int) -> str:
        """
        Extract context around a matched pattern.
        
        Args:
            text: Full text content
            match_start: Start position of the match
            match_end: End position of the match
            
        Returns:
            Context string with the match highlighted
        """
        context_start = max(0, match_start - self.context_chars)
        context_end = min(len(text), match_end + self.context_chars)
        
        context = text[context_start:context_end]
        
        # Clean up whitespace and newlines for display
        context = ' '.join(context.split())
        
        # Truncate if still too long
        if len(context) > 300:
            context = context[:300] + "..."
            
        return context
    
    def _check_jailbreak_patterns(
        self, 
        page_num: int, 
        text: str
    ) -> List[Finding]:
        """
        Check text for jailbreak/injection patterns.
        
        Args:
            page_num: Page number being analyzed
            text: Text content to check
            
        Returns:
            List of findings for matched patterns
        """
        findings = []
        
        for pattern_name, pattern in self.all_patterns.items():
            matches = list(pattern.finditer(text))
            
            for match in matches:
                matched_text = match.group(0)
                context = self._extract_context(text, match.start(), match.end())
                
                # Create finding with CRITICAL severity as these are severe security issues
                finding = self.create_finding(
                    finding_type=FindingType.PROMPT_INJECTION_JAILBREAK,
                    severity=Severity.CRITICAL,
                    description=(
                        f"Potential prompt injection/jailbreak attempt detected: "
                        f"'{matched_text}' (pattern: {pattern_name})"
                    ),
                    page_number=page_num,
                    metadata={
                        "pattern_name": pattern_name,
                        "matched_text": matched_text,
                        "context": context,
                        "rule": "PromptInjectionJailbreak",
                        "rule_version": "1.0.0",
                        "rule_author": "Thomas Roccia",
                        "category": "jailbreak/injection"
                    }
                )
                findings.append(finding)
        
        return findings
    
    def detect(self) -> List[Finding]:
        """
        Run the detector and return any findings.
        
        Checks all text blocks in the PDF for prompt injection and jailbreak patterns
        based on the PromptInjectionJailbreak rule.
        
        Returns:
            List of findings from the detector
        """
        findings = []
        
        self.logger.info(f"Starting prompt injection detection on {self.pdf_path}")
        
        # Extract all text blocks from the PDF
        text_blocks = self._extract_text_blocks()
        
        if not text_blocks:
            self.logger.warning(f"No text content found in {self.pdf_path}")
            return findings
        
        # Check each text block for patterns
        for page_num, text in text_blocks:
            page_findings = self._check_jailbreak_patterns(page_num, text)
            findings.extend(page_findings)
        
        self.logger.info(
            f"Prompt injection detection complete: found {len(findings)} potential issues"
        )
        
        return findings
