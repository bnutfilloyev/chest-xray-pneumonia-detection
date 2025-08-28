#!/bin/bash

# Script to regenerate all architecture diagrams from Mermaid source files
# Usage: ./regenerate-diagrams.sh
# 
# Quality Settings:
# - Width: 2400px, Height: 1800px for high resolution
# - Scale: 2x for crisp rendering on high-DPI displays
# - Custom Mermaid and Puppeteer configurations for optimal quality
# - Dark theme with transparent background

echo "🎨 Regenerating High-Quality Architecture Diagrams..."

# Check if mermaid-cli is installed
if ! command -v mmdc &> /dev/null; then
    echo "❌ Mermaid CLI not found. Installing..."
    npm install -g @mermaid-js/mermaid-cli
fi

# Navigate to diagrams directory
cd "$(dirname "$0")"

# Array of diagram names
diagrams=(
    "01-technical-architecture"
    "02-deployment-architecture"
    "03-data-flow-architecture"
    "04-cicd-pipeline"
    "05-security-architecture"
    "06-monitoring-observability"
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
echo "🎉 All diagrams regenerated successfully!"
echo ""
echo "📊 Generated files:"
ls -la *.png | awk '{printf "   %s (%s bytes)\n", $9, $5}'
