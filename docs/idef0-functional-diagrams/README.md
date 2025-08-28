# 🏗️ IDEF0 Functional Model Diagrams

This directory contains PNG versions of all IDEF0 functional model diagrams for the Pneumonia AI Detection System. IDEF0 is a function modeling methodology that provides a structured representation of the functions, activities, or processes within the system.

## 📊 Available IDEF0 Diagrams

### 1. Context Diagram (A-0 Level)
**File**: `01-context-diagram-a0.png`
- **Purpose**: Shows the system boundary and external entities
- **Level**: A-0 (highest level)
- **Description**: Pneumonia AI Detection System in its environment
- **External Entities**: Healthcare Professionals, Patients, Medical Standards, ML Models, Reports, Analytics, Security Requirements

### 2. A-0 System Decomposition
**File**: `02-a0-decomposition.png`
- **Purpose**: Breaks down the main system into 5 major functions
- **Level**: A-0 decomposition
- **Functions**: 
  - A-1: Manage Patient Data
  - A-2: Process Medical Images
  - A-3: Perform AI Diagnosis
  - A-4: Generate Reports & Analytics
  - A-5: Ensure Security & Compliance

### 3. A-1: Manage Patient Data
**File**: `03-a1-manage-patient-data.png`
- **Purpose**: Detailed breakdown of patient data management
- **Level**: A-1 decomposition
- **Sub-functions**:
  - A-1.1: Register New Patients
  - A-1.2: Update Patient Information
  - A-1.3: Search & Retrieve Patient Records
  - A-1.4: Track Patient History

### 4. A-2: Process Medical Images
**File**: `04-a2-process-medical-images.png`
- **Purpose**: Medical image processing workflow
- **Level**: A-2 decomposition
- **Sub-functions**:
  - A-2.1: Upload & Validate X-ray Images
  - A-2.2: Preprocess Images
  - A-2.3: Store & Manage Medical Files
  - A-2.4: Extract Image Metadata

### 5. A-3: Perform AI Diagnosis
**File**: `05-a3-perform-ai-diagnosis.png`
- **Purpose**: AI inference and diagnosis process
- **Level**: A-3 decomposition
- **Sub-functions**:
  - A-3.1: Load AI Model (ONNX Runtime)
  - A-3.2: Run Inference (EfficientNetB0)
  - A-3.3: Calculate Confidence Scores
  - A-3.4: Validate & Interpret Results

### 6. A-4: Generate Reports & Analytics
**File**: `06-a4-generate-reports-analytics.png`
- **Purpose**: Reporting and analytics generation
- **Level**: A-4 decomposition
- **Sub-functions**:
  - A-4.1: Compile Diagnostic Reports
  - A-4.2: Generate Statistics
  - A-4.3: Create Export Files
  - A-4.4: Update Dashboard

### 7. A-5: Ensure Security & Compliance
**File**: `07-a5-security-compliance.png`
- **Purpose**: Security and HIPAA compliance management
- **Level**: A-5 decomposition
- **Sub-functions**:
  - A-5.1: Manage Authentication
  - A-5.2: Enforce Access Control
  - A-5.3: Maintain Audit Logs
  - A-5.4: Ensure HIPAA Compliance

## 🔄 IDEF0 Methodology

IDEF0 diagrams follow the ICOM (Input, Control, Output, Mechanism) model:
- **Inputs (I)**: Data or objects consumed by the function
- **Controls (C)**: Rules, regulations, or conditions that govern the function
- **Outputs (O)**: Data or objects produced by the function
- **Mechanisms (M)**: Resources that perform the function

## 🛠️ Generation Details

These diagrams were generated from Mermaid source files using high-quality settings:

```bash
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

## 🔄 Updating Diagrams

To update any diagram:

1. Edit the corresponding `.mmd` file in this directory
2. Run `./regenerate-idef0-diagrams.sh` to regenerate all diagrams
3. The PNG files will automatically be updated

## 📝 Source Files

Each PNG has a corresponding `.mmd` source file:
- `01-context-diagram-a0.mmd` → `01-context-diagram-a0.png`
- `02-a0-decomposition.mmd` → `02-a0-decomposition.png`
- `03-a1-manage-patient-data.mmd` → `03-a1-manage-patient-data.png`
- `04-a2-process-medical-images.mmd` → `04-a2-process-medical-images.png`
- `05-a3-perform-ai-diagnosis.mmd` → `05-a3-perform-ai-diagnosis.png`
- `06-a4-generate-reports-analytics.mmd` → `06-a4-generate-reports-analytics.png`
- `07-a5-security-compliance.mmd` → `07-a5-security-compliance.png`

## ⚙️ Configuration Files

Quality optimization is achieved through:
- **`mermaid-config.json`**: Mermaid rendering settings
- **`puppeteer-config.json`**: Browser engine optimization
- **`regenerate-idef0-diagrams.sh`**: Generation script
