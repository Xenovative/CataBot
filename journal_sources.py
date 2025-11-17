#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Journal source mapping for automatic journal detection based on crawl source
"""

import re
from urllib.parse import urlparse

# Known journal sources mapping
JOURNAL_SOURCES = {
    # Chinese journals
    'cuhk.edu.hk/ics/21c': {
        'journal': '二十一世紀',
        'journal_en': 'Twenty-First Century',
        'publisher': '香港中文大學中國文化研究所',
        'url_pattern': r'cuhk\.edu\.hk/ics/21c'
    },
    'cuhk.edu.hk/theology': {
        'journal': '中國神學研究院期刊',
        'journal_en': 'China Graduate School of Theology Journal',
        'url_pattern': r'cuhk\.edu\.hk/theology'
    },
    
    # Add more journal sources here
    # Format:
    # 'domain/path': {
    #     'journal': 'Journal Name',
    #     'journal_en': 'English Name',
    #     'publisher': 'Publisher Name',
    #     'url_pattern': r'regex pattern'
    # }
}


def detect_journal_from_url(url: str) -> dict:
    """
    Detect journal information from crawl source URL
    
    Args:
        url: Source URL where PDFs were crawled from
        
    Returns:
        dict with journal info, or empty dict if not found
    """
    if not url:
        return {}
    
    # Parse URL
    try:
        parsed = urlparse(url)
        domain_path = f"{parsed.netloc}{parsed.path}"
    except:
        return {}
    
    # Check against known sources
    for source_key, journal_info in JOURNAL_SOURCES.items():
        pattern = journal_info.get('url_pattern', source_key)
        if re.search(pattern, domain_path, re.IGNORECASE):
            return {
                'journal': journal_info.get('journal'),
                'journal_en': journal_info.get('journal_en'),
                'publisher': journal_info.get('publisher'),
                'source_url': url,
                'confidence': 'high'  # High confidence from known source
            }
    
    # Try to extract journal name from URL path
    # Common patterns: /journal-name/, /publications/journal-name/
    path_parts = parsed.path.strip('/').split('/')
    if len(path_parts) >= 2:
        # Look for journal-like path segments
        for part in path_parts:
            if len(part) > 3 and not part.isdigit():
                # Potential journal identifier
                return {
                    'journal': part.replace('-', ' ').replace('_', ' ').title(),
                    'source_url': url,
                    'confidence': 'low'  # Low confidence from URL parsing
                }
    
    return {}


def add_journal_source(domain_path: str, journal_name: str, journal_en: str = None, 
                       publisher: str = None, url_pattern: str = None):
    """
    Add a new journal source to the database
    
    Args:
        domain_path: Domain and path identifier (e.g., 'example.com/journal')
        journal_name: Journal name (Chinese or English)
        journal_en: English journal name (optional)
        publisher: Publisher name (optional)
        url_pattern: Regex pattern for matching (optional, uses domain_path if not provided)
    """
    JOURNAL_SOURCES[domain_path] = {
        'journal': journal_name,
        'journal_en': journal_en,
        'publisher': publisher,
        'url_pattern': url_pattern or domain_path
    }


def get_all_sources():
    """Get all known journal sources"""
    return JOURNAL_SOURCES.copy()
