# CondGes Tools Directory

This directory contains utilities and tools for the CondGes financial management system.

## Directory Structure

### 📊 excel_processing/
Excel reading and processing utilities:
- `node_modules/` - Excel processing libraries (xlsx, cfb, codepage, etc.)
- `read_excel.py` - Python script for reading Excel files

### 📥 data_import/
Database import and data processing scripts:
- `insert_*.py` - Python scripts for database insertions
- `insert_*.sql` - SQL statements for data import
- `update_august_data.py` - August data update utilities

### 🏢 orti_tools/
ORTI-specific financial tools and utilities:
- `orti-finance-compass/` - ORTI financial compass application
- `orti-start.sh` - ORTI startup script
- `orti` - ORTI-specific utilities

### 📁 raw_data/
Raw data files and temporary storage:
- `excel_data.json` - Raw Excel data exports
- Other temporary data files

## Usage

These tools support the main CondGes system located in the parent directories:
- `../condges_app/` - Main web applications
- `../data/` - Structured financial data
- `../output/` - Analysis and reports

## Note

This tools directory was created by merging the separate 'finanza' utilities into the main CondGes system for better organization and maintenance.