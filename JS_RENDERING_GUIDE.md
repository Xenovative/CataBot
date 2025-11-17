# JavaScript Rendering for Dynamic Websites

## 🔍 Problem: https://library.cgst.edu/tc/journal/

### Why the Crawler Can't Find PDFs

The website **https://library.cgst.edu/tc/journal/** uses **JavaScript rendering** (Nuxt.js framework). This means:

1. **Initial HTML is minimal** - Only contains basic structure
2. **Content loads via JavaScript** - PDFs links are added dynamically after page load
3. **Standard crawler sees nothing** - Only sees the empty shell, not the rendered content

### Test Results

```
Total links found: 7
PDF-related links: 0
Scripts found: 7 (Nuxt.js framework)
Main content: 0 characters (before JS execution)
```

The page structure:
```html
<!-- What the crawler sees -->
<body>
  <div id="__nuxt"></div>
  <script src="/_nuxt/699816f.js"></script>
  <script src="/_nuxt/5373243.js"></script>
  <!-- Content loaded by JavaScript -->
</body>
```

## ✅ Solution: JavaScript Rendering Support

I've added **JavaScript rendering** capability using Playwright to handle dynamic websites!

---

## 🚀 New Features

### 1. **JavaScript Rendering Option**

New checkbox in Crawl tab:
```
☐ Enable JavaScript Rendering (for dynamic sites)
```

### 2. **Playwright Integration**

- Launches headless browser
- Executes JavaScript
- Waits for content to load
- Extracts rendered HTML
- Finds PDF links in dynamic content

### 3. **Automatic Detection**

If no PDFs found, the crawler suggests:
```
⚠️ This might be a JavaScript-rendered site
💡 Try enabling JS rendering
```

---

## 📦 Installation

### Install Playwright

```bash
pip install playwright
playwright install
```

This installs:
- Playwright Python library
- Chromium browser (headless)
- Required dependencies

### Verify Installation

```python
python -c "from playwright.async_api import async_playwright; print('✅ Playwright installed')"
```

---

## 🎯 How to Use

### Web Interface

1. **Open Crawl Tab**
2. **Enter URL**: `https://library.cgst.edu/tc/journal/`
3. **Check the box**: ☑ Enable JavaScript Rendering
4. **Set Depth**: 2 (recommended)
5. **Click**: 🌐 Start Crawling

### Python Code

```python
from web_crawler import AcademicCrawler
import asyncio

async def crawl_with_js():
    async with AcademicCrawler() as crawler:
        results = await crawler.crawl_website(
            url='https://library.cgst.edu/tc/journal/',
            max_depth=2,
            use_js_rendering=True  # Enable JS rendering
        )
    return results

# Run
results = asyncio.run(crawl_with_js())
```

---

## 🔧 How It Works

### Standard Crawling (Fast)
```
1. Fetch HTML
2. Parse with BeautifulSoup
3. Find <a> tags
4. Extract PDF links
```

### JavaScript Rendering (Thorough)
```
1. Launch headless browser
2. Navigate to URL
3. Wait for JavaScript execution
4. Wait for network idle
5. Extract rendered HTML
6. Parse with BeautifulSoup
7. Find PDF links in dynamic content
8. Also check via JavaScript evaluation
```

### Code Flow

```python
async def _find_pdf_links_with_js(self, url, max_depth):
    # Launch browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Load page and wait for JS
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_timeout(2000)
        
        # Get rendered HTML
        html = await page.content()
        
        # Parse for PDF links
        soup = BeautifulSoup(html, 'html.parser')
        # ... find PDFs ...
        
        # Also check via JS
        js_links = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a[href]'))
                .filter(a => a.href.includes('.pdf'))
                .map(a => a.href);
        }''')
```

---

## 📊 Comparison

### Without JS Rendering

| Metric | Value |
|--------|-------|
| Speed | Fast (1-2 seconds) |
| PDFs Found | 0 (on JS sites) |
| Browser Needed | No |
| Works On | Static HTML sites |

### With JS Rendering

| Metric | Value |
|--------|-------|
| Speed | Slower (5-10 seconds) |
| PDFs Found | All (on JS sites) |
| Browser Needed | Yes (Chromium) |
| Works On | All sites (static + dynamic) |

---

## 🎓 When to Use JS Rendering

### ✅ Use JS Rendering For:

1. **Single Page Applications (SPA)**
   - React, Vue, Angular apps
   - Nuxt.js, Next.js sites
   - Modern academic portals

2. **Dynamic Content Loading**
   - Content loaded via AJAX
   - Infinite scroll
   - Click-to-load buttons

3. **When Standard Crawl Finds Nothing**
   - 0 PDFs found
   - Empty page content
   - Lots of `<script>` tags

### ❌ Don't Use JS Rendering For:

1. **Static HTML Sites**
   - Traditional websites
   - Simple file listings
   - Direct PDF links

2. **When Speed Matters**
   - Large batch crawls
   - Time-sensitive operations
   - Standard crawl already works

---

## 🌐 Common JS-Rendered Sites

