#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug year extraction"""

import pdfplumber
import re

pdf = pdfplumber.open('pdfs/0812018.pdf')
content = pdf.pages[0].extract_text()

print("First 500 characters:")
print("=" * 60)
print(content[:500])
print("=" * 60)

# Test pattern
pattern = r'(\d{4})年'
matches = re.findall(pattern, content[:500])
print(f"\nYears found in first 500 chars: {matches}")

# Check what the extractor is doing
from pdf_extractor import PDFExtractor
extractor = PDFExtractor(use_vision=False, use_cache=False)

# Get metadata
metadata = extractor._extract_metadata('pdfs/0812018.pdf')
print(f"\nMetadata year: {metadata.get('year')}")

# Get enhanced metadata
enhanced = extractor._enhance_metadata(metadata, content, 'pdfs/0812018.pdf')
print(f"Enhanced year: {enhanced.get('year')}")

# Test _extract_year directly
year = extractor._extract_year(content)
print(f"Direct _extract_year: {year}")
