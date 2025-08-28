# 🗄️ IDEF1X Data Model Diagrams

This directory contains PNG versions of all IDEF1X data model diagrams for the Pneumonia AI Detection System. IDEF1X is a data modeling technique used to create a structured representation of data requirements and relationships within the system.

## 📊 Available IDEF1X Diagrams

### 1. Entity-Relationship Diagram (ERD)
**File**: `01-entity-relationship-diagram.png`
- **Purpose**: Complete database schema with all entities and relationships
- **Entities**: 
  - `PATIENT`: Patient demographic and medical information
  - `PREDICTION`: AI diagnosis results and metadata
  - `AUDIT_LOG`: System audit trail for HIPAA compliance
  - `SYSTEM_STATS`: Daily system performance statistics
  - `WEEKLY_STATS`: Aggregated weekly performance metrics
- **Relationships**: One-to-many relationships between patients and predictions, audit logging, and statistical aggregation

### 2. Prediction Workflow Sequence
**File**: `02-prediction-workflow-sequence.png`
- **Purpose**: Shows the data flow sequence for the AI prediction process
- **Process Flow**:
  1. User lookup/create patient
  2. Insert prediction record
  3. Log prediction action
  4. Update daily statistics
  5. Log statistics update
  6. Return prediction results
- **Participants**: User, Patient Table, Prediction Table, Audit Log, System Stats

### 3. Analytics Data Aggregation
**File**: `03-analytics-data-aggregation.png`
- **Purpose**: Illustrates how data flows from daily operations to reporting
- **Data Flow**:
  - Daily Operations → Daily System Stats
  - Daily Stats → Weekly Stats
  - Both feed into Dashboard Reports
  - Reports generate Export Files
- **Components**: Patient Operations, Prediction Results, Audit Activities, Statistics, Reports, Exports

## 🏗️ IDEF1X Methodology

IDEF1X diagrams represent:
- **Entities**: Things about which data is stored
- **Attributes**: Properties or characteristics of entities
- **Relationships**: Associations between entities
- **Keys**: Primary and foreign key constraints
- **Cardinality**: One-to-one, one-to-many, many-to-many relationships

## 📋 Data Model Features

### 🔒 HIPAA Compliance
- Comprehensive audit logging for all data access
- Protected Health Information (PHI) identification
- Secure data classification and handling

### 🔗 Referential Integrity
- Primary key constraints on all entities
- Foreign key relationships with cascade rules
- Check constraints for data validation

### 📊 Analytics Support
- Built-in aggregation tables for performance
- Time-based statistics tracking
- Efficient reporting data structures

### 🛡️ Security Design
- Audit trail for all database operations
- User activity tracking
- IP address and browser logging

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
2. Run `./regenerate-idef1x-diagrams.sh` to regenerate all diagrams
3. The PNG files will automatically be updated

## 📝 Source Files

Each PNG has a corresponding `.mmd` source file:
- `01-entity-relationship-diagram.mmd` → `01-entity-relationship-diagram.png`
- `02-prediction-workflow-sequence.mmd` → `02-prediction-workflow-sequence.png`
- `03-analytics-data-aggregation.mmd` → `03-analytics-data-aggregation.png`

## ⚙️ Configuration Files

Quality optimization is achieved through:
- **`mermaid-config.json`**: Mermaid rendering settings
- **`puppeteer-config.json`**: Browser engine optimization
- **`regenerate-idef1x-diagrams.sh`**: Generation script

## 💾 Database Implementation

These diagrams serve as the blueprint for:
- PostgreSQL database schema creation
- SQLAlchemy ORM model definitions
- Database migration scripts
- API endpoint data validation
- Frontend data model interfaces
