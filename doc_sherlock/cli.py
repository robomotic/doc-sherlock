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


def setup_logging(verbose: bool, show_warnings: bool = False) -> None:
    """
    Setup logging based on verbosity level and warning preferences.
    
    Args:
        verbose: Whether to enable verbose logging
        show_warnings: Whether to show warning messages
    """
    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        # Set level based on whether warnings should be shown
        level = logging.WARNING if show_warnings else logging.ERROR
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )


def print_banner() -> None:
    """Print the tool banner."""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   {Fore.WHITE}⠀⠀⢀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{Fore.CYAN}                                    ║
║   {Fore.WHITE}⢰⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{Fore.CYAN}                                    ║
║   {Fore.WHITE}⢸⣿⣿⠿⠿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{Fore.CYAN}                                    ║
║   {Fore.WHITE}⢸⣿⣉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{Fore.CYAN}                                    ║
║   {Fore.WHITE}⠘⠛⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{Fore.CYAN}                                    ║
║                                                               ║
║   {Fore.YELLOW}Doc-Sherlock: PDF Hidden Text & Prompt Injection Detector{Fore.CYAN}    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_summary(results: AnalysisResults) -> None:
    """
    Print a summary of analysis results.
    
    Args:
        results: Analysis results to summarize
    """
    if not results.has_findings():
        print(f"{Fore.GREEN}✓ No suspicious content detected{Style.RESET_ALL}")
        return
        
    # Count findings by severity
    severity_counts = results.severity_counts()
    type_counts = results.type_counts()
    
    # Print summary header
    print(f"\n{Fore.YELLOW}Findings Summary:{Style.RESET_ALL}")
    print(f"Total findings: {len(results.findings)}")
    
    # Print severity counts
    print("\nSeverity counts:")
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
        count = severity_counts[severity]
        if count > 0:
            color = Fore.RED if severity == Severity.CRITICAL else \
                   Fore.MAGENTA if severity == Severity.HIGH else \
                   Fore.YELLOW if severity == Severity.MEDIUM else \
                   Fore.BLUE
            print(f"  {color}• {severity.value.title()}: {count}{Style.RESET_ALL}")
    
    # Print type counts
    print("\nFinding types:")
    for finding_type, count in type_counts.items():
        if count > 0:
            print(f"  • {finding_type.value.replace('_', ' ').title()}: {count}")
    
    # Print top findings
    if results.findings:
        print(f"\n{Fore.YELLOW}Top findings:{Style.RESET_ALL}")
        sorted_findings = sorted(
            results.findings, 
            key=lambda f: ["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(f.severity.value.upper()),
            reverse=True
        )
        
        for i, finding in enumerate(sorted_findings[:10]):
            severity_color = Fore.RED if finding.severity == Severity.CRITICAL else \
                            Fore.MAGENTA if finding.severity == Severity.HIGH else \
                            Fore.YELLOW if finding.severity == Severity.MEDIUM else \
                            Fore.BLUE
                            
            page_info = f" (Page {finding.page_number})" if finding.page_number is not None else ""
            
            print(f"  {i+1}. {severity_color}[{finding.severity.value.upper()}]{Style.RESET_ALL} {finding.description}{page_info}")
            
            # Print text content if available (truncated)
            if finding.text_content:
                text = finding.text_content
                if len(text) > 100:
                    text = text[:97] + "..."
                print(f"     Text: \"{text}\"")
            
        if len(results.findings) > 10:
            print(f"  ... and {len(results.findings) - 10} more findings.")


@click.group()
@click.version_option()
def cli():
    """Doc-Sherlock: A tool to detect hidden text in PDF documents that could be used for prompt injection."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--recursive", "-r", is_flag=True, help="Recursively analyze all PDFs in directory")
@click.option("--min-contrast", type=float, default=4.5, help="Minimum contrast ratio for text (WCAG AA: 4.5)")
@click.option("--min-font-size", type=float, default=4.0, help="Minimum font size in points")
@click.option("--min-opacity", type=float, default=0.3, help="Minimum opacity for text (0.0-1.0)")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Output file path (default: stdout)")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--show-warnings", is_flag=True, help="Show warning messages (hidden by default)")
def analyze(path, recursive, min_contrast, min_font_size, min_opacity, output_format, output, verbose, show_warnings):
    """Analyze PDF file(s) for hidden text and other suspicious content."""
    # Setup logging
    setup_logging(verbose, show_warnings)
    
    # Print banner
    print_banner()
    
    # Prepare configuration
    config = {
        "min_contrast_ratio": min_contrast,
        "min_font_size": min_font_size,
        "min_opacity": min_opacity,
    }
    
    try:
        path = Path(path)
        all_results = []
        
        if path.is_file():
            # Single file
            if not path.suffix.lower() == ".pdf":
                click.echo(f"{Fore.RED}Error: File is not a PDF: {path}{Style.RESET_ALL}")
                sys.exit(1)
                
            click.echo(f"Analyzing PDF: {path}")
            analyzer = PDFAnalyzer(path, config)
            results = analyzer.run_all_detectors()
            all_results.append(results)
            
            # Print summary to console
            print_summary(results)
            
        elif path.is_dir():
            # Directory of files
            click.echo(f"Analyzing PDFs in directory: {path}" + (" (recursive)" if recursive else ""))
            results_list = PDFAnalyzer.analyze_directory(path, recursive=recursive, config=config)
            all_results.extend(results_list)
            
            # Print summary counts
            total_files = len(results_list)
            suspicious_files = sum(1 for r in results_list if r.has_findings())
            
            click.echo(f"\nAnalyzed {total_files} PDF files")
            if suspicious_files > 0:
                click.echo(f"{Fore.YELLOW}Found suspicious content in {suspicious_files} files{Style.RESET_ALL}")
                
                # Print detailed summaries for each suspicious file
                for results in results_list:
                    if results.has_findings():
                        click.echo(f"\n{Fore.CYAN}File: {results.filename}{Style.RESET_ALL}")
                        print_summary(results)
            else:
                click.echo(f"{Fore.GREEN}No suspicious content detected in any files{Style.RESET_ALL}")
        
        # Output results if requested
        if output:
            output_path = Path(output)
            
            if output_format == "json":
                # Output as JSON
                with open(output_path, "w") as f:
                    if len(all_results) == 1:
                        # Single result
                        json.dump(all_results[0].to_dict(), f, indent=2)
                    else:
                        # Multiple results
                        json.dump([r.to_dict() for r in all_results], f, indent=2)
                click.echo(f"\nResults saved to: {output_path}")
            else:
                # Output as text
                with open(output_path, "w") as f:
                    for results in all_results:
                        f.write(results.summary())
                        f.write("\n\n" + "-" * 80 + "\n\n")
                click.echo(f"\nResults saved to: {output_path}")
    
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
