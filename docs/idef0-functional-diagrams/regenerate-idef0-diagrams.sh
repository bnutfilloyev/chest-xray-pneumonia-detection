#!/bin/bash

# Script to regenerate all IDEF0 functional model diagrams from Mermaid source files
# Usage: ./regenerate-idef0-diagrams.sh
# 
# Quality Settings:
# - Width: 2400px, Height: 1800px for high resolution
# - Scale: 2x for crisp rendering on high-DPI displays
# - Custom Mermaid and Puppeteer configurations for optimal quality
# - Dark theme with transparent background

echo "🎨 Regenerating High-Quality IDEF0 Functional Diagrams..."

# Check if mermaid-cli is installed
if ! command -v mmdc &> /dev/null; then
    echo "❌ Mermaid CLI not found. Installing..."
    npm install -g @mermaid-js/mermaid-cli
fi

# Navigate to diagrams directory
cd "$(dirname "$0")"

# Array of IDEF0 diagram names
diagrams=(
    "01-context-diagram-a0"
    "02-a0-decomposition"
    "03-a1-manage-patient-data"
    "04-a2-process-medical-images"
    "05-a3-perform-ai-diagnosis"
    "06-a4-generate-reports-analytics"
    "07-a5-security-compliance"
)

# Generate each diagram with high quality settings
for diagram in "${diagrams[@]}"; do
    echo "🔄 Generating high-quality ${diagram}.png..."
    mmdc -i "${diagram}.mmd" -o "${diagram}.png" \
        --theme dark \
        --backgroundColor transparent \
        --width 2400 \
        --height 1800 \
        --scale 2 \
        --configFile mermaid-config.json \
        --puppeteerConfigFile puppeteer-config.json
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully generated ${diagram}.png"
    else
        echo "❌ Failed to generate ${diagram}.png"
        exit 1
    fi
done

echo ""
echo "🎉 All IDEF0 functional diagrams regenerated successfully!"
echo ""
echo "📊 Generated files:"
ls -la *.png | awk '{printf "   %s (%s bytes)\n", $9, $5}'
