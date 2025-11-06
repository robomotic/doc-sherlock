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
        
        # Combine default patterns (jailbreak + DAN)
        self.all_patterns = {**self.JAILBREAK_PATTERNS, **self.DAN_PATTERNS}
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
                
                # Create finding with high severity as these are potential security issues
                finding = self.create_finding(
                    finding_type=FindingType.PROMPT_INJECTION_JAILBREAK,
                    severity=Severity.HIGH,
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