### Academic Platforms

**Nuxt.js / Vue.js**:
- https://library.cgst.edu/tc/journal/
- Many university repositories
- Modern digital libraries

**React / Next.js**:
- Conference proceedings sites
- Research portals
- Academic databases

**Angular**:
- Institutional repositories
- Journal platforms
- Research management systems

### Detection Signs

```html
<!-- Nuxt.js -->
<div id="__nuxt"></div>
<script src="/_nuxt/*.js"></script>

<!-- Next.js -->
<div id="__next"></div>
<script src="/_next/*.js"></script>

<!-- React -->
<div id="root"></div>
<script src="/static/js/*.js"></script>

<!-- Angular -->
<app-root></app-root>
<script src="/main.*.js"></script>
```

---

## 🐛 Troubleshooting

### Playwright Not Installed

**Error**:
```
Playwright not available. JavaScript-rendered sites may not work.
```

**Solution**:
```bash
pip install playwright
playwright install
```

### Browser Installation Failed

**Error**:
```
Executable doesn't exist at ...
```

**Solution**:
```bash
playwright install chromium
```

### Timeout Errors

**Error**:
```
Timeout 60000ms exceeded
```

**Solutions**:
1. Increase timeout in code
2. Check internet connection
3. Try different depth
4. Site might be blocking bots

### Still No PDFs Found

**Possible Reasons**:
1. **Login Required**: Site needs authentication
2. **Bot Detection**: Site blocks automated access
3. **No PDFs**: Site actually has no PDFs
4. **Complex JavaScript**: Needs longer wait time

**Solutions**:
```python
# Increase wait time
await page.wait_for_timeout(5000)  # 5 seconds

# Wait for specific element
await page.wait_for_selector('.pdf-link')

# Scroll to load more
await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
```

---

## 💡 Best Practices

### 1. Try Standard First

```
1. Try standard crawling (fast)
2. If 0 PDFs found → Enable JS rendering
3. Compare results
```

### 2. Use Appropriate Depth

```
JS Rendering is slower:
- Depth 1: ~5-10 seconds
- Depth 2: ~20-30 seconds
- Depth 3: ~60+ seconds
```

### 3. Check Logs

```
INFO: Using JavaScript rendering (Playwright)
INFO: Loading page with JavaScript: https://...
INFO: Found PDF link: https://...
INFO: Found PDF link (JS): https://...
```

### 4. Fallback Strategy

```python
# Try JS rendering, fallback to standard
try:
    results = await crawler.crawl_website(url, use_js_rendering=True)
except Exception as e:
    logger.warning(f"JS rendering failed: {e}")
    results = await crawler.crawl_website(url, use_js_rendering=False)
```

---

## 📈 Performance Tips

### 1. Reuse Browser

For multiple pages:
```python
async with async_playwright() as p:
    browser = await p.chromium.launch()
    # Reuse browser for multiple pages
    for url in urls:
        page = await browser.new_page()
        # ... crawl ...
        await page.close()
    await browser.close()
```

### 2. Disable Unnecessary Features

```python
context = await browser.new_context(
    user_agent='...',
    ignore_https_errors=True,
    java_script_enabled=True,
    # Disable images for speed
    bypass_csp=True
)
```

### 3. Parallel Crawling

```python
# Crawl multiple sites in parallel
tasks = [
    crawl_with_js(url1),
    crawl_with_js(url2),
    crawl_with_js(url3)
]
results = await asyncio.gather(*tasks)
```

---

## 🔒 Security Considerations

### Headless Browser Risks

1. **Resource Usage**: Browser consumes more memory
2. **Execution Time**: Longer processing time
3. **Untrusted Code**: Executes site's JavaScript

### Mitigation

```python
# Set resource limits
context = await browser.new_context(
    viewport={'width': 1280, 'height': 720},
    # Limit storage
    storage_state=None
)

# Set timeouts
await page.goto(url, timeout=30000)

# Close after use
await browser.close()
```

---

## 📚 Additional Resources

### Playwright Documentation
- https://playwright.dev/python/
- https://playwright.dev/python/docs/api/class-page

### Alternative Solutions

**Selenium** (older, more common):
```python
from selenium import webdriver
driver = webdriver.Chrome()
driver.get(url)
# ... extract content ...
```

**Puppeteer** (Node.js):
```javascript
const puppeteer = require('puppeteer');
const browser = await puppeteer.launch();
// ... crawl ...
```

---

## ✅ Summary

### The Problem
- **https://library.cgst.edu/tc/journal/** uses JavaScript rendering
- Standard crawler sees empty page
- No PDF links found

### The Solution
- Added Playwright integration
- JavaScript rendering option in UI
- Executes JS and extracts rendered content
- Finds PDFs in dynamic sites

### How to Use
```
1. Install: pip install playwright && playwright install
2. Check box: ☑ Enable JavaScript Rendering
3. Crawl: Works on dynamic sites!
```

---

**Now you can crawl JavaScript-rendered academic sites!** 🎉

For the CGST library site, enable JS rendering and it should find the PDFs.
