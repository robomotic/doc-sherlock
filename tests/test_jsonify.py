import json
import pytest
from pathlib import Path
from doc_sherlock.analyzer import PDFAnalyzer


def test_findings_json_serialization(tmp_path):
    # Use a sample PDF from the test data directory
    test_pdf = Path(__file__).parent / "data" / "low_contrast.pdf"
    local_path = str(test_pdf)

    try:
        analyzer = PDFAnalyzer(local_path)
        results = analyzer.analyze_file()

        # Run all detectors
        results = analyzer.run_all_detectors()
        
        # Check that results are returned
        assert results is not None
        assert hasattr(results, "findings")
        
        # The test PDF should have findings
        assert len(results.findings) > 0

        json_out = results.to_json()

        assert type(json_out)==str

        json_out = results.to_dict()

        assert type(json_out)==dict

    except Exception as e:
        pytest.fail(f"Analysis failed: {str(e)}")
