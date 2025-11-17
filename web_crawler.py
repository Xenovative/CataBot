import os
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin, urlparse
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import playwright for JavaScript rendering
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.info("Playwright not available. JavaScript-rendered sites may not work. Install with: pip install playwright && playwright install")


class AcademicCrawler:
    """Crawl academic websites and download PDFs"""
    
    def __init__(self, max_concurrent: int = 5, timeout: int = 30):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.session = None
        self.downloaded_urls = set()
        self.html_metadata = {}  # Store metadata extracted from HTML pages
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def extract_metadata_from_html(self, soup: BeautifulSoup, page_url: str) -> Dict:
        """Extract paper metadata from HTML meta tags"""
        metadata = {}
        
        # Common meta tag patterns for academic papers
        meta_mappings = {
            'title': ['citation_title', 'DC.title', 'og:title', 'twitter:title'],
            'authors': ['citation_author', 'DC.creator', 'author'],
            'journal': ['citation_journal_title', 'DC.source', 'citation_conference_title'],
            'year': ['citation_publication_date', 'citation_date', 'DC.date'],
            'volume': ['citation_volume'],
            'issue': ['citation_issue'],
            'pages': ['citation_firstpage', 'citation_lastpage'],
            'doi': ['citation_doi', 'DC.identifier'],
            'abstract': ['citation_abstract', 'DC.description', 'description'],
        }
        
        # Extract from meta tags
        for field, tag_names in meta_mappings.items():
            for tag_name in tag_names:
                meta_tag = soup.find('meta', attrs={'name': tag_name})
                if not meta_tag:
                    meta_tag = soup.find('meta', attrs={'property': tag_name})
                
                if meta_tag and meta_tag.get('content'):
                    content = meta_tag['content'].strip()
                    if field == 'authors':
                        # Collect all author tags
                        if 'authors' not in metadata:
                            metadata['authors'] = []
                        metadata['authors'].append(content)
                    elif field == 'pages':
                        # Combine first and last page
                        if 'pages' not in metadata:
                            metadata['pages'] = content
                        else:
                            metadata['pages'] += f'-{content}'
                    elif field not in metadata:
                        metadata[field] = content
        
        # Join multiple authors
        if 'authors' in metadata and isinstance(metadata['authors'], list):
            metadata['authors'] = '; '.join(metadata['authors'])
        
        # Extract year from date if needed
        if 'year' in metadata and len(metadata['year']) > 4:
            import re
            year_match = re.search(r'(\d{4})', metadata['year'])
            if year_match:
                metadata['year'] = year_match.group(1)
        
        # Try to extract from page content if meta tags not found
        if 'title' not in metadata:
            title_tag = soup.find('h1') or soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text().strip()
        
        logger.info(f"Extracted metadata from {page_url}: {list(metadata.keys())}")
        return metadata
    
    async def crawl_website(self, base_url: str, output_dir: str = 'pdfs', 
                           max_depth: int = 2, use_js_rendering: bool = False) -> List[Dict]:
        """Crawl a website and download all PDFs"""
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Starting crawl of {base_url} (max depth: {max_depth}, JS rendering: {use_js_rendering})")
        
        # Try JavaScript rendering if requested and available
        if use_js_rendering and PLAYWRIGHT_AVAILABLE:
            logger.info("Using JavaScript rendering (Playwright)")
            pdf_links = await self._find_pdf_links_with_js(base_url, max_depth)
        else:
            if use_js_rendering and not PLAYWRIGHT_AVAILABLE:
                logger.warning("JavaScript rendering requested but Playwright not available. Falling back to static crawling.")
            pdf_links = await self._find_pdf_links(base_url, max_depth)
        
        logger.info(f"Found {len(pdf_links)} PDF links")
        
        if len(pdf_links) == 0:
            logger.warning(f"No PDF links found on {base_url}.")
            if not use_js_rendering:
                logger.warning("This might be a JavaScript-rendered site. Try enabling JS rendering or install Playwright.")
            logger.warning("Suggestions: 1) Increase max_depth, 2) Check if site has PDFs, 3) Try JS rendering")
        else:
            logger.info(f"PDF links found: {pdf_links[:5]}{'...' if len(pdf_links) > 5 else ''}")
        
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        tasks = []
        for pdf_url in pdf_links:
            task = self._download_pdf_with_semaphore(pdf_url, output_dir, semaphore)
            tasks.append(task)
        
        # Download with progress bar
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading PDFs"):
            result = await coro
            if result:
                results.append(result)
        
        logger.info(f"Successfully downloaded {len(results)} PDFs out of {len(pdf_links)} links")
        return results
    
    async def _find_pdf_links(self, url: str, max_depth: int, 
                             current_depth: int = 0, visited: set = None) -> List[str]:
        """Recursively find all PDF links on a website"""
        if visited is None:
            visited = set()
        
        if current_depth > max_depth or url in visited:
            return []
        
        visited.add(url)
        pdf_links = []
        
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    return []
                
                content_type = response.headers.get('Content-Type', '')
                
                # Direct PDF link
                if 'application/pdf' in content_type:
                    return [url]
                
                # Parse HTML for links
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract metadata from this page
                page_metadata = self.extract_metadata_from_html(soup, url)
                
                # Find PDFs in meta tags
                for meta in soup.find_all('meta', attrs={'name': 'citation_pdf_url'}):
                    if meta.get('content'):
                        pdf_url = urljoin(url, meta['content'])
                        pdf_links.append(pdf_url)
                        # Store metadata for this PDF
                        self.html_metadata[pdf_url] = page_metadata
                
                # Find all links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    link_text = link.get_text().lower().strip()
                    
                    # Enhanced PDF detection
                    is_pdf = self._is_pdf_link(href, link_text, link)
                    
                    if is_pdf:
                        pdf_links.append(full_url)
                        # If this page has metadata, associate it with the PDF
                        if page_metadata:
                            self.html_metadata[full_url] = page_metadata
                    
                    # Recursively crawl if same domain and not too deep
                    elif current_depth < max_depth:
                        base_domain = urlparse(url).netloc
                        link_domain = urlparse(full_url).netloc
                        
                        # Skip obvious non-page links
                        if self._should_crawl_link(full_url, base_domain, link_domain, visited):
                            sub_pdfs = await self._find_pdf_links(
                                full_url, max_depth, current_depth + 1, visited
                            )
                            pdf_links.extend(sub_pdfs)
        
        except Exception as e:
            logger.warning(f"Error crawling {url}: {e}")
        
        return list(set(pdf_links))  # Remove duplicates
    
    async def _find_pdf_links_with_js(self, url: str, max_depth: int) -> List[str]:
        """Find PDF links using JavaScript rendering with Playwright"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available for JS rendering")
            return []
        
        pdf_links = []
        visited = set()
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Navigate and wait for network to be idle
                logger.info(f"Loading page with JavaScript: {url}")
                await page.goto(url, wait_until='networkidle', timeout=60000)
                
                # Wait a bit more for dynamic content
                await page.wait_for_timeout(2000)
                
                # Get rendered HTML
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract metadata from this page
                page_metadata = self.extract_metadata_from_html(soup, url)
                
                # Find all links in rendered page
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    link_text = link.get_text().lower().strip()
                    
                    if self._is_pdf_link(href, link_text, link):
                        pdf_links.append(full_url)
                        # Store metadata for this PDF
                        if page_metadata:
                            self.html_metadata[full_url] = page_metadata
                        logger.info(f"Found PDF link: {full_url}")
                
                # Also check for dynamically loaded links via JavaScript
                js_links = await page.evaluate('''() => {
                    const links = [];
                    document.querySelectorAll('a[href]').forEach(a => {
                        const href = a.getAttribute('href');
                        if (href && (href.includes('.pdf') || href.includes('pdf') || 
                            a.textContent.toLowerCase().includes('pdf'))) {
                            links.push(a.href);
                        }
                    });
                    return links;
                }''')
                
                for link in js_links:
                    if link not in pdf_links:
                        pdf_links.append(link)
                        # Store metadata for JS-found PDFs too
                        if page_metadata:
                            self.html_metadata[link] = page_metadata
                        logger.info(f"Found PDF link (JS): {link}")
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"Error with JavaScript rendering: {e}")
        
        return list(set(pdf_links))
    
    def _is_pdf_link(self, href: str, link_text: str, link_tag) -> bool:
        """Enhanced PDF detection with multiple heuristics"""
        href_lower = href.lower()
        
        # Direct .pdf extension
        if href_lower.endswith('.pdf'):
            return True
        
        # PDF in URL path or query
        if '.pdf' in href_lower:
            return True
        
        # Common PDF download patterns
        pdf_patterns = [
            'download.php',
            'getpdf',
            'viewpdf',
            'showpdf',
            'pdf.php',
            'paper.php',
            'download.aspx',
            'content_type=pdf',
            'type=pdf',
            'format=pdf',
            'filetype=pdf'
        ]
        
        if any(pattern in href_lower for pattern in pdf_patterns):
            return True
        
        # Link text indicators
        pdf_text_indicators = [
            'pdf',
            'download pdf',
            'full text',
            'full paper',
            'download paper',
            'view pdf',
            'download full text'
        ]
        
        if any(indicator in link_text for indicator in pdf_text_indicators):
            return True
        
        # Check for PDF icon or class
        if link_tag.find('img', alt=re.compile(r'pdf', re.I)):
            return True
        
        link_class = link_tag.get('class', [])
        if isinstance(link_class, list):
            link_class = ' '.join(link_class).lower()
        else:
            link_class = str(link_class).lower()
        
        if 'pdf' in link_class:
            return True
        
        return False
    
    def _should_crawl_link(self, full_url: str, base_domain: str, 
                          link_domain: str, visited: set) -> bool:
        """Determine if a link should be crawled"""
        if base_domain != link_domain:
            return False
        
        if full_url in visited:
            return False
        
        # Skip common non-content URLs
        skip_patterns = [
            '/login', '/signin', '/register', '/logout',
            '/cart', '/checkout', '/account',
            'javascript:', 'mailto:', 'tel:',
            '#', '?print=', '/print/',
            '.jpg', '.png', '.gif', '.css', '.js',
            '/feed', '/rss', '.xml'
        ]
        
        url_lower = full_url.lower()
        if any(pattern in url_lower for pattern in skip_patterns):
            return False
        
        return True
    
    async def _download_pdf_with_semaphore(self, url: str, output_dir: str, 
                                          semaphore: asyncio.Semaphore) -> Dict:
        """Download a PDF with concurrency control"""
        async with semaphore:
            return await self._download_pdf(url, output_dir)
    
    async def _download_pdf(self, url: str, output_dir: str) -> Dict:
        """Download a single PDF file"""
        if url in self.downloaded_urls:
            return None
        
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    logger.warning(f"Failed to download {url}: Status {response.status}")
                    return None
                
                # Verify content type
                content_type = response.headers.get('Content-Type', '').lower()
                
                # Read content
                content = await response.read()
                
                # Verify it's actually a PDF by checking magic bytes
                if not self._is_valid_pdf(content):
                    logger.warning(f"Skipping {url}: Not a valid PDF file (Content-Type: {content_type})")
                    return None
                
                # Generate filename
                filename = self._generate_filename(url)
                filepath = os.path.join(output_dir, filename)
                
                # Save PDF
                with open(filepath, 'wb') as f:
                    f.write(content)
                
                self.downloaded_urls.add(url)
                logger.info(f"Downloaded: {filename} ({len(content)} bytes)")
                
                return {
                    'url': url,
                    'filepath': filepath,
                    'filename': filename,
                    'size': len(content)
                }
        
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None
    
    def _is_valid_pdf(self, content: bytes) -> bool:
        """Check if content is a valid PDF by checking magic bytes"""
        if len(content) < 4:
            return False
        
        # PDF files start with %PDF
        return content[:4] == b'%PDF'
    
    def _generate_filename(self, url: str) -> str:
        """Generate a safe filename from URL"""
        # Extract filename from URL
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        if not filename or not filename.endswith('.pdf'):
            # Generate from URL path
            filename = re.sub(r'[^\w\-_.]', '_', parsed.path.strip('/'))
            if not filename.endswith('.pdf'):
                filename += '.pdf'
        
        # Ensure unique filename
        base, ext = os.path.splitext(filename)
        counter = 1
        while filename in self.downloaded_urls:
            filename = f"{base}_{counter}{ext}"
            counter += 1
        
        return filename
    
    def crawl_directory(self, directory: str) -> List[str]:
        """Find all PDFs in a local directory"""
        pdf_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {directory}")
        return pdf_files
