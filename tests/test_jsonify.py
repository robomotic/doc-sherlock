import json
import pytest
from pathlib import Path
from doc_sherlock.analyzer import PDFAnalyzer
from doc_sherlock.findings import FindingType, Severity


def test_findings_json_serialization(tmp_path):
    # Use a sample PDF from the test data directory
    test_pdf = Path(__file__).parent / "data" / "low_contrast.pdf"
    local_path = str(test_pdf)

    try:
        analyzer = PDFAnalyzer(local_path)
        results = analyzer.analyze_file()
        
        # Check that results are returned
        assert results is not None
        assert hasattr(results, "findings")
        assert hasattr(results, "actions")
        
        # Test JSON serialization
        json_out = results.to_json()
        assert type(json_out) == str
        
        # Test that JSON is valid
        parsed_json = json.loads(json_out)
        assert "pdf_path" in parsed_json
        assert "findings" in parsed_json
        assert "actions" in parsed_json
        
        # Test dictionary conversion
        dict_out = results.to_dict()
        assert type(dict_out) == dict
        assert "pdf_path" in dict_out
        assert "findings" in dict_out
        assert "actions" in dict_out

    except Exception as e:
        pytest.fail(f"Analysis failed: {str(e)}")


def test_actions_field_logic():
    """Test the actions field logic for different scenarios."""
    from doc_sherlock.findings import AnalysisResults, Finding
    
    # Test empty findings
    results = AnalysisResults("test.pdf", [])
    assert results.actions == "This document is clean"
    
    # Test with prompt injection finding
    prompt_finding = Finding(
        finding_type=FindingType.PROMPT_INJECTION_JAILBREAK,
        severity=Severity.CRITICAL,
        description="Prompt injection detected",
        page_number=1
    )
    results = AnalysisResults("test.pdf", [prompt_finding])
    assert results.actions == "This document should be blocked and reviewed by a human analyst"
    
    # Test with other findings
    other_finding = Finding(
        finding_type=FindingType.LOW_CONTRAST,
        severity=Severity.MEDIUM,
        description="Low contrast detected",
        page_number=1
    )
    results = AnalysisResults("test.pdf", [other_finding])
    assert results.actions == "This document is potentially risky and should be reviewed"
    
    # Test with multiple findings including prompt injection
    results = AnalysisResults("test.pdf", [other_finding, prompt_finding])
    assert results.actions == "This document should be blocked and reviewed by a human analyst"
