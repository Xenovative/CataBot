# HTML Metadata Extraction Feature

## Overview
Enhanced the crawler to extract paper metadata directly from HTML content pages, improving accuracy and reducing dependency on PDF extraction alone.

## Problem Solved
**Before:** Only extracted metadata from PDFs, which could be:
- Incomplete or missing
- Difficult to parse (scanned PDFs, non-standard formats)
- Slow (requires vision extraction for better accuracy)

**After:** Extracts metadata from HTML pages first, then uses it to enhance PDF extraction results.

## How It Works

### 1. HTML Metadata Extraction
When crawling a website, the system now:
1. Parses each HTML page for academic metadata
2. Looks for standard meta tags (Dublin Core, OpenGraph, Citation tags)
3. Stores metadata associated with PDF URLs
4. Merges HTML metadata with PDF extraction

### 2. Supported Meta Tags

**Title:**
- `citation_title`
- `DC.title`
- `og:title`
- `twitter:title`
- `<h1>` or `<title>` tags

**Authors:**
- `citation_author` (multiple)
- `DC.creator`
- `author`

**Journal/Conference:**
- `citation_journal_title`
- `DC.source`
- `citation_conference_title`

**Publication Date:**
- `citation_publication_date`
- `citation_date`
- `DC.date`

**Volume/Issue:**
- `citation_volume`
- `citation_issue`

**Pages:**
- `citation_firstpage`
- `citation_lastpage`

**DOI:**
- `citation_doi`
- `DC.identifier`

**Abstract:**
- `citation_abstract`
- `DC.description`
- `description`

### 3. Metadata Merging Strategy

```python
# Priority order:
1. PDF extraction (if available and valid)
2. HTML metadata (as fallback)
3. Default values (N/A, Unknown)

# Example:
PDF: title="", authors="John Doe", year="2024"
HTML: title="Paper Title", authors="", year="2024"
Result: title="Paper Title", authors="John Doe", year="2024"
```

## Implementation Details

### web_crawler.py Changes

**New Method:**
```python
def extract_metadata_from_html(self, soup: BeautifulSoup, page_url: str) -> Dict:
    """Extract paper metadata from HTML meta tags"""
    # Searches for common academic meta tag patterns
    # Returns dictionary with extracted fields
```

**Enhanced Crawling:**
```python
async def _find_pdf_links(...):
    # Parse HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract metadata from this page
    page_metadata = self.extract_metadata_from_html(soup, url)
    
    # Find PDF links
    for pdf_url in pdf_links:
        # Associate metadata with PDF
        self.html_metadata[pdf_url] = page_metadata
```

### app.py Changes

**Enhanced Crawl Background:**
```python
async def crawl_website_background(...):
    # After downloading PDFs
    for file_info in downloaded_files:
        pdf_url = file_info.get('url')
        if pdf_url in crawler.html_metadata:
            file_info['html_metadata'] = crawler.html_metadata[pdf_url]
    
    # Pass metadata to processing
    html_metadata_map = {f['filepath']: f.get('html_metadata', {}) for f in downloaded_files}
    process_pdfs_background(..., html_metadata=html_metadata_map)
```

**Enhanced PDF Processing:**
```python
def process_pdfs_background(..., html_metadata=None):
    # After PDF extraction
    if pdf_path in html_metadata:
        html_meta = html_metadata[pdf_path]
        for paper in detected_papers:
            # Use HTML metadata as fallback
            for field in ['title', 'authors', 'journal', ...]:
                if not paper.get(field) and html_meta.get(field):
                    paper[field] = html_meta[field]
```

## Benefits

### 1. **Improved Accuracy**
- HTML metadata is often more reliable than PDF extraction
- Especially helpful for scanned PDFs or non-standard formats
- Reduces "N/A" or "Unknown" values

### 2. **Better Performance**
- HTML parsing is faster than PDF vision extraction
- Can get metadata even if PDF extraction fails
- Reduces API calls to vision models

### 3. **Richer Data**
- Can extract abstracts from HTML
- DOI and other identifiers more reliably available
- Multiple author names properly formatted

### 4. **Fallback Mechanism**
- If PDF extraction works, use it
- If PDF extraction fails/incomplete, use HTML
- Best of both worlds

## Example Scenarios

### Scenario 1: Academic Journal Website
```
HTML Page: https://journal.com/article/123
├─ Meta tags: title, authors, journal, year, doi
└─ PDF link: https://journal.com/article/123.pdf

Process:
1. Extract metadata from HTML page
2. Download PDF
3. Extract from PDF (may be incomplete)
4. Merge: HTML fills in missing fields
Result: Complete metadata ✓
```

### Scenario 2: Conference Proceedings
```
HTML Page: https://conference.org/paper/456
├─ Meta tags: title, authors, conference, year
└─ PDF link: https://conference.org/paper/456.pdf

Process:
1. Extract conference name from HTML
2. PDF extraction gets title and authors
3. Merge: HTML adds conference name
Result: Complete with conference info ✓
```

### Scenario 3: Scanned PDF
```
HTML Page: https://archive.org/details/old-paper
├─ Meta tags: Complete metadata
└─ PDF link: Scanned PDF (no text)

Process:
1. Extract all metadata from HTML
2. PDF extraction fails (scanned image)
3. Use HTML metadata entirely
Result: Complete metadata without vision extraction ✓
```

## Logging

The system logs metadata extraction:
```
INFO:web_crawler:Extracted metadata from https://example.com: ['title', 'authors', 'journal', 'year']
INFO:app:Associated HTML metadata with pdfs/paper.pdf
INFO:app:Enhanced title from HTML metadata for pdfs/paper.pdf
INFO:app:Enhanced authors from HTML metadata for pdfs/paper.pdf
```

## Compatibility

### Works With:
- Standard academic publishers (Springer, Elsevier, IEEE, etc.)
- Open access repositories (arXiv, PubMed Central)
- Conference websites
- University repositories
- Any site using Dublin Core or Citation meta tags

### Fallback For:
- Sites without meta tags (uses PDF extraction only)
- Direct PDF links (no HTML page to parse)
- Non-academic websites

## Future Enhancements

Possible improvements:
- Extract keywords from HTML
- Parse structured data (JSON-LD, Microdata)
- Extract references/citations
- Get full-text from HTML (not just PDF)
- Support more meta tag standards
- Machine learning for HTML structure parsing
