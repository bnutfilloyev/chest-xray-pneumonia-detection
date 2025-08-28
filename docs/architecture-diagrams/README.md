# 🏗️ Architecture Diagrams

This directory contains PNG versions of all system architecture diagrams for the Pneumonia AI Detection System.

## 📊 Available Diagrams

### 1. Technical Architecture Overview
**File**: `01-technical-architecture.png`
- Shows layered architecture from client to infrastructure
- Includes all major system components and their relationships
- Highlights different tiers: Client, Presentation, Application, Business Logic, Data, and Infrastructure

### 2. Deployment Architecture
**File**: `02-deployment-architecture.png`
- Illustrates deployment strategies across different environments
- Covers Development, Docker Compose, and Production Kubernetes deployments
- Shows scaling and high availability patterns

### 3. Data Flow Architecture
**File**: `03-data-flow-architecture.png`
- Demonstrates microservices-based data flow
- External system integrations (Hospital, PACS, Lab systems)
- AI/ML pipeline for inference and monitoring

### 4. CI/CD Pipeline Architecture
**File**: `04-cicd-pipeline.png`
- Complete CI/CD workflow from source control to production
- Includes build, test, security scanning, and deployment stages
- Multi-environment deployment strategy with monitoring

### 5. Security Architecture
**File**: `05-security-architecture.png`
- Multi-layered security approach
- Network, application, data, and infrastructure security
- HIPAA compliance and audit logging

### 6. Monitoring & Observability Stack
**File**: `06-monitoring-observability.png`
- Comprehensive observability solution
- Metrics collection, logging, tracing, and alerting
- Integration with external notification services

## 🛠️ Generation Details

These diagrams were generated from Mermaid source files using the Mermaid CLI tool with high-quality settings:

```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate high-quality PNG with optimized settings
mmdc -i diagram.mmd -o diagram.png \
    --theme dark \
    --backgroundColor transparent \
    --width 2400 \
    --height 1800 \
    --scale 2 \
    --configFile mermaid-config.json \
    --puppeteerConfigFile puppeteer-config.json
```

### 🎯 Quality Optimizations

- **Resolution**: 2400x1800px for crisp high-resolution output
- **Scale Factor**: 2x for excellent clarity on high-DPI displays  
- **Custom Mermaid Config**: Optimized colors, spacing, and typography
- **Puppeteer Optimization**: Enhanced rendering engine settings
- **Force Device Scale**: 2x scale factor for maximum sharpness

## 🔄 Updating Diagrams

To update any diagram:

1. Edit the corresponding `.mmd` file in this directory
2. Run the Mermaid CLI command to regenerate the PNG
3. The PNG will automatically be referenced in the main documentation

## 📝 Source Files

Each PNG has a corresponding `.mmd` source file:
- `01-technical-architecture.mmd` → `01-technical-architecture.png`
- `02-deployment-architecture.mmd` → `02-deployment-architecture.png`
- `03-data-flow-architecture.mmd` → `03-data-flow-architecture.png`
- `04-cicd-pipeline.mmd` → `04-cicd-pipeline.png`
- `05-security-architecture.mmd` → `05-security-architecture.png`
- `06-monitoring-observability.mmd` → `06-monitoring-observability.png`

## ⚙️ Configuration Files

Quality optimization is achieved through custom configuration files:

- **`mermaid-config.json`**: Mermaid rendering settings (colors, spacing, typography)
- **`puppeteer-config.json`**: Browser engine optimization (scale factor, rendering options)
- **`regenerate-diagrams.sh`**: Main script for generating all diagrams
- **`compare-quality.sh`**: Utility to compare standard vs high-quality output

## 🎨 Styling

All diagrams use high-quality rendering with:
- **Resolution**: 2400x1800px for crisp, detailed output
- **Scale Factor**: 2x for excellent clarity on all displays
- **Theme**: Dark mode for better readability and professional appearance
- **Background**: Transparent for flexible document integration
- **Colors**: Consistent, carefully chosen color scheme across all diagrams
- **Typography**: Optimized font rendering and spacing
- **Icons**: Emoji-based icons for visual clarity and universal understanding

### 📊 Quality Comparison

The current high-quality settings produce images that are 3-8x larger in file size compared to standard settings, with significantly improved:
- Text clarity and readability
- Line sharpness and definition  
- Color depth and consistency
- Overall professional appearance
