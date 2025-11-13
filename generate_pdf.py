#!/usr/bin/env python3
"""
Generate PDF documentation from markdown files
"""

import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """Check if required tools are installed"""
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
        print("✓ Pandoc found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Pandoc not found")
        print("\nInstall Pandoc:")
        print("  macOS: brew install pandoc")
        print("  Linux: sudo apt-get install pandoc")
        print("  Windows: Download from https://pandoc.org/installing.html")
        sys.exit(1)

    # Check for LaTeX (optional, for better formatting)
    try:
        subprocess.run(['pdflatex', '--version'], capture_output=True, check=True)
        print("✓ LaTeX found (better formatting)")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("! LaTeX not found (basic formatting will be used)")
        print("  For better PDFs, install: brew install --cask mactex")
        return False

def generate_pdf(markdown_file, output_pdf, use_latex=False):
    """Convert markdown to PDF using pandoc"""

    md_path = Path(markdown_file)
    if not md_path.exists():
        print(f"✗ File not found: {markdown_file}")
        return False

    print(f"\n📄 Converting {markdown_file} → {output_pdf}")

    cmd = [
        'pandoc',
        str(md_path),
        '-o', output_pdf,
        '--pdf-engine=pdflatex' if use_latex else '--pdf-engine=wkhtmltopdf',
        '-V', 'geometry:margin=1in',
        '-V', 'fontsize=11pt',
        '--highlight-style=tango'
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Generated: {output_pdf}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e.stderr.decode()}")
        return False

def main():
    """Generate PDFs for all documentation"""

    print("AYKA Documentation PDF Generator\n")
    print("="*50)

    has_latex = check_dependencies()

    # Files to convert
    docs = [
        ('ARCHITECTURE.md', 'AYKA_Architecture.pdf'),
        ('DEPLOYMENT_PLAN.md', 'AYKA_Deployment_Plan.pdf'),
        ('ROADMAP.md', 'AYKA_Roadmap.pdf'),
        ('CLAUDE.md', 'AYKA_Agent_System.pdf'),
    ]

    success_count = 0

    for md_file, pdf_file in docs:
        if Path(md_file).exists():
            if generate_pdf(md_file, pdf_file, has_latex):
                success_count += 1
        else:
            print(f"⊘ Skipping {md_file} (not found)")

    print("\n" + "="*50)
    print(f"✓ Generated {success_count}/{len(docs)} PDFs")

    if success_count > 0:
        print("\n📁 PDF files created:")
        for _, pdf_file in docs:
            if Path(pdf_file).exists():
                print(f"   - {pdf_file}")

if __name__ == "__main__":
    main()