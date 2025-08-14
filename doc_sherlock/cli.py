"""
Command-line interface for Doc-Sherlock.
"""

import sys
import os
import json
import logging
import click
from pathlib import Path
from typing import Dict, List, Any, Optional
from colorama import init, Fore, Style

# FastAPI imports for REST service
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn

from .analyzer import PDFAnalyzer
from .findings import Finding, FindingType, Severity, AnalysisResults

# Initialize colorama
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_finding(finding, show_location=True):
    """Print a finding with color-coded severity."""
    severity_colors = {
        Severity.LOW: Fore.GREEN,
        Severity.MEDIUM: Fore.YELLOW,
        Severity.HIGH: Fore.RED,
        Severity.CRITICAL: Fore.RED + Style.BRIGHT
    }

    color = severity_colors.get(finding.severity, '')
    print(f"{color}Finding [{finding.finding_type}] - Severity: {finding.severity}{Style.RESET_ALL}")
    print(f"Page {finding.page_number}: {finding.description}")
    
    if show_location and finding.location:
        print("Location (normalized coordinates):")
        for key, value in finding.location.items():
            print(f"  {key}: {value:.3f}")
    print()


@click.group()
def cli():
    """Doc-Sherlock: Detect hidden text and potential prompt injection vectors in PDF files."""


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Save results to JSON file')
@click.option('--markdown', '-m', type=click.Path(), help='Save extracted PDF content as Markdown file')
@click.option('--recursive', '-r', is_flag=True, help='Recursively analyze PDFs in directories')
@click.option('--no-color', is_flag=True, help='Disable colored output')
@click.option('--quiet', '-q', is_flag=True, help='Only output machine-readable results')
@click.option('--extract-only', is_flag=True, help='Only extract PDF content (no detections)')
@click.option('--extract-tables', is_flag=True, help='Extract tables as CSV files (requires tabula-py)')
def analyze(path, output, markdown, recursive, no_color, quiet, extract_only, extract_tables):
    """Analyze PDF files for hidden text and potential prompt injection vectors. Optionally export PDF content as Markdown, and extract tables as CSV."""
    if no_color:
        # Disable colorama colors
        Fore.GREEN = Fore.YELLOW = Fore.RED = Style.BRIGHT = Style.RESET_ALL = ''

    try:
        path = Path(path)
        if path.is_file():
            if path.suffix.lower() != '.pdf':
                logger.error("Not a PDF file: %s", path)
                sys.exit(1)
            pdf_files = [str(path)]
        else:
            pdf_files = [str(p) for p in path.glob('**/*.pdf')] if recursive else [str(p) for p in path.glob('*.pdf')]

        if not pdf_files:
            logger.warning("No PDF files found to analyze")
            return

        # Only extract content, skip detections
        if extract_only or markdown or extract_tables:
            if markdown:
                try:
                    from PyPDF2 import PdfReader
                except ImportError:
                    logger.error("PyPDF2 is required for Markdown export. Please install it with 'pip install PyPDF2'.")
                    sys.exit(1)
                md_path = Path(markdown)
                with open(md_path, 'w', encoding='utf-8') as md_file:
                    for pdf_path in pdf_files:
                        reader = PdfReader(pdf_path)
                        md_file.write(f'# {os.path.basename(pdf_path)}\n\n')
                        for i, page in enumerate(reader.pages):
                            text = page.extract_text() or ''
                            md_file.write(f'## Page {i+1}\n\n{text}\n\n')
                logger.info(f"Markdown exported to {md_path}")
            if extract_tables:
                try:
                    import tabula
                except ImportError:
                    logger.error("tabula-py is required for table extraction. Please install it with 'pip install tabula-py'.")
                    sys.exit(1)
                for pdf_path in pdf_files:
                    base = os.path.splitext(os.path.basename(pdf_path))[0]
                    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True)
                    for idx, table in enumerate(tables):
                        csv_path = f"{base}_table_{idx+1}.csv"
                        table.to_csv(csv_path, index=False)
                        logger.info(f"Extracted table to {csv_path}")
            return

        # ...existing detection/analysis code...
        if not results:
            logger.warning("No PDF files found to analyze")
            return

        # Print results
        if not quiet:
            total_findings = sum(len(result.findings) for result in results)
            print(f"\nAnalyzed {len(results)} file(s), found {total_findings} potential issues\n")

            for result in results:
                if len(results) > 1:
                    print(f"\nFindings for {result.pdf_path}:")
                for finding in result.findings:
                    print_finding(finding)

        # Save results if requested
        if output:
            output_path = Path(output)
            if len(results) == 1 and output_path.suffix.lower() == '.json':
                # Single file analysis - save direct result
                results[0].save_json(output)
            else:
                # Multiple files or no extension - save array of results
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump([r.to_dict() for r in results], f, indent=2)

        # Save Markdown if requested
        if markdown:
            try:
                from PyPDF2 import PdfReader
            except ImportError:
                logger.error("PyPDF2 is required for Markdown export. Please install it with 'pip install PyPDF2'.")
                sys.exit(1)
            md_path = Path(markdown)
            with open(md_path, 'w', encoding='utf-8') as md_file:
                for pdf_path in pdf_files:
                    reader = PdfReader(pdf_path)
                    md_file.write(f'# {os.path.basename(pdf_path)}\n\n')
                    for i, page in enumerate(reader.pages):
                        text = page.extract_text() or ''
                        md_file.write(f'## Page {i+1}\n\n{text}\n\n')
            logger.info(f"Markdown exported to {md_path}")

    except Exception as e:
        logger.error("Error during analysis: %s", str(e))
        if not quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


# --- FastAPI REST Service Command ---
@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to run the FastAPI server on')
@click.option('--port', default=8000, help='Port to run the FastAPI server on')
def rest_service(host, port):
    """Start a FastAPI REST service for PDF analysis."""
    app = FastAPI(title="Doc-Sherlock REST API")

    @app.post("/analyze")
    async def analyze_pdf(file: UploadFile = File(...)):
        """Analyze a PDF file and return findings as JSON."""
        try:
            # Save uploaded file to a temporary location
            import tempfile
            suffix = Path(file.filename).suffix or ".pdf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await file.read())
                tmp_path = tmp.name

            analyzer = PDFAnalyzer(tmp_path)
            results = analyzer.run_all_detectors()
            # Clean up temp file
            os.remove(tmp_path)

            # Convert findings to dicts for JSON response
            findings_json = [f.to_dict() for f in results.findings]
            return JSONResponse(content={"findings": findings_json})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    print(f"Starting FastAPI server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
