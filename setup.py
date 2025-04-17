from setuptools import setup, find_packages

setup(
    name="doc-sherlock",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pypdf>=3.15.0",
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
