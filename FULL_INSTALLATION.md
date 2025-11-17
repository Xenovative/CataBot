# CataBot Full Installation Guide

## What Gets Installed

The deployment script now installs **everything** needed to run CataBot with all features enabled.

### System Dependencies

#### Core
- Python 3.x
- pip (Python package manager)
- python3-venv (Virtual environments)
- git

#### PDF Processing
- **poppler-utils** - PDF rendering and manipulation
- **tesseract-ocr** - OCR (Optical Character Recognition)
- **libtesseract-dev** - Tesseract development files
- **libpoppler-cpp-dev** - Poppler C++ development files

#### Vision Extraction
- **libjpeg-dev** - JPEG image processing
- **zlib1g-dev** - Compression library

#### JavaScript Rendering (Playwright)
- **libnss3** - Network Security Services
- **libnspr4** - Netscape Portable Runtime
- **libatk1.0-0** - Accessibility Toolkit
- **libatk-bridge2.0-0** - ATK bridge
- **libcups2** - Common UNIX Printing System
- **libdrm2** - Direct Rendering Manager
- **libxkbcommon0** - Keyboard handling
- **libxcomposite1** - X Composite extension
- **libxdamage1** - X Damage extension
- **libxfixes3** - X Fixes extension
- **libxrandr2** - X RandR extension
- **libgbm1** - Generic Buffer Management
- **libasound2** - ALSA sound library

#### Optional
- **nginx** - Reverse proxy (only if you choose to install it)

### Python Packages

All packages from `requirements.txt` are installed:

#### Core Functionality
- **Flask** - Web framework
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Werkzeug** - WSGI utility library
- **requests** - HTTP library
- **beautifulsoup4** - HTML parsing
- **aiohttp** - Async HTTP client

#### PDF Processing
- **PyPDF2** - PDF manipulation
- **pdfplumber** - PDF text extraction
- **PyMuPDF** (fitz) - Advanced PDF processing

#### Vision Extraction
- **Pillow** - Image processing
- **pdf2image** - PDF to image conversion

#### AI & Classification
- **openai** - OpenAI API client
- **python-dotenv** - Environment variable management

#### Data Processing & Output
- **pandas** - Data manipulation
- **openpyxl** - Excel file generation
- **tqdm** - Progress bars

#### JavaScript Rendering
- **playwright** - Browser automation
  - Includes Chromium browser installation

### Application Structure

The deployment creates:

```
/opt/catabot/
├── app.py                 # Main Flask application
├── pdf_extractor.py       # PDF extraction module
├── web_crawler.py         # Web crawling module
├── ai_classifier.py       # AI classification module
├── catalog_generator.py   # Catalog generation
├── journal_sources.py     # Journal detection
├── config.py             # Configuration
├── requirements.txt      # Python dependencies
├── .env                  # Environment configuration
├── .env.example          # Environment template
├── start.sh              # Startup script
├── venv/                 # Python virtual environment
├── pdfs/                 # Downloaded PDFs
├── uploads/              # Uploaded files
├── job_history/          # Job history JSON files
├── logs/                 # Application logs
├── output/               # Generated catalogs
├── templates/            # Flask templates
└── static/               # Static files
```

## Features Enabled

### ✅ Basic Features (Always Available)
- PDF upload and processing
- Metadata extraction
- Basic text extraction
- Catalog generation (Excel, JSON, CSV, HTML)
- Web crawling for PDFs
- Keyword-based classification

### ✅ Vision Extraction (Now Included)
- Enhanced metadata extraction using OpenAI Vision API
- Better accuracy for complex PDFs
- Image-based text recognition
- Layout analysis

### ✅ JavaScript Rendering (Now Included)
- Crawl JavaScript-heavy websites
- Handle dynamic content loading
- Support for modern web frameworks
- Automated browser interaction

### ✅ AI Classification (Requires API Key)
- OpenAI GPT-based classification
- 18+ subject categories
- Confidence scoring
- Custom category support

## Installation

### One-Command Install

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

