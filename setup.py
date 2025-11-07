from setuptools import setup, find_packages
import os
import re


def get_version():
    """Read version from doc_sherlock/__init__.py"""
    init_path = os.path.join(os.path.dirname(__file__), "doc_sherlock", "__init__.py")
    with open(init_path, "r") as f:
        content = f.read()
        match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE)
        if match:
            return match.group(1)
        raise RuntimeError("Unable to find version string in doc_sherlock/__init__.py")


setup(
    name="doc-sherlock",
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        "pypdf>=3.15.0",
        "PyPDF2>=3.0.0",
        "pdfminer.six==20221105",  # Using version compatible with pdfplumber
        "pikepdf>=8.0.0",
        "pdfplumber==0.10.4",  # Specific version compatible with pdfminer.six==20221105
        "pillow>=10.0.0",
        "pytesseract>=0.3.10",
        "colorama>=0.4.6",
        "click>=8.1.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "pylint>=3.0.0",
            "fastapi>=0.110.0",
            "uvicorn[standard]>=0.29.0",
            "python-multipart>=0.0.7",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "fpdf>=1.7.2",
            "reportlab>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "doc-sherlock=doc_sherlock.cli:main",
        ],
    },
    author="DocSherlock Team",
    author_email="example@example.com",
    description="A tool to detect hidden text in PDF documents that could be used for prompt injection attacks",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/doc-sherlock",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
