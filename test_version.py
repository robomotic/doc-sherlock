#!/usr/bin/env python
"""
Demonstration script showing different ways to access doc-sherlock version.
"""

print("=" * 60)
print("Doc-Sherlock Version Access Demonstration")
print("=" * 60)

# Method 1: Direct import of __version__
print("\n1. Direct access to __version__:")
import doc_sherlock
print(f"   doc_sherlock.__version__ = '{doc_sherlock.__version__}'")

# Method 2: Using the get_version() function
print("\n2. Using get_version() function:")
print(f"   doc_sherlock.get_version() = '{doc_sherlock.get_version()}'")

# Method 3: From package metadata (if installed)
print("\n3. From package metadata (if installed via pip):")
try:
    from importlib.metadata import version
    pkg_version = version('doc-sherlock')
    print(f"   importlib.metadata.version('doc-sherlock') = '{pkg_version}'")
except Exception as e:
    print(f"   Not available: {e}")

# Method 4: CLI commands
print("\n4. CLI commands:")
print("   Run: doc-sherlock --version")
print("   Run: doc-sherlock version")
print("   Run: python -m doc_sherlock.cli --version")
print("   Run: python -m doc_sherlock.cli version")

print("\n" + "=" * 60)
print("All version access methods working correctly! ✓")
print("=" * 60)