The script will:
1. ✅ Update system packages
2. ✅ Install all system dependencies
3. ✅ Create application user
4. ✅ Set up directory structure
5. ✅ Copy application files
6. ✅ Create Python virtual environment
7. ✅ Install all Python packages
8. ✅ Install Playwright browsers (Chromium)
9. ✅ Set correct permissions
10. ✅ Create systemd service
11. ⚠️ Optionally configure Nginx (you can skip)
12. ✅ Create .env configuration
13. ✅ Start services
14. ✅ Configure firewall
15. ✅ Create maintenance scripts

### What You Need to Provide

**Required:**
- Root/sudo access
- Ubuntu 20.04+ or Debian 11+ (or similar)

**Optional (for full functionality):**
- OpenAI API key (for AI classification and vision extraction)
- Domain name (for Nginx/SSL setup)

## Post-Installation Configuration

### 1. Add API Keys (Optional but Recommended)

```bash
sudo nano /opt/catabot/.env
```

Add your API keys:
```bash
OPENAI_API_KEY=sk-your-key-here
```

Then restart:
```bash
sudo systemctl restart catabot
```

### 2. Test All Features

#### Test Basic Functionality
```bash
curl http://localhost:5000
```

#### Test Vision Extraction
- Upload a PDF through the web interface
- Check if metadata is extracted accurately

#### Test JavaScript Rendering
- Try crawling a JavaScript-heavy website
- Enable "Use JavaScript Rendering" option

#### Test AI Classification
- Process some PDFs
- Check if subjects are classified correctly

## Verification

Run the verification script:

```bash
chmod +x verify_deployment.sh
sudo ./verify_deployment.sh
```

This checks:
- ✅ All system dependencies installed
- ✅ Python packages available
- ✅ Playwright browsers installed
- ✅ All directories created
- ✅ Permissions correct
- ✅ Service running
- ✅ Port accessible

## Disk Space Requirements

- **Base installation**: ~500MB
- **With Playwright browsers**: ~800MB
- **With PDFs and data**: Variable (depends on usage)

**Recommended**: At least 5GB free space

## Memory Requirements

- **Minimum**: 1GB RAM
- **Recommended**: 2GB+ RAM
- **With vision extraction**: 4GB+ RAM recommended

## Troubleshooting

### Playwright Installation Fails

```bash
# Install manually
cd /opt/catabot
sudo -u catabot bash -c "source venv/bin/activate && python3 -m playwright install chromium"
```

### Vision Extraction Not Working

```bash
# Check if Pillow is installed
/opt/catabot/venv/bin/python3 -c "from PIL import Image; print('Pillow OK')"

# Check if pdf2image works
/opt/catabot/venv/bin/python3 -c "import pdf2image; print('pdf2image OK')"
```

### Missing System Dependencies

```bash
# Reinstall all dependencies
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr libtesseract-dev \
    libpoppler-cpp-dev libjpeg-dev zlib1g-dev libnss3 libnspr4 \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

## Updating

To update CataBot with new dependencies:

```bash
cd /opt/catabot
sudo systemctl stop catabot

# Pull latest code
sudo -u catabot git pull

# Update dependencies
sudo -u catabot bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Update Playwright browsers
sudo -u catabot bash -c "source venv/bin/activate && python3 -m playwright install chromium"

sudo systemctl start catabot
```

## Feature Comparison

| Feature | Without Full Install | With Full Install |
|---------|---------------------|-------------------|
| PDF Upload | ✅ | ✅ |
| Basic Metadata | ✅ | ✅ |
| Vision Extraction | ❌ | ✅ |
| JS Website Crawling | ❌ | ✅ |
| Static Website Crawling | ✅ | ✅ |
| AI Classification | ✅ (with API key) | ✅ (with API key) |
| Keyword Classification | ✅ | ✅ |
| Excel/JSON/CSV Export | ✅ | ✅ |
| Complex PDF Handling | Limited | ✅ Enhanced |

## Summary

The deployment script now installs **everything** you need:

✅ All system dependencies
✅ All Python packages (including optional ones)
✅ Playwright browsers for JavaScript rendering
✅ Vision extraction libraries
✅ Complete directory structure
✅ Proper permissions and security
✅ Systemd service
✅ Maintenance scripts

**You just need to:**
1. Run `sudo ./deploy.sh`
2. Add your OpenAI API key (optional)
3. Start using CataBot with all features!

No manual installation of optional dependencies needed anymore!
