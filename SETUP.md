# Table-Aware RAG Pipeline - Setup Guide

## Python Version Requirement ⚠️

**This project requires Python 3.9, 3.10, or 3.11**

Python 3.12+ is **NOT currently supported** because the `unstructured` library (our core document parsing engine) does not yet support Python 3.12.

### Check Your Python Version

```bash
python --version
# or
python3 --version
```

If you see `Python 3.12.x`, you'll need to install Python 3.11.

---

## Installation Options

Choose one of the following methods to set up Python 3.11:

### Option 1: Using `pyenv` (Recommended for macOS/Linux)

`pyenv` allows you to manage multiple Python versions easily.

```bash
# Install pyenv (if not already installed)
# macOS
brew install pyenv

# Linux
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.9

# Set Python 3.11 for this project only
cd /path/to/hybrid-rag-parser
pyenv local 3.11.9

# Verify
python --version  # Should show Python 3.11.9
```

### Option 2: Using Anaconda/Miniconda (Cross-platform)

```bash
# Create a new conda environment with Python 3.11
conda create -n rag-pipeline python=3.11 -y

# Activate the environment
conda activate rag-pipeline

# Verify
python --version  # Should show Python 3.11.x
```

### Option 3: Using `venv` with System Python 3.11 (Windows/Linux)

If you have Python 3.11 installed on your system:

```bash
# Navigate to project directory
cd /path/to/hybrid-rag-parser

# Create virtual environment
python3.11 -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify
python --version  # Should show Python 3.11.x
```

### Option 4: Download Python 3.11 Directly

Download the latest Python 3.11.x from the official website:
- **Official Downloads**: https://www.python.org/downloads/
- Choose the installer for your operating system
- During installation, make sure to check "Add Python to PATH"

---

## Installing Dependencies

