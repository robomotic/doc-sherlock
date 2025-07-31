# Doc-Sherlock

[![GitHub stars](https://img.shields.io/github/stars/robomotic/doc-sherlock.svg?style=social)](https://github.com/robomotic/doc-sherlock/stargazers)
[![PyPI version](https://badge.fury.io/py/doc-sherlock.svg)](https://badge.fury.io/py/doc-sherlock)
[![Tests](https://github.com/robomotic/doc-sherlock/workflows/Tests/badge.svg)](https://github.com/robomotic/doc-sherlock/actions)
[![Coverage Status](https://coveralls.io/repos/github/robomotic/doc-sherlock/badge.svg?branch=main)](https://coveralls.io/github/robomotic/doc-sherlock?branch=main)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Doc-Sherlock is a security tool designed to identify hidden text in PDF documents that could be used for prompt injection attacks against LLM systems. This tool helps security teams detect common techniques used to hide malicious content from human reviewers while remaining accessible to LLM parsers.

## The Problem: Hidden Text in PDFs

Attackers can exploit LLM systems by hiding text in PDFs that is:
- Invisible to human reviewers
- Parsed and processed by LLM systems
- Designed to inject malicious prompts or instructions

These attacks can lead to prompt injection, data leakage, or manipulation of LLM outputs.

The related technique is the [l ](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) from OWASP top 10 for LLMs, which states that "LLMs can be tricked into executing malicious code or commands by embedding them in seemingly innocuous text." 
## Features

Doc-Sherlock implements multiple detection strategies to identify hidden content:

### 1. Low Contrast Detection
- Identifies text with colors too similar to the background (e.g., white text on white background)
- Calculates contrast ratios using WCAG standards
- Flags text that falls below configurable thresholds

### 2. Tiny Font Detection
- Identifies text with abnormally small font sizes
- Configurable minimum size thresholds (default: 4pt)
- Detects text that would be illegible to humans

### 3. Boundary Detection
- Identifies text positioned outside normal page boundaries
- Detects content placed beyond page margins or viewport
- Flags text that would be invisible when viewing the document normally

### 4. Opacity Detection
- Identifies text with low opacity/transparency settings
- Detects nearly invisible text (e.g., 1-10% opacity)
- Analyzes PDF content streams for transparency operators

### 5. Layer Detection
- Identifies content in hidden PDF layers (Optional Content Groups)
- Detects layers with suspicious names or hidden by default
- Analyzes PDF structure for layer manipulation

### 6. Obscured Text Detection
- Identifies text hidden behind images, shapes, or other elements
- Detects z-ordering manipulation to obscure content
- Compares visual rendering with extracted text

### 7. Metadata Analysis
- Identifies suspicious content in PDF metadata fields
- Detects potential prompt injection attempts in document properties
- Flags unusually large metadata strings

### 8. Rendering Discrepancy Detection
- Compares visual rendering with extracted text content
- Uses OCR to identify differences between what's visible and what's present
- Detects sophisticated hiding techniques

### 9. Encoding Anomaly Detection
- Identifies unusual encoding patterns in PDF content
- Detects obfuscated text and operators
- Flags embedded files and suspicious structures

## Installation

### From PyPI

```bash
pip install doc-sherlock
```

### From Source

```bash
git clone https://github.com/example/doc-sherlock.git
cd doc-sherlock
pip install -e .
```

### Automatic Installation with System Dependencies

For Ubuntu/Debian systems, you can automatically install both Doc-Sherlock and its system dependencies using the following script:

```bash
#!/bin/bash
# Install Tesseract OCR system dependency
sudo apt-get update && sudo apt-get install -y tesseract-ocr

# Install Doc-Sherlock
pip install doc-sherlock

# Or if installing from source
# cd path/to/doc-sherlock
# pip install -e .
```


### Dependencies

Doc-Sherlock requires:
- Python 3.8+
- Tesseract OCR (for rendering discrepancy detection)

#### REST API (FastAPI) Support

To use the REST API server, you need the `fastapi` and `uvicorn` packages. These are included in the `dev` extra requirements:

```bash
pip install -e .[dev]
```

This will install all development dependencies, including FastAPI and Uvicorn, which are required to run the REST API server.

#### Running the REST API Server

After installing the dev dependencies, you can start the REST API server with:

```bash
doc-sherlock rest_service
# or, if not installed as a script:
python -m doc_sherlock.cli rest_service
```

This will start a FastAPI server (default: http://127.0.0.1:8000) with a `/analyze` POST endpoint. You can send a PDF file to this endpoint and receive the findings as a JSON response.

**Example using curl:**

```bash
curl -F "file=@path/to/document.pdf" http://127.0.0.1:8000/analyze
```

---

#### Installing Tesseract OCR Manually

Tesseract OCR is required for the rendering discrepancy detection feature, which compares visual content with extracted text. Without it, some detection methods will be disabled or will report warnings.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

**Verify Installation:**
```bash
tesseract --version
```

#### Testing Tesseract Installation

After installing Tesseract OCR, you should see the rendering discrepancy detection working properly. When analyzing a test PDF like `tests/data/tiny_font.pdf`, you should see findings like:

```
[HIGH] Page contains more text in PDF than visible through OCR (Page 1)
```

If you don't see this finding or see warnings about Tesseract not being installed, check your installation.

## Usage

### Command Line

```bash
# Basic usage: Analyze a single PDF file
doc-sherlock analyze path/to/your/document.pdf

# Customize detection thresholds
doc-sherlock analyze --min-contrast 4.5 --min-font-size 4 --min-opacity 0.3 document.pdf

# Output detailed report in JSON format
doc-sherlock analyze --output-format json --output report.json document.pdf

# Analyze a directory of PDFs recursively
doc-sherlock analyze --recursive path/to/pdf/directory/

# Enable verbose output
doc-sherlock analyze --verbose document.pdf

# Show warnings (warnings are hidden by default to reduce noise)
doc-sherlock analyze --show-warnings document.pdf

# Combine options
doc-sherlock analyze --show-warnings --verbose --min-font-size 3 document.pdf
```

### Python API

```python
from doc_sherlock import PDFAnalyzer

# Create an analyzer with custom configuration
config = {
    "min_contrast_ratio": 4.5,  # WCAG AA standard
    "min_font_size": 4.0,      # Minimum font size in points
    "min_opacity": 0.3,        # Minimum opacity (0.0-1.0)
}
analyzer = PDFAnalyzer("path/to/document.pdf", config)

# Run all detectors
results = analyzer.run_all_detectors()

# Print a summary of findings
print(results.summary())

# Access individual findings
for finding in results.findings:
    print(f"{finding.finding_type.value}: {finding.description} (Severity: {finding.severity.value})")
    if finding.text_content:
        print(f"Text: {finding.text_content}")

# Run specific detectors
contrast_results = analyzer.detect_low_contrast()
font_results = analyzer.detect_tiny_font()

# Export results to JSON
results.save_json("report.json")

# Analyze a directory of PDFs
dir_results = PDFAnalyzer.analyze_directory("/path/to/pdfs/", recursive=True, config=config)
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/example/doc-sherlock.git
cd doc-sherlock

# Create and activate a virtual environment
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
# venv\Scripts\activate

# Install basic package with dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Install test dependencies
pip install -e ".[test]"

# Install all dependencies (dev and test)
pip install -e ".[dev,test]"
```

### Dependencies Overview

#### Core Dependencies
- `pypdf`: PDF parsing and manipulation
- `pdfminer.six`: Text extraction with formatting details
- `pikepdf`: Low-level PDF structure analysis
- `pdfplumber`: Text extraction with position information
- `pillow`: Image processing
- `pytesseract`: OCR capabilities (requires Tesseract to be installed)
- `colorama`: Terminal color output
- `click`: Command-line interface

#### Development Dependencies
- `pytest`: Testing framework
- `pytest-cov`: Test coverage reporting
- `black`: Code formatting
- `isort`: Import sorting
- `flake8`: Linting

#### Test Dependencies
- `fpdf`: PDF generation for tests
- `reportlab`: PDF generation with advanced features for tests

### Using the CLI Tool After Installation

After installing Doc-Sherlock with `pip install -e .`, you can use the command-line tool as follows:

```bash
# Analyze a PDF file
doc-sherlock analyze path/to/your/document.pdf

# Analyze a test PDF
doc-sherlock analyze tests/data/tiny_font.pdf

# Show warnings during analysis (warnings are hidden by default)
doc-sherlock analyze --show-warnings path/to/your/document.pdf

# Get help on available commands
doc-sherlock --help
```

> **Note**: The command is `doc-sherlock` (not `dock-sherlock`)

### Running Tests

Doc-Sherlock includes a comprehensive test suite with test PDFs that simulate various hiding techniques:

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=doc_sherlock

# Run specific test categories
python -m pytest tests/test_contrast_detector.py
```

The test suite generates test PDFs using ReportLab and validates that each detector correctly identifies the corresponding hiding technique.

## Security Considerations

- Doc-Sherlock is designed as a detection tool, not a guarantee of security
- False positives and false negatives are possible
- Always combine with other security measures when processing PDFs in LLM pipelines
- Consider using PDF sanitization tools alongside Doc-Sherlock

## Example of practical attacks

For more information on practical attacks, you can visit the following link:

https://kai-greshake.de/posts/inject-my-pdf/

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

AGPL 3.0 License. See LICENSE.txt for details.
