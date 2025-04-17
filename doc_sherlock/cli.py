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
@click.option('--recursive', '-r', is_flag=True, help='Recursively analyze PDFs in directories')
@click.option('--no-color', is_flag=True, help='Disable colored output')
@click.option('--quiet', '-q', is_flag=True, help='Only output machine-readable results')
def analyze(path, output, recursive, no_color, quiet):
    """Analyze PDF files for hidden text and potential prompt injection vectors."""
    if no_color:
        # Disable colorama colors
        Fore.GREEN = Fore.YELLOW = Fore.RED = Style.BRIGHT = Style.RESET_ALL = ''

    try:
        path = Path(path)
        if path.is_file():
            if path.suffix.lower() != '.pdf':
                logger.error("Not a PDF file: %s", path)
                sys.exit(1)
            analyzer = PDFAnalyzer(str(path))
            results = [analyzer.analyze_file()]
        else:
            results = PDFAnalyzer.analyze_directory(str(path), recursive=recursive)

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

    except Exception as e:
        logger.error("Error during analysis: %s", str(e))
        if not quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
