#!/bin/bash

# Script to compare standard vs high-quality diagram generation
# Usage: ./compare-quality.sh [diagram-name]

echo "📊 Diagram Quality Comparison Tool"
echo "=================================="

# Check if diagram name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 [diagram-name]"
    echo "Example: $0 01-technical-architecture"
    echo ""
    echo "Available diagrams:"
    echo "  01-technical-architecture"
    echo "  02-deployment-architecture"
    echo "  03-data-flow-architecture"
    echo "  04-cicd-pipeline"
    echo "  05-security-architecture"
    echo "  06-monitoring-observability"
    exit 1
fi

DIAGRAM_NAME="$1"

# Check if source file exists
if [ ! -f "${DIAGRAM_NAME}.mmd" ]; then
    echo "❌ Source file ${DIAGRAM_NAME}.mmd not found!"
    exit 1
fi

echo "🔄 Generating standard quality version..."
mmdc -i "${DIAGRAM_NAME}.mmd" -o "${DIAGRAM_NAME}-standard.png" \
    --theme dark --backgroundColor transparent

echo "🔄 Generating high quality version..."
mmdc -i "${DIAGRAM_NAME}.mmd" -o "${DIAGRAM_NAME}-hq.png" \
    --theme dark \
    --backgroundColor transparent \
    --width 2400 \
    --height 1800 \
    --scale 2 \
    --configFile mermaid-config.json \
    --puppeteerConfigFile puppeteer-config.json

echo ""
echo "📊 Comparison Results:"
echo "====================="
echo -n "Standard Quality: "
ls -lh "${DIAGRAM_NAME}-standard.png" | awk '{print $5}'
echo -n "High Quality:     "
ls -lh "${DIAGRAM_NAME}-hq.png" | awk '{print $5}'

echo ""
echo "🖼️  Files generated:"
echo "   ${DIAGRAM_NAME}-standard.png (standard quality)"
echo "   ${DIAGRAM_NAME}-hq.png (high quality)"
echo ""
echo "💡 Tip: Open both files to visually compare the quality difference!"
