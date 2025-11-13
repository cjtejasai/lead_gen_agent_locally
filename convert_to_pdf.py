#!/usr/bin/env python3
"""Simple markdown to PDF converter"""

from markdown_pdf import MarkdownPdf, Section
from pathlib import Path

# Read the markdown file
md_file = Path("ARCHITECTURE.md")
pdf_file = Path("pdfs/AYKA_Architecture.pdf")

# Create pdfs directory
pdf_file.parent.mkdir(exist_ok=True)

# Read content
with open(md_file, 'r') as f:
    content = f.read()

# Create PDF
pdf = MarkdownPdf()
pdf.add_section(Section(content, toc=False))
pdf.meta["title"] = "AYKA Platform Architecture"
pdf.meta["author"] = "AYKA Team"
pdf.save(str(pdf_file))

print(f"✓ PDF generated: {pdf_file}")
print(f"📁 Location: {pdf_file.absolute()}")