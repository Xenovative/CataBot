# CataBot Web Application Guide

## 🌐 Web-Based GUI

CataBot now includes a beautiful, modern web interface for easy paper cataloging!

## 🚀 Quick Start

### Windows
```bash
run_webapp.bat
```

### Cross-Platform
```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## ✨ Features

### 1. **Upload Files** 📤
- Drag & drop PDF files
- Multiple file upload
- Real-time progress tracking
- Instant results

### 2. **Crawl Website** 🌐
- Enter any academic website URL
- Configurable crawl depth (1-3 levels)
- Automatic PDF discovery
- Batch download and process

### 3. **Process Directory** 📁
- Process local folders
- Recursive scanning
- Batch processing
- Preserves file structure

## 🎨 Interface Overview

### Main Dashboard
- **Three Tabs**: Upload, Crawl, Directory
- **Real-time Progress**: Visual progress bar with status
- **Statistics Cards**: Papers processed, categories, time
- **Download Options**: All formats available instantly

### Processing Flow
```
1. Select Input Method
   ├─ Upload PDFs
   ├─ Enter URL
   └─ Specify Directory
        ↓
2. Choose Output Format
   ├─ All Formats
   ├─ Excel Only
   ├─ HTML Only
   ├─ JSON Only
   └─ CSV Only
        ↓
3. Start Processing
   └─ Real-time progress
        ↓
4. View Results
   ├─ Statistics
   ├─ Subject Distribution
   └─ Download Files
```

## 📊 Features in Detail

### Upload Tab
- **Drag & Drop**: Simply drag PDF files into the upload area
- **Browse**: Click to select files from your computer
- **File List**: See all selected files with sizes
- **Format Selection**: Choose output format before processing

### Crawl Tab
- **URL Input**: Enter journal or repository URL
- **Depth Control**: 
  - Level 1: Current page only
  - Level 2: Recommended (default)
  - Level 3: Deep crawl
- **Auto Discovery**: Finds all PDF links automatically

### Directory Tab
- **Path Input**: Enter full directory path
- **Server-side**: Processes files on the server
- **Recursive**: Scans all subdirectories
- **Batch Mode**: Handles large collections

### Progress Tracking
- **Visual Progress Bar**: Shows completion percentage
- **Current File**: Displays file being processed
- **File Counter**: Shows X/Y files processed
- **Status Updates**: Real-time status messages

### Results Display
- **Statistics Cards**:
  - Total papers processed
  - Number of subject categories
  - Processing time
  
- **Download Buttons**: One-click download for each format
  
- **Subject Distribution**: Visual breakdown by category

## 🎯 Use Cases

### Scenario 1: Quick Upload
```
1. Click "Upload Files" tab
2. Drag PDFs into upload area
3. Select "Excel Only" format
4. Click "Start Processing"
5. Download Excel file when complete
```

### Scenario 2: Website Crawl
```
1. Click "Crawl Website" tab
2. Enter: https://journal.example.com/archive
3. Set depth to 2
4. Select "All Formats"
5. Click "Start Crawling"
6. Wait for completion
7. Download all formats
```

### Scenario 3: Local Directory
```
1. Click "Local Directory" tab
2. Enter: C:\Research\Papers
3. Select "HTML Only"
4. Click "Process Directory"
5. View beautiful HTML report
```

## 🔧 API Endpoints

The web app exposes a REST API:

### Upload Files
```
POST /api/upload
Content-Type: multipart/form-data

files[]: PDF files
format: output format
```

### Crawl Website
```
POST /api/crawl
Content-Type: application/json

{
  "url": "https://example.com",
  "depth": 2,
  "format": "all"
}
```

### Process Directory
```
POST /api/directory
Content-Type: application/json

{
  "directory": "/path/to/pdfs",
  "format": "all"
}
```

### Check Status
```
GET /api/status/<job_id>

Returns:
{
  "job_id": "job_1",
  "status": "processing",
  "progress": 5,
  "total": 10,
  "current_file": "paper.pdf"
}
```

### Download Results
```
GET /api/download/<job_id>/<format>

Downloads the specified format file
```

## 🎨 Customization

### Change Port
Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Modify UI Colors
Edit `templates/index.html` CSS:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Add Custom Themes
Create new CSS files in `static/` folder

## 🔒 Security Notes

### Production Deployment
1. **Change Secret Key**:
```python
app.config['SECRET_KEY'] = 'your-secure-random-key'
```

2. **Disable Debug Mode**:
```python
app.run(debug=False)
```

3. **Add Authentication**: Implement user login

4. **File Upload Limits**: Already set to 500MB

5. **HTTPS**: Use reverse proxy (nginx/Apache)

## 🌐 Remote Access

### Local Network
```bash
# Find your IP
ipconfig  # Windows
ifconfig  # Linux/Mac

# Access from other devices
http://YOUR_IP:5000
```

### Public Access (Advanced)
Use services like:
- ngrok
- localtunnel
- Cloudflare Tunnel

Example with ngrok:
```bash
ngrok http 5000
```

## 📱 Mobile Support

The interface is fully responsive:
- ✅ Works on phones
- ✅ Works on tablets
- ✅ Touch-friendly
- ✅ Adaptive layout

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(port=8080)
```

### Flask Not Found
```bash
pip install flask flask-cors werkzeug
```

### Upload Fails
- Check file size (max 500MB)
- Ensure `uploads/` directory exists
- Check disk space

### Crawl Timeout
- Reduce crawl depth
- Check website accessibility
- Increase timeout in `config.py`

## 📊 Performance Tips

### For Large Collections
1. **Use Directory Mode**: Faster than upload
2. **Batch Processing**: Process in chunks
3. **Format Selection**: Choose only needed formats
4. **Server Resources**: Ensure adequate RAM

### Optimization
- Close other applications
- Use SSD for faster I/O
- Increase concurrent downloads in `config.py`

## 🔄 Updates

### Check for Updates
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Restart Server
```bash
# Stop: Ctrl+C
# Start: python app.py
```

## 📚 Integration

### Embed in Website
```html
<iframe src="http://localhost:5000" width="100%" height="800px"></iframe>
```

### API Integration
```javascript
// Upload files via JavaScript
const formData = new FormData();
formData.append('files[]', file);

fetch('http://localhost:5000/api/upload', {
    method: 'POST',
    body: formData
}).then(r => r.json())
  .then(data => console.log(data.job_id));
```

## 🎓 Examples

### Example 1: Research Lab
Upload 50 papers → Get Excel catalog → Share with team

### Example 2: Library
Crawl journal website → Download all PDFs → Generate HTML catalog

### Example 3: Student
Process thesis PDFs → Get subject classification → Create bibliography

## 💡 Tips

1. **Bookmark**: Save http://localhost:5000 for quick access
2. **Multiple Jobs**: Can process multiple batches simultaneously
3. **Download All**: Use "All Formats" for maximum flexibility
4. **Check Config**: Green checkmark = OpenAI configured
5. **Progress**: Don't close browser during processing

## 🆘 Support

### Common Issues

**Q: Page won't load**
A: Ensure Flask is running, check console for errors

**Q: Upload stuck at 0%**
A: Check browser console, try smaller batch

**Q: Results not showing**
A: Refresh page, check job status via API

**Q: Download fails**
A: Check output directory permissions

## 🚀 Next Steps

1. **Try Demo**: Upload a few test PDFs
2. **Configure API**: Add OpenAI key for better classification
3. **Customize**: Modify colors and layout
4. **Deploy**: Set up for production use
5. **Integrate**: Connect with your existing systems

---

**Enjoy the CataBot Web Interface!** 🎉

Access at: http://localhost:5000