**IMPORTANT UPDATE**: The advanced `hi_res` strategy with layoutparser is currently **not available** due to dependency conflicts (layoutparser requires an obsolete version of paddlepaddle that's not available for Python 3.10+).

**GOOD NEWS**: The `unstructured` library has excellent built-in table extraction that works without layoutparser! The `auto` and `fast` strategies provide great results for most documents.

Once you have Python 3.9, 3.10, or 3.11 active:

### Recommended Installation (Works for Everyone)

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install dependencies (no layoutparser/pytorch needed!)
pip install -r requirements.txt
```

**This installs:**
- ✅ unstructured with PDF support (handles table extraction)
- ✅ PDF processing tools (pdf2image, pdfminer, etc.)
- ✅ Data processing (pandas, numpy)
- ✅ Works with 'auto' and 'fast' strategies
- ✅ No heavy ML dependencies (~200MB total)
- ✅ Installation takes 2-3 minutes

### Alternative: Minimal Installation (Troubleshooting)

If you encounter any issues with the main requirements:

```bash
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

### Common Installation Issues

#### Issue: Dependency conflict with `unstructured-inference`

**Error message**:
```
ERROR: Cannot install unstructured-inference and unstructured[pdf] because these package versions have conflicting dependencies.
The conflict is caused by:
    unstructured[pdf] 0.11.8 depends on unstructured-inference==0.7.18
```

**Solution 1**: Use the minimal requirements file:
```bash
pip install -r requirements-minimal.txt
```

**Solution 2**: Install packages step-by-step in the correct order:
```bash
# Clear any partial installation
pip uninstall unstructured unstructured-inference -y

# Install in order - unstructured FIRST
pip install "unstructured[pdf]>=0.11.0,<0.12.0"
pip install torch torchvision
pip install layoutparser
pip install pandas numpy python-dotenv
```

**Solution 3**: Let pip figure it out with no version constraints:
```bash
pip install unstructured[pdf] torch torchvision layoutparser pandas numpy python-dotenv
```

#### Issue: `paddlepaddle` dependency conflict with `layoutparser`

**Error message**:
```
ERROR: Cannot install layoutparser[paddledetection]==0.3.4 and paddlepaddle==3.2.1
because these package versions have conflicting dependencies.
The conflict is caused by:
    layoutparser[paddledetection] 0.3.4 depends on paddlepaddle==2.1.0
```

**Problem**:
- `layoutparser[paddledetection]` requires the ancient `paddlepaddle==2.1.0`
- `paddlepaddle==2.1.0` is **not available** for Python 3.10+ on most platforms
- This is a known issue with layoutparser - the project hasn't updated dependencies

**Solution**: **Don't use layoutparser** - it's not needed!

The `unstructured` library extracts tables excellently on its own using the `auto` or `fast` strategies. Simply install with:

```bash
pip install -r requirements.txt
```

This installs everything you need WITHOUT layoutparser or paddlepaddle.

**The pipeline will:**
- ✅ Extract tables from PDFs
- ✅ Separate tables from narrative text
- ✅ Work with all your sample PDFs
- ✅ Support the 'auto' and 'fast' strategies
- ✅ No heavy ML dependencies or conflicts

**Note**: The `hi_res` strategy with layoutparser is currently unavailable due to this dependency conflict. The `auto` strategy provides excellent results for most use cases.


#### Issue: `python-magic` fails on Windows

**Solution**: Install `python-magic-bin` instead:
```bash
pip install python-magic-bin
```

#### Issue: `layoutparser[paddledetection]` fails

**Solution**: Install base layoutparser first, then paddledetection separately:
```bash
pip install layoutparser
pip install "paddlepaddle>=2.0.0"
pip install "paddledetection>=2.0.0"
```

#### Issue: Out of memory during installation

**Solution**: Install packages individually:
```bash
pip install unstructured[pdf]
pip install torch torchvision
pip install layoutparser[paddledetection]
pip install -r requirements.txt  # Install remaining packages
```

---

## System Dependencies

Some packages require system-level dependencies:

### macOS

```bash
# Install Poppler (for pdf2image)
brew install poppler

# Install Tesseract OCR (for pytesseract)
brew install tesseract

# Install libmagic (for python-magic)
brew install libmagic
```

### Ubuntu/Debian Linux

```bash
# Install Poppler
sudo apt-get update
sudo apt-get install -y poppler-utils

# Install Tesseract OCR
sudo apt-get install -y tesseract-ocr

# Install libmagic
sudo apt-get install -y libmagic1
```

### Windows

1. **Poppler**: Download from https://github.com/oschwartz10612/poppler-windows/releases/
   - Extract and add the `bin/` folder to your PATH

2. **Tesseract**: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
   - Install and add to PATH

3. **python-magic**: Use `python-magic-bin` package instead (no system dependency needed)
   ```bash
   pip install python-magic-bin
   ```

---

## Verifying Installation

After installation, verify everything works:

```bash
# Test Python version
python --version
# Should output: Python 3.11.x

# Test imports
python -c "import unstructured; print('✓ unstructured')"
python -c "import torch; print('✓ torch')"
python -c "import layoutparser; print('✓ layoutparser')"
python -c "import PIL; print('✓ Pillow')"

# Run syntax check on main script
python -m py_compile ingest.py
echo "✓ ingest.py syntax is valid"
```

---

## Quick Start

Once everything is installed:

```bash
# Process all PDFs in the data/ directory
python ingest.py

# Process a specific PDF
python ingest.py data/sample1.pdf

# Run examples
python example_usage.py
```

---

## Project Structure

```
hybrid-rag-parser/
├── data/                    # PDF files to process
│   ├── sample1.pdf
│   ├── sample2.pdf
│   └── sample3.pdf
├── ingest.py               # Main ingestion script
├── example_usage.py        # Usage examples
├── requirements.txt        # Python dependencies
├── SETUP.md               # This file
└── .gitignore             # Git ignore patterns
```

---

## Next Steps After Setup

1. **Test with sample PDFs**: Run `python ingest.py` to process the sample PDFs
2. **Review the output**: Check the extracted tables and text chunks
3. **Phase 2 - Database Integration**: Implement MongoDB and Qdrant connectors
4. **Phase 3 - Query Interface**: Build hybrid search capabilities
5. **Phase 4 - Fabric Migration**: Migrate to Microsoft Fabric architecture

---

## Troubleshooting

### "Command not found: python"

Try using `python3` instead:
```bash
python3 --version
python3 ingest.py
```

### Virtual environment not activating

Make sure you're in the project directory and using the correct activation command for your OS.

### Import errors after installation

Ensure your virtual environment is activated and you've installed all dependencies:
```bash
# Check which python you're using
which python
# Should point to your virtual environment

# Reinstall dependencies
pip install -r requirements.txt
```

### Out of disk space during installation

PyTorch and related libraries are large (~2GB total). Free up at least 5GB of disk space.

---

## Support

For issues specific to:
- **unstructured.io**: https://github.com/Unstructured-IO/unstructured/issues
- **PyTorch**: https://pytorch.org/get-started/locally/
- **This project**: Create an issue in your project repository

---

## Alternative: Docker (Future Enhancement)

If you encounter persistent installation issues, we can create a Docker container with Python 3.11 and all dependencies pre-installed. Let me know if you'd like me to add this!
