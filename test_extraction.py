#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Chinese journal extraction"""

import sys
sys.path.insert(0, '.')

from pdf_extractor import PDFExtractor
import os

# Test with a sample PDF
pdf_path = 'pdfs/0812018.pdf'

if os.path.exists(pdf_path):
    print(f"Testing extraction on: {pdf_path}")
    print("=" * 60)
    
    # Create extractor (no vision for quick test)
    extractor = PDFExtractor(use_vision=False, use_cache=False)
    
    # Extract metadata
    result = extractor.extract_from_pdf(pdf_path)
    
    print(f"\n📄 Title: {result['title']}")
    print(f"👤 Authors: {result['authors']}")
    print(f"📅 Year: {result['year']}")
    print(f"📰 Journal: {result['journal']}")
    print(f"📖 Volume: {result['volume']}")
    print(f"🔢 Issue: {result['issue']}")
    print(f"📄 Pages: {result['pages']}")
    
    print("\n" + "=" * 60)
    print("✅ Text-based extraction complete!")
    
else:
    print(f"❌ PDF not found: {pdf_path}")
