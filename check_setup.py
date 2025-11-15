#!/usr/bin/env python3
"""
Setup Verification Script for Table-Aware RAG Pipeline
=======================================================
Run this script to verify your Python environment and dependencies.

Usage:
    python check_setup.py
"""

import sys
import platform


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"🐍 Python Version: {platform.python_version()}")

    if version.major != 3:
        print("   ❌ ERROR: Python 3 is required")
        return False

    if version.minor < 9:
        print("   ❌ ERROR: Python 3.9 or higher is required")
        print(f"   Your version: {version.major}.{version.minor}.{version.micro}")
        return False

    if version.minor >= 12:
        print("   ❌ ERROR: Python 3.12+ is not supported")
        print("   Supported versions: 3.9, 3.10, 3.11")
        print("\n   📖 Please see SETUP.md for installation instructions")
        return False

    print(f"   ✅ Version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking Dependencies:")

    # Core dependencies (required)
    core_dependencies = {
        'unstructured': 'unstructured',
        'PIL': 'Pillow',
        'pandas': 'pandas',
        'numpy': 'NumPy',
        'dotenv': 'python-dotenv',
    }

    # Optional dependencies for hi_res strategy
    optional_dependencies = {
        'torch': 'PyTorch (optional - for hi_res strategy)',
        'layoutparser': 'LayoutParser (optional - for hi_res strategy)',
    }

    all_core_installed = True
    any_optional_installed = False

    print("\n   Core Dependencies:")
    for module, display_name in core_dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {display_name}")
        except ImportError:
            print(f"   ❌ {display_name} - Not installed")
            all_core_installed = False

    print("\n   Optional Dependencies (for advanced table detection):")
    for module, display_name in optional_dependencies.items():
        try:
            imported = __import__(module)
            # For layoutparser, check version
            if module == 'layoutparser':
                version = getattr(imported, '__version__', 'unknown')
                if version != 'unknown':
                    major, minor = version.split('.')[:2]
                    if int(major) == 0 and int(minor) < 3:
                        print(f"   ⚠️  {display_name} - Version {version} (need >=0.3.4)")
                        print(f"       Install with: pip install 'layoutparser[paddledetection]>=0.3.4'")
                    else:
                        print(f"   ✅ {display_name} - v{version}")
                        any_optional_installed = True
                else:
                    print(f"   ✅ {display_name}")
                    any_optional_installed = True
            else:
                print(f"   ✅ {display_name}")
                any_optional_installed = True
        except ImportError:
            print(f"   ⚠️  {display_name} - Not installed")
            print(f"       (Pipeline will use 'fast' strategy instead of 'hi_res')")

    if not any_optional_installed:
        print("\n   ℹ️  Note: Without optional dependencies, the pipeline uses 'fast' strategy")
        print("   ℹ️  For best table detection, install: pip install -r requirements.txt")
        print("   ℹ️  For quick start, you can use: pip install -r requirements-lite.txt")

    return all_core_installed


def check_system_dependencies():
    """Check system-level dependencies."""
    print("\n🔧 Checking System Dependencies:")

    # Check for poppler (pdf2image)
    try:
        import pdf2image
        pdf2image.pdfinfo_from_path  # This will fail if poppler is not installed
        print("   ✅ Poppler (pdf2image)")
    except Exception:
        print("   ⚠️  Poppler - May not be properly configured")
        print("      See SETUP.md for installation instructions")

    # Check for tesseract (pytesseract)
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("   ✅ Tesseract OCR")
    except Exception:
        print("   ⚠️  Tesseract OCR - May not be properly configured")
        print("      (Optional for basic table extraction)")

    return True


def check_data_directory():
    """Check if data directory exists with PDF files."""
    print("\n📁 Checking Data Directory:")

    import os
    from pathlib import Path

    data_dir = Path("data")

    if not data_dir.exists():
        print("   ❌ 'data' directory not found")
        return False

    pdf_files = list(data_dir.glob("*.pdf"))

    if not pdf_files:
        print("   ⚠️  No PDF files found in 'data' directory")
        return False

    print(f"   ✅ Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"      • {pdf.name}")

    return True


def test_import_ingest():
    """Test importing the main ingest module."""
    print("\n📝 Testing ingest.py:")

    try:
        import ingest
        print("   ✅ Successfully imported ingest module")

        # Check if main classes/functions exist
        if hasattr(ingest, 'DocumentProcessor'):
            print("   ✅ DocumentProcessor class found")
        if hasattr(ingest, 'process_single_pdf'):
            print("   ✅ process_single_pdf function found")
        if hasattr(ingest, 'process_directory'):
            print("   ✅ process_directory function found")

        return True
    except ImportError as e:
        print(f"   ❌ Failed to import ingest module: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def print_recommendations(results):
    """Print recommendations based on check results."""
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 All checks passed! Your environment is ready.")
        print("\nNext steps:")
        print("  1. Run: python ingest.py")
        print("  2. Or run examples: python example_usage.py")
        print("  3. See SETUP.md for more information")
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
        print("\nRecommendations:")

        if not results['python_version']:
            print("  1. Install Python 3.11 (see SETUP.md)")
            print("     - Using pyenv: pyenv install 3.11.9 && pyenv local 3.11.9")
            print("     - Using conda: conda create -n rag-pipeline python=3.11")

        if not results['dependencies']:
            print("  2. Install Python dependencies:")
            print("     Option A (Full - best accuracy): pip install -r requirements.txt")
            print("     Option B (Lite - faster install): pip install -r requirements-lite.txt")
            print("     Option C (Minimal - troubleshooting): pip install -r requirements-minimal.txt")

        if not results['data_directory']:
            print("  3. Add PDF files to the 'data' directory")

        print("\n📖 See SETUP.md for detailed installation instructions")

    print("="*70 + "\n")


def main():
    """Run all setup checks."""
    print("="*70)
    print("TABLE-AWARE RAG PIPELINE - SETUP VERIFICATION")
    print("="*70)

    results = {
        'python_version': check_python_version(),
        'dependencies': True,  # Will be updated
        'system_deps': True,   # Will be updated
        'data_directory': True,  # Will be updated
        'ingest_module': True,   # Will be updated
    }

    # Only check dependencies if Python version is correct
    if results['python_version']:
        results['dependencies'] = check_dependencies()

        # Only check system deps if Python packages are installed
        if results['dependencies']:
            results['system_deps'] = check_system_dependencies()
            results['data_directory'] = check_data_directory()
            results['ingest_module'] = test_import_ingest()

    print_recommendations(results)

    # Exit with appropriate code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
