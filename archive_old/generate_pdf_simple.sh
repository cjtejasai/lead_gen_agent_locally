#!/bin/bash
# Simple PDF generation script (alternative method)

echo "AYKA Documentation PDF Generator"
echo "================================="
echo ""

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "Error: Pandoc is not installed"
    echo ""
    echo "Install with:"
    echo "  macOS: brew install pandoc"
    echo "  Linux: sudo apt-get install pandoc"
    echo ""
    exit 1
fi

# Create output directory
mkdir -p pdfs

# Convert each markdown file
echo "Converting markdown files to PDF..."
echo ""

if [ -f "ARCHITECTURE.md" ]; then
    echo "📄 Converting ARCHITECTURE.md..."
    pandoc ARCHITECTURE.md -o pdfs/AYKA_Architecture.pdf \
        -V geometry:margin=1in \
        -V fontsize=11pt \
        --highlight-style=tango
    echo "✓ Generated: pdfs/AYKA_Architecture.pdf"
fi

if [ -f "DEPLOYMENT_PLAN.md" ]; then
    echo "📄 Converting DEPLOYMENT_PLAN.md..."
    pandoc DEPLOYMENT_PLAN.md -o pdfs/AYKA_Deployment_Plan.pdf \
        -V geometry:margin=1in \
        -V fontsize=11pt \
        --highlight-style=tango
    echo "✓ Generated: pdfs/AYKA_Deployment_Plan.pdf"
fi

if [ -f "ROADMAP.md" ]; then
    echo "📄 Converting ROADMAP.md..."
    pandoc ROADMAP.md -o pdfs/AYKA_Roadmap.pdf \
        -V geometry:margin=1in \
        -V fontsize=11pt \
        --highlight-style=tango
    echo "✓ Generated: pdfs/AYKA_Roadmap.pdf"
fi

if [ -f "CLAUDE.md" ]; then
    echo "📄 Converting CLAUDE.md..."
    pandoc CLAUDE.md -o pdfs/AYKA_Agent_System.pdf \
        -V geometry:margin=1in \
        -V fontsize=11pt \
        --highlight-style=tango
    echo "✓ Generated: pdfs/AYKA_Agent_System.pdf"
fi

echo ""
echo "================================="
echo "✓ PDF generation complete!"
echo ""
echo "📁 Files saved in: pdfs/"
ls -lh pdfs/*.pdf 2>/dev/null || echo "No PDFs generated"