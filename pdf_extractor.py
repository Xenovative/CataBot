import re
import PyPDF2
import pdfplumber
from typing import Dict, Optional, List
import logging
import base64
import io
from PIL import Image
import os
import hashlib
import json
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import OpenAI for vision capabilities
try:
    import openai
    from openai import OpenAI
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    logger.info("OpenAI not available. Vision-based extraction disabled. Install with: pip install openai")

# Try to import pdf2image for PDF to image conversion
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    logger.info("pdf2image not available. Vision extraction will be limited. Install with: pip install pdf2image")


class PDFExtractor:
    """Extract metadata and content from PDF files"""
    
    def __init__(self, use_vision: bool = True, api_key: str = None, use_cache: bool = True):
        self.use_vision = use_vision and VISION_AVAILABLE
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.use_cache = use_cache
        self.cache_dir = '.cache/pdf_metadata'
        
        if self.use_cache:
            os.makedirs(self.cache_dir, exist_ok=True)
        
        if self.use_vision and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("Vision-based extraction enabled")
        else:
            self.client = None
            if use_vision:
                logger.warning("Vision extraction requested but OpenAI API key not found")
        
        self.metadata_patterns = {
            'journal': [
                # Chinese journals with 《》 brackets (most common format)
                r'《([^》]{3,40})》[^\n]{0,20}(?:網絡版|網路版)?',  # 《二十一世紀》網絡版
                r'《([^》]{3,40})》',  # 《期刊名》
                # Chinese academic journals
                r'^([^\n]{3,30})[學学]報',  # XX學報
                r'^([^\n]{3,30})[學学]刊',  # XX學刊
                r'([^\n]{4,30})(?:學報|学报|學刊|学刊)',
                # English journals
                r'(?:Journal|JOURNAL)\s+(?:of|OF)\s+([A-Z][A-Za-z\s&]{5,60})',
                r'([A-Z][A-Za-z\s&]{10,60})\s*[,\n]?\s*(?:Vol|Volume)',
                # Proceedings
                r'Proceedings?\s+of\s+(?:the\s+)?([A-Z][A-Za-z\s&]{5,60})',
                # Common journal format at start of line
                r'^([A-Z][A-Za-z\s&:]{10,60}),\s*Vol',
            ],
            'title': [
                # Title with colon (common in academic papers)
                r'^([A-Z][A-Za-z0-9\s,:-]+(?::|：)[A-Za-z0-9\s,:-]+?)(?:\n|$)',
                # Explicit title label
                r'(?:Title|TITLE|標題)\s*[：:]\s*(.+?)(?:\n|$)',
                # First line that looks like a title (capitalized, 10-200 chars)
                r'^([A-Z][A-Za-z\s]{10,200})(?:\n|Abstract|ABSTRACT)',
                # All caps title
                r'^([A-Z][A-Z\s]{10,100})(?:\n)',
                # Title case with multiple words
                r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,})(?:\n)',
            ],
            'author': [
                # Explicit author labels
                r'(?:Author|AUTHORS|作者)[s]?\s*[：:]\s*(.+?)(?:\n|$)',
                r'By[：:]?\s+(.+?)(?:\n|$)',
                # Name patterns (First Last, First Last)
                r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:,\s*[A-Z][a-z]+\s+[A-Z][a-z]+)*)',
                # Names with initials (J. Smith, A. B. Johnson)
                r'([A-Z]\.\s*[A-Z]?\.?\s*[A-Z][a-z]+(?:,\s*[A-Z]\.\s*[A-Z]?\.?\s*[A-Z][a-z]+)*)',
                # Names before email or affiliation
                r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*(?:@|\n.*?@|\n.*?University|\n.*?Department)',
                # Asian names (Last First)
                r'([A-Z][a-z]+\s+[A-Z][a-z]+|[\u4e00-\u9fff]{2,4})',
            ],
            'year': [
                # Chinese year format with 年 (highest priority - most reliable)
                r'(\d{4})年',
                # Standard year patterns
                r'\b(19|20)\d{2}\b',
                r'(19|20)\d{2}',
                # Chinese traditional year format (二○○九年, 二〇〇九年)
                # Note: PDF extraction may drop ○ characters, so this is less reliable
                r'([二三四五六七八九○〇零一]{4})年',
                # Year with month
                r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[,\s]+((?:19|20)\d{2})',
                # Copyright year
                r'©\s*((?:19|20)\d{2})',
                r'Copyright\s*©?\s*((?:19|20)\d{2})',
                # Published year
                r'(?:Published|Publication)[：:]?\s*(?:in\s+)?((?:19|20)\d{2})',
            ],
            'volume': [
                # Volume patterns
                r'Vol(?:ume)?\.?\s*(\d+)',
                r'Volume\s+(\d+)',
                r'VOL\.?\s*(\d+)',
                r'V\.\s*(\d+)',
                # Volume with issue
                r'Vol\.?\s*(\d+)\s*(?:,|\()',
                # Chinese
                r'(?:卷|第.*?卷)[：:]?\s*(\d+)',
            ],
            'issue': [
                # Chinese issue patterns (more specific)
                r'第\s*(\d+)\s*期',  # 第84期
                r'總第\s*(\d+)\s*期',  # 總第84期 (total issue number)
                r'(?:期|期號)[：:]?\s*(\d+)',
                # English issue patterns
                r'(?:No|NO|Issue|ISSUE|Number)\s*\.?\s*[：:]?\s*(\d+)',
                r'Issue\s+(\d+)',
                r'No\.?\s*(\d+)',
                r'Number\s+(\d+)',
                r'#(\d+)',
                # Issue in parentheses
                r'\((\d+)\)',
                # Chinese
                r'(?:期|第.*?期)[：:]?\s*(\d+)',
            ],
            'pages': [
                # Page range patterns
                r'pp?\.?\s*(\d+)\s*[-–—]\s*(\d+)',
                r'Pages?\s*[：:]?\s*(\d+)\s*[-–—]\s*(\d+)',
                r'P\.\s*(\d+)\s*[-–—]\s*(\d+)',
                # Page range with colon
                r'(\d+)\s*[-–—]\s*(\d+)\s*(?:pp|pages)',
                # Chinese
                r'(?:頁|页)[：:]?\s*(\d+)\s*[-–—]\s*(\d+)',
            ]
        }
    
    def _get_cache_key(self, pdf_path: str) -> str:
        """Generate cache key based on file path and modification time"""
        try:
            stat = os.stat(pdf_path)
            # Use file path, size, and mtime for cache key
            key_str = f"{pdf_path}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(key_str.encode()).hexdigest()
        except:
            return None
    
    def _get_cached_metadata(self, pdf_path: str) -> Optional[Dict]:
        """Retrieve cached metadata if available"""
        if not self.use_cache:
            return None
        
        cache_key = self._get_cache_key(pdf_path)
        if not cache_key:
            return None
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    logger.info(f"Using cached metadata for {os.path.basename(pdf_path)}")
                    return cached
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        return None
    
    def _save_to_cache(self, pdf_path: str, metadata: Dict):
        """Save metadata to cache"""
        if not self.use_cache:
            return
        
        cache_key = self._get_cache_key(pdf_path)
        if not cache_key:
            return
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _get_vision_cache(self, pdf_path: str) -> Optional[Dict]:
        """Retrieve cached vision results"""
        if not self.use_cache:
            return None
        
        cache_key = self._get_cache_key(pdf_path)
        if not cache_key:
            return None
        
        vision_cache_dir = os.path.join(self.cache_dir, 'vision')
        os.makedirs(vision_cache_dir, exist_ok=True)
        
        cache_file = os.path.join(vision_cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load vision cache: {e}")
        
        return None
    
    def _save_vision_cache(self, pdf_path: str, metadata: Dict):
        """Save vision results to cache"""
        if not self.use_cache:
            return
        
        cache_key = self._get_cache_key(pdf_path)
        if not cache_key:
            return
        
        vision_cache_dir = os.path.join(self.cache_dir, 'vision')
        os.makedirs(vision_cache_dir, exist_ok=True)
        
        cache_file = os.path.join(vision_cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save vision cache: {e}")
    
    def extract_from_pdf(self, pdf_path: str, fast_mode: bool = False) -> Dict[str, any]:
        """Extract metadata and content from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            fast_mode: If True, skip vision extraction and use faster text-only extraction
        """
        # Check cache first
        cached = self._get_cached_metadata(pdf_path)
        if cached:
            return cached
        
        try:
            # Fast mode: text-only extraction
            if fast_mode:
                metadata = self._extract_metadata(pdf_path)
                content = self._extract_text(pdf_path, max_pages=3)  # Only first 3 pages
                metadata = self._enhance_metadata(metadata, content, pdf_path)
            else:
                # Full extraction
                metadata = self._extract_metadata(pdf_path)
                content = self._extract_text(pdf_path)
                
                # Try to extract additional info from content first
                if content:
                    metadata = self._enhance_metadata(metadata, content, pdf_path)
                
                # Try vision-based extraction (vision takes priority over text)
                if self.use_vision and self.client:
                    try:
                        vision_metadata = self._extract_with_vision(pdf_path)
                        # Merge vision results with existing metadata (vision takes priority)
                        for key, value in vision_metadata.items():
                            # Accept vision results if they're not "Unknown" or "未知"
                            if value and value not in ['Unknown', 'N/A', '', '未知', 'N/A']:
                                metadata[key] = value
                            # If text extraction found something but vision didn't, keep text result
                            elif not value or value in ['Unknown', '未知']:
                                # Keep existing metadata if it's better
                                pass
                        logger.info(f"Vision extraction successful for {pdf_path}")
                    except Exception as e:
                        logger.warning(f"Vision extraction failed, falling back to text: {e}")
            
            result = {
                'title': metadata.get('title', 'Unknown'),
                'authors': metadata.get('authors', 'Unknown'),
                'year': metadata.get('year', 'Unknown'),
                'journal': metadata.get('journal', 'N/A'),
                'volume': metadata.get('volume', 'N/A'),
                'issue': metadata.get('issue', 'N/A'),
                'pages': metadata.get('pages', 'N/A'),
                'content_preview': content[:500] if content else '',
                'full_content': content,
                'file_path': pdf_path
            }
            
            # Save to cache
            self._save_to_cache(pdf_path, result)
            
            return result
        except Exception as e:
            logger.error(f"Error extracting from {pdf_path}: {e}")
            return {
                'title': 'Error',
                'authors': 'Unknown',
                'year': 'Unknown',
                'journal': 'N/A',
                'volume': 'N/A',
                'issue': 'N/A',
                'pages': 'N/A',
                'content_preview': '',
                'full_content': '',
                'file_path': pdf_path,
                'error': str(e)
            }
    
    def extract_from_pdfs_batch(self, pdf_paths: List[str], max_workers: int = 4, fast_mode: bool = False) -> List[Dict]:
        """Extract metadata from multiple PDFs in parallel
        
        Args:
            pdf_paths: List of PDF file paths
            max_workers: Number of parallel workers (default: 4)
            fast_mode: If True, use faster text-only extraction
        
        Returns:
            List of metadata dictionaries
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self.extract_from_pdf, path, fast_mode): path 
                for path in pdf_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                pdf_path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Completed: {os.path.basename(pdf_path)}")
                except Exception as e:
                    logger.error(f"Failed to process {pdf_path}: {e}")
                    results.append({
                        'title': 'Error',
                        'authors': 'Unknown',
                        'year': 'Unknown',
                        'journal': 'N/A',
                        'volume': 'N/A',
                        'issue': 'N/A',
                        'pages': 'N/A',
                        'content_preview': '',
                        'full_content': '',
                        'file_path': pdf_path,
                        'error': str(e)
                    })
        
        return results
    
    def _extract_metadata(self, pdf_path: str) -> Dict[str, str]:
        """Extract metadata from PDF properties"""
        metadata = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_info = pdf_reader.metadata
                
                if pdf_info:
                    metadata['title'] = pdf_info.get('/Title', '')
                    metadata['authors'] = pdf_info.get('/Author', '')
                    metadata['subject'] = pdf_info.get('/Subject', '')
                    
                    # Try to extract year from creation date
                    creation_date = pdf_info.get('/CreationDate', '')
                    if creation_date:
                        year_match = re.search(r'(19|20)\d{2}', creation_date)
                        if year_match:
                            metadata['year'] = year_match.group(0)
                
                # Get page count
                metadata['page_count'] = len(pdf_reader.pages)
        
        except Exception as e:
            logger.warning(f"Could not extract PDF metadata: {e}")
        
        return metadata
    
    def _extract_headers_footers(self, pdf_path: str, max_pages: int = 3) -> Dict[str, List[str]]:
        """Extract headers and footers from multiple pages to find consistent journal info
        
        Optimized: Only checks first 3 pages (reduced from 5) for speed
        """
        headers = []
        footers = []
        
        try:
            # Use PyPDF2 first (faster than pdfplumber)
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for i in range(min(max_pages, len(pdf_reader.pages))):
                    text = pdf_reader.pages[i].extract_text() or ""
                    lines = text.split('\n')
                    if len(lines) > 0:
                        # First line only (faster)
                        headers.append(lines[0])
                        # Last line only (faster)
                        if len(lines) > 1:
                            footers.append(lines[-1])
        except Exception as e:
            logger.warning(f"Header/footer extraction failed: {e}")
        
        return {'headers': headers, 'footers': footers}
    
    def _extract_text(self, pdf_path: str, max_pages: int = 10) -> str:
        """Extract text content from PDF (first few pages for metadata)"""
        text = ""
        
        try:
            # Try pdfplumber first (better text extraction)
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages[:max_pages]):
                    text += page.extract_text() or ""
                    if i < len(pdf.pages) - 1:
                        text += "\n\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for i in range(min(max_pages, len(pdf_reader.pages))):
                        text += pdf_reader.pages[i].extract_text() or ""
            except Exception as e2:
                logger.error(f"Text extraction failed: {e2}")
        
        return text.strip()
    
    def _enhance_metadata(self, metadata: Dict, content: str, pdf_path: str = None) -> Dict:
        """Extract additional metadata from content using patterns"""
        
        # Clean content for better matching
        content_lines = content.split('\n')
        
        # Extract headers/footers for journal, volume, issue detection
        header_footer_text = ""
        if pdf_path:
            try:
                hf_data = self._extract_headers_footers(pdf_path)
                header_footer_text = '\n'.join(hf_data['headers'] + hf_data['footers'])
            except Exception as e:
                logger.warning(f"Could not extract headers/footers: {e}")
        
        # Extract journal name from headers/footers (most reliable)
        if not metadata.get('journal') or metadata.get('journal') == '':
            journal = self._extract_journal(header_footer_text, content)
            if journal:
                metadata['journal'] = journal
        
        # Extract title if not present
        if not metadata.get('title') or metadata.get('title') == '':
            title = self._extract_title(content, content_lines)
            if title:
                metadata['title'] = title
        
        # Extract authors if not present
        if not metadata.get('authors') or metadata.get('authors') == '':
            authors = self._extract_authors(content, content_lines)
            if authors:
                metadata['authors'] = authors
        
        # Extract year from content (always prefer content over PDF metadata)
        year = self._extract_year(content)
        if year:
            metadata['year'] = year
        elif not metadata.get('year') or metadata.get('year') == '':
            # Only use PDF metadata year as last resort
            pass
        
        # Extract volume from headers/footers first, then content
        if not metadata.get('volume') or metadata.get('volume') == '':
            # Try headers/footers first (more reliable for periodicals)
            for pattern in self.metadata_patterns['volume']:
                match = re.search(pattern, header_footer_text, re.IGNORECASE)
                if match:
                    metadata['volume'] = match.group(1)
                    break
            # Fallback to content
            if not metadata.get('volume'):
                for pattern in self.metadata_patterns['volume']:
                    match = re.search(pattern, content[:2000], re.IGNORECASE)
                    if match:
                        metadata['volume'] = match.group(1)
                        break
        
        # Extract issue from headers/footers first, then content
        if not metadata.get('issue') or metadata.get('issue') == '':
            # Try headers/footers first (more reliable for periodicals)
            for pattern in self.metadata_patterns['issue']:
                match = re.search(pattern, header_footer_text, re.IGNORECASE)
                if match:
                    metadata['issue'] = match.group(1)
                    break
            # Fallback to content
            if not metadata.get('issue'):
                for pattern in self.metadata_patterns['issue']:
                    match = re.search(pattern, content[:2000], re.IGNORECASE)
                    if match:
                        metadata['issue'] = match.group(1)
                        break
        
        # Extract page range
        if not metadata.get('pages') or metadata.get('pages') == '':
            for pattern in self.metadata_patterns['pages']:
                match = re.search(pattern, content[:2000], re.IGNORECASE)
                if match:
                    if len(match.groups()) >= 2:
                        metadata['pages'] = f"{match.group(1)}-{match.group(2)}"
                    break
        
        return metadata
    
    def _extract_title(self, content: str, lines: List[str]) -> Optional[str]:
        """Enhanced title extraction"""
        # Try each pattern
        for pattern in self.metadata_patterns['title']:
            match = re.search(pattern, content[:1500], re.MULTILINE)
            if match:
                title = match.group(1).strip()
                # Validate title (not too short, not too long, not all caps unless reasonable)
                if 10 <= len(title) <= 300:
                    # Clean up title
                    title = re.sub(r'\s+', ' ', title)  # Normalize whitespace
                    title = title.strip('.,;:')
                    return title
        
        # Fallback: First substantial line that looks like a title
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            # Skip very short lines, page numbers, headers
            if len(line) < 10 or len(line) > 300:
                continue
            if re.match(r'^\d+$', line):  # Skip page numbers
                continue
            if line.lower() in ['abstract', 'introduction', 'keywords']:
                continue
            # Check if it looks like a title
            if re.match(r'^[A-Z]', line) and not line.endswith(':'):
                return line
        
        return None
    
    def _extract_authors(self, content: str, lines: List[str]) -> Optional[str]:
        """Enhanced author extraction"""
        # Try explicit author patterns first
        for pattern in self.metadata_patterns['author'][:3]:
            match = re.search(pattern, content[:2000], re.MULTILINE | re.IGNORECASE)
            if match:
                authors = match.group(1).strip()
                # Clean up
                authors = re.sub(r'\s+', ' ', authors)
                if len(authors) > 3 and len(authors) < 500:
                    return authors
        
        # Look for author-like patterns in first 20 lines
        potential_authors = []
        for i, line in enumerate(lines[:20]):
            line = line.strip()
            # Skip title and abstract
            if i == 0 or 'abstract' in line.lower():
                continue
            
            # Check for name patterns
            # Pattern: First Last, First Last
            if re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', line):
                # Check if line has email or affiliation indicators
                next_lines = ' '.join(lines[i:i+3]).lower()
                if any(indicator in next_lines for indicator in ['@', 'university', 'department', 'institute', 'college']):
                    potential_authors.append(line)
                    break
        
        if potential_authors:
            return potential_authors[0][:200]  # Limit length
        
        return None
    
    def _chinese_year_to_arabic(self, chinese_year: str) -> Optional[str]:
        """Convert Chinese traditional year format to Arabic numerals"""
        chinese_to_arabic = {
            '○': '0', '〇': '0', '零': '0',  # Multiple zero variants
            '一': '1', '二': '2', '三': '3', '四': '4',
            '五': '5', '六': '6', '七': '7', '八': '8', '九': '9'
        }
        try:
            arabic = ''.join(chinese_to_arabic.get(c, c) for c in chinese_year)
            if arabic.isdigit() and len(arabic) == 4:
                return arabic
        except:
            pass
        return None
    
    def _extract_year(self, content: str) -> Optional[str]:
        """Enhanced year extraction with validation"""
        import datetime
        current_year = datetime.datetime.now().year
        
        # Try to find year in first 500 chars (header area) first
        early_years = []
        for pattern in self.metadata_patterns['year']:
            matches = re.findall(pattern, content[:500], re.IGNORECASE)
            for match in matches:
                year_str = match if isinstance(match, str) else match[0]
                
                # Check if it's Chinese traditional format
                if re.match(r'[二三四五六七八九○〇零一]{4}', year_str):
                    arabic_year = self._chinese_year_to_arabic(year_str)
                    if arabic_year:
                        year_str = arabic_year
                
                # Validate year is reasonable
                try:
                    year = int(year_str)
                    if 1900 <= year <= current_year + 1:
                        early_years.append(year_str)
                except ValueError:
                    continue
        
        # If found in header, return the most recent one from header
        if early_years:
            valid_years = [y for y in early_years if int(y) <= current_year]
            if valid_years:
                return max(valid_years)
            return max(early_years)
        
        # Fallback: search in full content (first 3000 chars)
        all_years = []
        for pattern in self.metadata_patterns['year']:
            matches = re.findall(pattern, content[:3000], re.IGNORECASE)
            for match in matches:
                year_str = match if isinstance(match, str) else match[0]
                
                # Check if it's Chinese traditional format
                if re.match(r'[二三四五六七八九○〇零一]{4}', year_str):
                    arabic_year = self._chinese_year_to_arabic(year_str)
                    if arabic_year:
                        year_str = arabic_year
                
                # Validate year is reasonable
                try:
                    year = int(year_str)
                    if 1900 <= year <= current_year + 1:
                        all_years.append(year_str)
                except ValueError:
                    continue
        
        if all_years:
            valid_years = [y for y in all_years if int(y) <= current_year]
            if valid_years:
                return max(valid_years)
            return max(all_years)
        
        return None
    
    def _extract_journal(self, header_footer_text: str, content: str) -> Optional[str]:
        """Extract journal/periodical name from headers/footers"""
        # Try headers/footers first (most reliable for consistent periodical names)
        if header_footer_text:
            for pattern in self.metadata_patterns['journal']:
                match = re.search(pattern, header_footer_text, re.MULTILINE)
                if match:
                    journal = match.group(1).strip()
                    # Clean up whitespace
                    journal = re.sub(r'\s+', ' ', journal)
                    # Validate length (relaxed for Chinese journals)
                    if 3 <= len(journal) <= 100:
                        return journal
        
        # Fallback to content (first 500 chars for better accuracy)
        for pattern in self.metadata_patterns['journal']:
            match = re.search(pattern, content[:500], re.MULTILINE)
            if match:
                journal = match.group(1).strip()
                journal = re.sub(r'\s+', ' ', journal)
                # Relaxed validation for Chinese journals (can be shorter)
                if 3 <= len(journal) <= 100:
                    return journal
        
        return None
    
    def _extract_with_vision(self, pdf_path: str) -> Dict[str, str]:
        """Extract metadata using GPT-4 Vision (optimized for speed)"""
        if not self.client or not VISION_AVAILABLE:
            return {}
        
        # Check vision cache first
        vision_cache = self._get_vision_cache(pdf_path)
        if vision_cache:
            logger.info(f"Using cached vision results for {os.path.basename(pdf_path)}")
            return vision_cache
        
        try:
            # Convert first page of PDF to image (optimized: smaller size, lower quality)
            image_data = self._pdf_page_to_image(pdf_path, page_num=0, dpi=150, quality=75)
            if not image_data:
                return {}
            
            # Prepare the prompt
            prompt = """Analyze this academic paper's first page and extract the following metadata:

1. Title: The main title of the paper (Chinese or English)
2. Authors: All author names (comma-separated, Chinese or English)
3. Year: Publication year (look for formats like 2009, 2009年, or 二○○九年)
4. Journal: Journal or periodical name
   - For Chinese journals, look for 《journal name》 format (e.g., 《二十一世紀》)
   - Extract ONLY the text between 《 and 》, do NOT include 網絡版, 網路版, or other suffixes
   - Also check headers/footers for consistent journal names
5. Volume: Journal volume number (look for 卷, Vol, Volume)
6. Issue: Journal issue number (look for 期, 總第X期, 第X期, No., Issue)
7. Pages: Page range (e.g., "123-145" or "71-79")

IMPORTANT for Chinese journals:
- If you see 《二十一世紀》網絡版, extract journal as "二十一世紀" (NOT "二十一世紀網絡版")
- If you see 總第84期, extract issue as "84"
- If you see 第12期, extract issue as "12"

Return ONLY a JSON object with these exact keys: title, authors, year, journal, volume, issue, pages
If any field is not found, use "Unknown" for text fields or "N/A" for numeric fields.

Example format:
{
  "title": "Machine Learning in Healthcare",
  "authors": "John Doe, Jane Smith",
  "year": "2024",
  "journal": "Journal of AI Research",
  "volume": "15",
  "issue": "3",
  "pages": "123-145"
}"""
            
            # Call GPT-4 Vision (optimized settings)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Faster and cheaper than gpt-4-vision-preview
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}",
                                    "detail": "low"  # Low detail mode = faster + cheaper
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,  # Reduced from 500 (faster response)
                temperature=0.0  # Deterministic (slightly faster)
            )
            
            # Parse response
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (might have markdown code blocks)
            import json
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            metadata = json.loads(result_text)
            logger.info(f"Vision extracted: {metadata}")
            
            # Save to vision cache
            self._save_vision_cache(pdf_path, metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Vision extraction error: {e}")
            return {}
    
    def _pdf_page_to_image(self, pdf_path: str, page_num: int = 0, dpi: int = 150, quality: int = 75) -> Optional[str]:
        """Convert PDF page to base64-encoded image (optimized for speed)
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number to convert (0-indexed)
            dpi: DPI for image conversion (default: 150, lower = faster)
            quality: JPEG quality 0-100 (default: 75, lower = faster)
        """
        try:
            if PDF2IMAGE_AVAILABLE:
                # Use pdf2image (optimized settings)
                images = convert_from_path(
                    pdf_path,
                    first_page=page_num + 1,
                    last_page=page_num + 1,
                    dpi=dpi  # Lower DPI = faster conversion
                )
                if images:
                    img = images[0]
                    # Resize to smaller size for faster upload (max 1536px for low detail)
                    max_size = 1536  # Reduced from 2048
                    if img.width > max_size or img.height > max_size:
                        ratio = min(max_size / img.width, max_size / img.height)
                        new_size = (int(img.width * ratio), int(img.height * ratio))
                        img = img.resize(new_size, Image.Resampling.BILINEAR)  # BILINEAR faster than LANCZOS
                    
                    # Convert to base64 with lower quality
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG", quality=quality, optimize=False)  # optimize=False = faster
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    return img_str
            else:
                # Fallback: Use PyMuPDF if available
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(pdf_path)
                    page = doc[page_num]
                    # Render page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
                    img_data = pix.tobytes("jpeg")
                    img_str = base64.b64encode(img_data).decode()
                    doc.close()
                    return img_str
                except ImportError:
                    logger.warning("Neither pdf2image nor PyMuPDF available for image conversion")
                    return None
                    
        except Exception as e:
            logger.error(f"Error converting PDF to image: {e}")
            return None
    
    def detect_multiple_papers(self, pdf_path: str) -> List[Dict]:
        """Detect if PDF contains multiple papers and split them"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
            
            # Extract full text to analyze structure
            full_text = self._extract_full_text(pdf_path)
            
            # Detect paper boundaries
            paper_boundaries = self._find_paper_boundaries(full_text, total_pages)
            
            if len(paper_boundaries) <= 1:
                # Single paper - process normally
                logger.info(f"{pdf_path}: Single paper detected")
                return [self.extract_from_pdf(pdf_path)]
            
            # Multiple papers detected
            logger.info(f"{pdf_path}: {len(paper_boundaries)} papers detected")
            papers = []
            
            for i, boundary in enumerate(paper_boundaries, 1):
                start_page = boundary['start_page']
                end_page = boundary['end_page']
                
                # Extract metadata for this paper section
                paper_data = self._extract_paper_section(
                    pdf_path, 
                    start_page, 
                    end_page,
                    paper_number=i,
                    total_papers=len(paper_boundaries)
                )
                papers.append(paper_data)
            
            return papers
            
        except Exception as e:
            logger.error(f"Error detecting multiple papers in {pdf_path}: {e}")
            # Fallback to single paper
            return [self.extract_from_pdf(pdf_path)]
    
    def _extract_full_text(self, pdf_path: str) -> str:
        """Extract all text from PDF for analysis"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n\n--- PAGE BREAK ---\n\n"
        except Exception as e:
            logger.warning(f"Full text extraction failed: {e}")
        return text
    
    def _find_paper_boundaries(self, full_text: str, total_pages: int) -> List[Dict]:
        """Find boundaries between multiple papers in the text"""
        boundaries = []
        
        # Split by page breaks
        pages = full_text.split("--- PAGE BREAK ---")
        
        # Patterns that indicate a new paper starting
        new_paper_patterns = [
            r'^[A-Z][A-Za-z\s:]{10,100}$',  # Title-like line (all caps or title case)
            r'^\s*Abstract[\s:]*',  # Abstract section
            r'^\s*ABSTRACT[\s:]*',
            r'^\s*Introduction[\s:]*',  # Introduction section
            r'^\s*INTRODUCTION[\s:]*',
            r'^\s*1\.?\s+Introduction',  # Numbered introduction
            r'^\s*I\.?\s+INTRODUCTION',
            r'^\s*Keywords?[\s:]*',  # Keywords
            r'^\s*KEYWORDS?[\s:]*',
        ]
        
        current_paper_start = 0
        potential_starts = []
        
        for page_num, page_text in enumerate(pages):
            lines = page_text.strip().split('\n')
            
            # Check first few lines of each page
            for line_num, line in enumerate(lines[:10]):
                line = line.strip()
                
                # Skip very short lines
                if len(line) < 10:
                    continue
                
                # Check if line matches new paper pattern
                for pattern in new_paper_patterns:
                    if re.match(pattern, line, re.MULTILINE):
                        # Check if this looks like a genuine new paper start
                        # (not just a section in the middle of a paper)
                        if self._is_likely_paper_start(lines, line_num, page_num):
                            potential_starts.append({
                                'page': page_num,
                                'line': line,
                                'confidence': self._calculate_start_confidence(lines, line_num)
                            })
                        break
        
        # Filter and consolidate potential starts
        if not potential_starts:
            # No clear boundaries found - treat as single paper
            return [{
                'start_page': 0,
                'end_page': total_pages - 1,
                'title': 'Unknown'
            }]
        
        # Sort by confidence and page number
        potential_starts.sort(key=lambda x: (x['page'], -x['confidence']))
        
        # Remove duplicates (multiple matches on same page)
        filtered_starts = []
        last_page = -1
        for start in potential_starts:
            if start['page'] != last_page:
                filtered_starts.append(start)
                last_page = start['page']
        
        # Create boundaries
        for i, start in enumerate(filtered_starts):
            end_page = filtered_starts[i + 1]['page'] - 1 if i + 1 < len(filtered_starts) else total_pages - 1
            
            # Only include if paper has at least 2 pages
            if end_page - start['page'] >= 1:
                boundaries.append({
                    'start_page': start['page'],
                    'end_page': end_page,
                    'title': start['line'][:100]
                })
        
        # If we found boundaries but they don't cover the whole document, add first section
        if boundaries and boundaries[0]['start_page'] > 0:
            boundaries.insert(0, {
                'start_page': 0,
                'end_page': boundaries[0]['start_page'] - 1,
                'title': 'Unknown'
            })
        
        return boundaries if boundaries else [{
            'start_page': 0,
            'end_page': total_pages - 1,
            'title': 'Unknown'
        }]
    
    def _is_likely_paper_start(self, lines: List[str], line_num: int, page_num: int) -> bool:
        """Determine if a line is likely the start of a new paper"""
        # First page is always a potential start
        if page_num == 0:
            return True
        
        # Check if followed by author names or abstract
        next_lines = ' '.join(lines[line_num + 1:line_num + 5]).lower()
        
        indicators = [
            'abstract', 'author', 'university', 'department',
            'email', '@', 'keywords', 'introduction'
        ]
        
        return any(indicator in next_lines for indicator in indicators)
    
    def _calculate_start_confidence(self, lines: List[str], line_num: int) -> float:
        """Calculate confidence that this is a paper start"""
        confidence = 0.5
        
        # Check surrounding context
        context = ' '.join(lines[max(0, line_num - 2):min(len(lines), line_num + 5)]).lower()
        
        # Positive indicators
        if 'abstract' in context:
            confidence += 0.3
        if 'author' in context or 'university' in context:
            confidence += 0.2
        if 'keywords' in context:
            confidence += 0.1
        if '@' in context or 'email' in context:
            confidence += 0.1
        
        # Negative indicators (likely just a section header)
        if 'conclusion' in context or 'references' in context:
            confidence -= 0.3
        if 'section' in context or 'chapter' in context:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _extract_paper_section(self, pdf_path: str, start_page: int, end_page: int, 
                               paper_number: int, total_papers: int) -> Dict:
        """Extract metadata from a specific page range"""
        try:
            # Extract text from the specified page range
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for i in range(start_page, min(end_page + 1, len(pdf.pages))):
                    if i < len(pdf.pages):
                        text += pdf.pages[i].extract_text() or ""
                        text += "\n\n"
            
            # Extract metadata from this section
            metadata = self._enhance_metadata({}, text[:3000])
            
            # Add section information
            metadata['paper_number'] = paper_number
            metadata['total_papers_in_file'] = total_papers
            metadata['page_range'] = f"{start_page + 1}-{end_page + 1}"
            metadata['pages'] = f"{start_page + 1}-{end_page + 1}"
            
            return {
                'title': metadata.get('title', f'Paper {paper_number} (Unknown Title)'),
                'authors': metadata.get('authors', 'Unknown'),
                'year': metadata.get('year', 'Unknown'),
                'volume': metadata.get('volume', 'N/A'),
                'issue': metadata.get('issue', 'N/A'),
                'pages': metadata['page_range'],
                'content_preview': text[:500] if text else '',
                'full_content': text,
                'file_path': pdf_path,
                'is_multi_paper': True,
                'paper_number': paper_number,
                'total_papers': total_papers
            }
            
        except Exception as e:
            logger.error(f"Error extracting paper section: {e}")
            return {
                'title': f'Paper {paper_number} (Error)',
                'authors': 'Unknown',
                'year': 'Unknown',
                'volume': 'N/A',
                'issue': 'N/A',
                'pages': f"{start_page + 1}-{end_page + 1}",
                'content_preview': '',
                'full_content': '',
                'file_path': pdf_path,
                'error': str(e),
                'is_multi_paper': True,
                'paper_number': paper_number,
                'total_papers': total_papers
            }
