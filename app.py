"""
CataBot Web Application
Flask-based GUI for academic paper cataloging
"""

import os
import json
import asyncio
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import logging

from pdf_extractor import PDFExtractor
from web_crawler import AcademicCrawler
from pdf_extractor import PDFExtractor
from ai_classifier import AIClassifier
from catalog_generator import CatalogGenerator
from journal_sources import detect_journal_from_url
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'catabot-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('output', exist_ok=True)
os.makedirs('job_history', exist_ok=True)

# Global state for job tracking
jobs = {}
job_counter = 0

# Initialize components
# Load settings to check vision extraction preference and custom categories
settings_file = 'settings.json'
use_vision = True  # Default to enabled
custom_categories = None
if os.path.exists(settings_file):
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            use_vision = settings.get('use_vision_extraction', True)
            custom_categories = settings.get('custom_categories', None)
    except:
        pass

pdf_extractor = PDFExtractor(use_vision=use_vision)
classifier = AIClassifier(custom_categories=custom_categories)
catalog_generator = CatalogGenerator()


class ProcessingJob:
    """Track processing job status"""
    def __init__(self, job_id, job_type, source_url=None):
        self.job_id = job_id
        self.job_type = job_type
        self.status = 'pending'
        self.progress = 0
        self.total = 0
        self.current_file = ''
        self.results = []
        self.output_files = {}
        self.error = None
        self.start_time = datetime.now()
        self.end_time = None
        self.source_url = source_url  # Store original URL for re-fetching
    
    def to_dict(self):
        """Convert job to dictionary for JSON serialization"""
        return {
            'job_id': self.job_id,
            'job_type': self.job_type,
            'status': self.status,
            'progress': self.progress,
            'total': self.total,
            'current_file': self.current_file,
            'results': self.results,
            'output_files': self.output_files,
            'error': self.error,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'source_url': self.source_url
        }
    
    @staticmethod
    def from_dict(data):
        """Create job from dictionary"""
        job = ProcessingJob(data['job_id'], data['job_type'], data.get('source_url'))
        job.status = data['status']
        job.progress = data['progress']
        job.total = data['total']
        job.current_file = data['current_file']
        job.results = data['results']
        job.output_files = data['output_files']
        job.error = data['error']
        job.start_time = datetime.fromisoformat(data['start_time'])
        job.end_time = datetime.fromisoformat(data['end_time']) if data['end_time'] else None
        return job


def save_job_to_history(job):
    """Save completed job to persistent storage"""
    try:
        job_file = os.path.join('job_history', f'{job.job_id}.json')
        with open(job_file, 'w', encoding='utf-8') as f:
            json.dump(job.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved job {job.job_id} to history")
    except Exception as e:
        logger.error(f"Failed to save job to history: {e}")


def load_job_from_history(job_id):
    """Load job from persistent storage"""
    try:
        job_file = os.path.join('job_history', f'{job_id}.json')
        if os.path.exists(job_file):
            with open(job_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ProcessingJob.from_dict(data)
    except Exception as e:
        logger.error(f"Failed to load job from history: {e}")
    return None


def get_all_job_history():
    """Get all jobs from history"""
    jobs_list = []
    try:
        for filename in os.listdir('job_history'):
            if filename.endswith('.json'):
                job_id = filename[:-5]  # Remove .json
                job = load_job_from_history(job_id)
                if job:
                    jobs_list.append({
                        'job_id': job.job_id,
                        'job_type': job.job_type,
                        'status': job.status,
                        'start_time': job.start_time.isoformat(),
                        'end_time': job.end_time.isoformat() if job.end_time else None,
                        'results_count': len(job.results),
                        'error': job.error,
                        'source_url': job.source_url
                    })
        # Sort by start time, newest first
        jobs_list.sort(key=lambda x: x['start_time'], reverse=True)
    except Exception as e:
        logger.error(f"Failed to load job history: {e}")
    return jobs_list


def process_pdfs_background(job_id, pdf_files, output_format='all', source_url=None, html_metadata=None):
    """Background task to process PDFs"""
    job = jobs[job_id]
    html_metadata = html_metadata or {}
    
    try:
        job.status = 'processing'
        job.total = len(pdf_files)
        
        # Detect journal from source URL if provided
        source_journal_info = {}
        if source_url:
            source_journal_info = detect_journal_from_url(source_url)
            if source_journal_info.get('journal'):
                logger.info(f"Detected journal from source: {source_journal_info['journal']}")
        
        papers = []
        for i, pdf_path in enumerate(pdf_files):
            # Check if job was cancelled
            if job.status == 'cancelled':
                logger.info(f"Job {job_id} was cancelled, stopping processing")
                save_job_to_history(job)
                return
            
            job.current_file = os.path.basename(pdf_path)
            job.progress = i + 1
            
            try:
                # Detect and split multiple papers in single PDF
                detected_papers = pdf_extractor.detect_multiple_papers(pdf_path)
                
                if len(detected_papers) > 1:
                    logger.info(f"{pdf_path}: Found {len(detected_papers)} papers in single PDF")
                
                # Merge HTML metadata with PDF extraction
                if pdf_path in html_metadata:
                    html_meta = html_metadata[pdf_path]
                    logger.info(f"Found HTML metadata for {pdf_path}: {list(html_meta.keys())}")
                    for paper in detected_papers:
                        # Use HTML metadata as fallback for missing fields
                        enhanced_fields = []
                        for field in ['title', 'authors', 'journal', 'year', 'volume', 'issue', 'pages', 'doi', 'abstract']:
                            if (not paper.get(field) or paper.get(field) in ['N/A', 'Unknown', '未知']) and html_meta.get(field):
                                paper[field] = html_meta[field]
                                enhanced_fields.append(field)
                        if enhanced_fields:
                            logger.info(f"Enhanced {', '.join(enhanced_fields)} from HTML metadata for {pdf_path}")
                else:
                    logger.warning(f"No HTML metadata found for {pdf_path}. Available keys: {list(html_metadata.keys())[:5]}")
                
                papers.extend(detected_papers)
                
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                continue
        
        logger.info(f"Total papers extracted: {len(papers)} from {len(pdf_files)} PDF files")
        
        # Apply source journal info AFTER all extraction (including vision) is complete
        if source_journal_info.get('journal') and source_journal_info.get('confidence') == 'high':
            # For high-confidence sources (known journal sites), always apply source journal
            # This overrides individual extraction which may be inconsistent
            corrected_count = 0
            for paper in papers:
                old_journal = paper.get('journal', 'Unknown')
                paper['journal'] = source_journal_info['journal']
                if old_journal != source_journal_info['journal']:
                    corrected_count += 1
            logger.info(f"Applied source journal '{source_journal_info['journal']}' to all {len(papers)} papers ({corrected_count} corrected)")
        elif source_journal_info.get('journal'):
            # For low-confidence sources, only apply to Unknown/N/A
            corrected_count = 0
            for paper in papers:
                if not paper.get('journal') or paper.get('journal') in ['N/A', 'Unknown', '未知']:
                    paper['journal'] = source_journal_info['journal']
                    corrected_count += 1
            if corrected_count > 0:
                logger.info(f"Applied source journal '{source_journal_info['journal']}' to {corrected_count} papers with missing journal")
        
        # Check if job was cancelled before classification
        if job.status == 'cancelled':
            logger.info(f"Job {job_id} was cancelled before classification")
            save_job_to_history(job)
            return
        
        # Classify papers
        job.current_file = 'Classifying papers...'
        papers = classifier.batch_classify(papers)
        job.results = papers
        
        # Check if job was cancelled before catalog generation
        if job.status == 'cancelled':
            logger.info(f"Job {job_id} was cancelled before catalog generation")
            save_job_to_history(job)
            return
        
        # Generate catalog
        job.current_file = 'Generating catalog...'
        output_files = catalog_generator.generate_catalog(papers, format=output_format)
        job.output_files = output_files
        
        job.status = 'completed'
        job.end_time = datetime.now()
        save_job_to_history(job)
        
    except Exception as e:
        job.status = 'failed'
        job.error = str(e)
        job.end_time = datetime.now()
        save_job_to_history(job)
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)


async def crawl_website_background(job_id, url, max_depth=2, output_format='all', use_js=False):
    """Background task to crawl website"""
    job = jobs[job_id]
    
    try:
        job.status = 'crawling'
        job.current_file = f'Discovering PDFs on {url}...'
        job.total = 0
        job.progress = 0
        
        # Crawl and download PDFs with progress updates
        async with AcademicCrawler() as crawler:
            # First, find all PDF links
            job.current_file = f'Scanning website (depth: {max_depth})...'
            if use_js:
                pdf_links = await crawler._find_pdf_links_with_js(url, max_depth)
            else:
                pdf_links = await crawler._find_pdf_links(url, max_depth)
            
            # Check if job was cancelled during scanning
            if job.status == 'cancelled':
                logger.info(f"Crawl job {job_id} was cancelled during scanning")
                save_job_to_history(job)
                return
            
            logger.info(f"Found {len(pdf_links)} PDF links")
            
            if len(pdf_links) == 0:
                job.status = 'failed'
                job.error = 'No PDFs found on this website'
                job.end_time = datetime.now()
                save_job_to_history(job)
                return
            
            # Update job with total PDFs to download
            job.total = len(pdf_links)
            job.current_file = f'Downloading {len(pdf_links)} PDFs...'
            
            # Download PDFs with progress tracking
            downloaded_files = []
            semaphore = asyncio.Semaphore(crawler.max_concurrent)
            
            async def download_with_progress(pdf_url, output_dir):
                # Check if job was cancelled before starting download
                if job.status == 'cancelled':
                    return None
                result = await crawler._download_pdf_with_semaphore(pdf_url, output_dir, semaphore)
                # Check if job was cancelled after download
                if job.status == 'cancelled':
                    return None
                if result:
                    job.progress += 1
                    job.current_file = f'Downloaded: {os.path.basename(result["filepath"])}'
                    downloaded_files.append(result)
                return result
            
            # Download in batches to allow more frequent cancellation checks
            batch_size = 10
            for i in range(0, len(pdf_links), batch_size):
                # Check if cancelled before each batch
                if job.status == 'cancelled':
                    logger.info(f"Crawl job {job_id} was cancelled during download batch {i//batch_size + 1}")
                    save_job_to_history(job)
                    return
                
                batch = pdf_links[i:i+batch_size]
                tasks = [download_with_progress(pdf_url, 'pdfs') for pdf_url in batch]
                await asyncio.gather(*tasks)
            
            # Check if job was cancelled during download
            if job.status == 'cancelled':
                logger.info(f"Crawl job {job_id} was cancelled during download")
                save_job_to_history(job)
                return
            
            logger.info(f"Successfully downloaded {len(downloaded_files)} PDFs")
            
            # Enhance downloaded files with HTML metadata
            logger.info(f"Total HTML metadata entries: {len(crawler.html_metadata)}")
            for file_info in downloaded_files:
                pdf_url = file_info.get('url')
                if pdf_url and pdf_url in crawler.html_metadata:
                    file_info['html_metadata'] = crawler.html_metadata[pdf_url]
                    logger.info(f"Associated HTML metadata with {file_info['filepath']}: {list(crawler.html_metadata[pdf_url].keys())}")
                else:
                    logger.warning(f"No HTML metadata for URL: {pdf_url}")
        
        if not downloaded_files:
            job.status = 'failed'
            job.error = 'Failed to download any PDFs'
            job.end_time = datetime.now()
            save_job_to_history(job)
            return
        
        # Process downloaded PDFs with source URL for journal detection
        pdf_files = [f['filepath'] for f in downloaded_files]
        html_metadata_map = {f['filepath']: f.get('html_metadata', {}) for f in downloaded_files}
        process_pdfs_background(job_id, pdf_files, output_format, source_url=url, html_metadata=html_metadata_map)
        
    except Exception as e:
        job.status = 'failed'
        job.error = str(e)
        job.end_time = datetime.now()
        save_job_to_history(job)
        logger.error(f"Crawl job {job_id} failed: {e}", exc_info=True)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Upload PDF files"""
    global job_counter
    
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    output_format = request.form.get('format', 'all')
    
    if not files:
        return jsonify({'error': 'No files selected'}), 400
    
    # Save uploaded files
    uploaded_paths = []
    for file in files:
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_paths.append(filepath)
    
    if not uploaded_paths:
        return jsonify({'error': 'No valid PDF files'}), 400
    
    # Create job
    job_counter += 1
    job_id = f"job_{job_counter}"
    job = ProcessingJob(job_id, 'upload')
    jobs[job_id] = job
    
    # Start processing in background
    thread = threading.Thread(
        target=process_pdfs_background,
        args=(job_id, uploaded_paths, output_format)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'message': f'Processing {len(uploaded_paths)} files'
    })


@app.route('/api/crawl', methods=['POST'])
def crawl_website():
    """Crawl a website for PDFs"""
    global job_counter
    
    data = request.get_json()
    url = data.get('url')
    depth = int(data.get('depth', 2))
    output_format = data.get('format', 'all')
    use_js = data.get('use_js_rendering', False)
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Create job
    job_counter += 1
    job_id = f"crawl_{job_counter}"
    job = ProcessingJob(job_id, 'crawl', source_url=url)
    jobs[job_id] = job
    
    # Start processing in background
    thread = threading.Thread(
        target=lambda: asyncio.run(crawl_website_background(job_id, url, depth, output_format, use_js))
    )
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'message': f'Crawling {url}'
    })


@app.route('/api/directory', methods=['POST'])
def process_directory():
    """Process local directory"""
    global job_counter
    
    data = request.get_json()
    directory = data.get('directory')
    output_format = data.get('format', 'all')
    
    if not directory or not os.path.exists(directory):
        return jsonify({'error': 'Invalid directory'}), 400
    
    # Find all PDFs
    crawler = AcademicCrawler()
    pdf_files = crawler.crawl_directory(directory)
    
    if not pdf_files:
        return jsonify({'error': 'No PDFs found in directory'}), 400
    
    # Create job
    job_counter += 1
    job_id = f"job_{job_counter}"
    job = ProcessingJob(job_id, 'directory')
    jobs[job_id] = job
    
    # Start processing
    thread = threading.Thread(
        target=process_pdfs_background,
        args=(job_id, pdf_files, output_format)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'message': f'Processing {len(pdf_files)} files from directory'
    })


@app.route('/api/status/<job_id>')
def job_status(job_id):
    """Get job status"""
    job = jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    response = {
        'job_id': job.job_id,
        'status': job.status,
        'progress': job.progress,
        'total': job.total,
        'current_file': job.current_file,
        'start_time': job.start_time.isoformat(),
        'results_count': len(job.results),  # Include current count even during processing
    }
    
    if job.end_time:
        response['end_time'] = job.end_time.isoformat()
        response['duration'] = (job.end_time - job.start_time).total_seconds()
    
    if job.error:
        response['error'] = job.error
    
    if job.status == 'completed':
        response['output_files'] = {
            fmt: os.path.basename(path) 
            for fmt, path in job.output_files.items()
        }
        
        # Subject statistics
        subject_counts = {}
        for paper in job.results:
            subject = paper.get('classification', {}).get('primary_subject', 'Other')
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        response['subject_distribution'] = subject_counts
    
    return jsonify(response)


@app.route('/api/cancel/<job_id>', methods=['POST'])
def cancel_job(job_id):
    """Cancel a running job"""
    job = jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job.status in ['completed', 'failed', 'cancelled']:
        return jsonify({'error': 'Job already finished'}), 400
    
    # Mark job as cancelled
    job.status = 'cancelled'
    job.error = 'Cancelled by user'
    job.end_time = datetime.now()
    
    # Save cancelled job to history
    save_job_to_history(job)
    
    logger.info(f"Job {job_id} cancelled by user and saved to history")
    
    return jsonify({
        'success': True,
        'message': 'Job cancelled successfully'
    })


@app.route('/api/results/<job_id>')
def job_results(job_id):
    """Get detailed job results"""
    job = jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job.status != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    return jsonify({
        'job_id': job.job_id,
        'papers': job.results,
        'output_files': job.output_files
    })


@app.route('/api/download/<job_id>/<format>')
def download_file(job_id, format):
    """Download output file"""
    job = jobs.get(job_id)
    
    if not job or job.status != 'completed':
        return jsonify({'error': 'File not available'}), 404
    
    filepath = job.output_files.get(format)
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)


@app.route('/api/config')
def get_config():
    """Get system configuration"""
    return jsonify({
        'has_openai_key': bool(config.OPENAI_API_KEY),
        'subject_categories': config.SUBJECT_CATEGORIES,
        'max_concurrent': config.MAX_CONCURRENT_DOWNLOADS
    })


@app.route('/api/jobs')
def list_jobs():
    """List all jobs (current session)"""
    job_list = []
    for job_id, job in jobs.items():
        job_list.append({
            'job_id': job.job_id,
            'type': job.job_type,
            'status': job.status,
            'progress': job.progress,
            'total': job.total,
            'start_time': job.start_time.isoformat()
        })
    
    return jsonify({'jobs': job_list})


@app.route('/api/history')
def job_history():
    """Get all job history"""
    return jsonify({'jobs': get_all_job_history()})


@app.route('/api/history/<job_id>')
def get_history_job(job_id):
    """Get specific job from history"""
    # First check current jobs
    job = jobs.get(job_id)
    if not job:
        # Load from history
        job = load_job_from_history(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    response = {
        'job_id': job.job_id,
        'job_type': job.job_type,
        'status': job.status,
        'start_time': job.start_time.isoformat(),
        'end_time': job.end_time.isoformat() if job.end_time else None,
        'papers': job.results,
        'output_files': job.output_files,
        'error': job.error
    }
    
    # Subject statistics
    if job.results:
        subject_counts = {}
        for paper in job.results:
            subject = paper.get('classification', {}).get('primary_subject', 'Other')
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        response['subject_distribution'] = subject_counts
    
    return jsonify(response)


@app.route('/api/reclassify/<job_id>', methods=['POST'])
def reclassify_job(job_id):
    """Re-classify papers from a completed job"""
    global job_counter
    
    # Load the original job
    original_job = jobs.get(job_id)
    if not original_job:
        original_job = load_job_from_history(job_id)
    
    if not original_job:
        return jsonify({'error': 'Job not found'}), 404
    
    if not original_job.results:
        return jsonify({'error': 'No papers to re-classify'}), 400
    
    # Get parameters
    data = request.get_json() or {}
    output_format = data.get('format', 'all')
    
    # Create new job for re-classification
    job_counter += 1
    new_job_id = f"reclassify_{job_counter}"
    job = ProcessingJob(new_job_id, 'reclassify')
    jobs[new_job_id] = job
    
    # Start re-classification in background
    thread = threading.Thread(
        target=reclassify_background,
        args=(new_job_id, original_job.results, output_format)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': new_job_id,
        'message': f'Re-classifying {len(original_job.results)} papers'
    })


@app.route('/api/refetch/<job_id>', methods=['POST'])
def refetch_job(job_id):
    """Re-fetch and re-classify a crawl job"""
    global job_counter
    
    # Load original job
    original_job = load_job_from_history(job_id)
    if not original_job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Only crawl jobs can be re-fetched
    if original_job.job_type != 'crawl':
        return jsonify({'error': 'Only crawl jobs can be re-fetched'}), 400
    
    # Must have source URL
    if not original_job.source_url:
        return jsonify({'error': 'No source URL available for this job'}), 400
    
    data = request.get_json() or {}
    output_format = data.get('format', 'all')
    depth = int(data.get('depth', 2))
    use_js = data.get('use_js_rendering', False)
    
    # Create new job
    job_counter += 1
    new_job_id = f"refetch_{job_counter}"
    job = ProcessingJob(new_job_id, 'crawl', source_url=original_job.source_url)
    jobs[new_job_id] = job
    
    # Start crawling in background
    thread = threading.Thread(
        target=lambda: asyncio.run(crawl_website_background(new_job_id, original_job.source_url, depth, output_format, use_js))
    )
    thread.start()
    
    return jsonify({
        'job_id': new_job_id,
        'message': f'Re-fetching from {original_job.source_url}'
    })


def reclassify_background(job_id, papers, output_format='all'):
    """Background task to re-classify papers"""
    job = jobs[job_id]
    
    try:
        job.status = 'processing'
        job.total = len(papers)
        job.current_file = 'Re-classifying papers...'
        
        # Check if job was cancelled
        if job.status == 'cancelled':
            logger.info(f"Re-classification job {job_id} was cancelled")
            save_job_to_history(job)
            return
        
        # Re-classify papers with current classifier settings
        reclassified_papers = classifier.batch_classify(papers)
        job.results = reclassified_papers
        job.progress = len(papers)
        
        # Check if job was cancelled before catalog generation
        if job.status == 'cancelled':
            logger.info(f"Re-classification job {job_id} was cancelled before catalog generation")
            save_job_to_history(job)
            return
        
        # Generate new catalog
        job.current_file = 'Generating catalog...'
        output_files = catalog_generator.generate_catalog(reclassified_papers, format=output_format)
        job.output_files = output_files
        
        job.status = 'completed'
        job.end_time = datetime.now()
        save_job_to_history(job)
        
    except Exception as e:
        job.status = 'failed'
        job.error = str(e)
        job.end_time = datetime.now()
        save_job_to_history(job)
        logger.error(f"Re-classification job {job_id} failed: {e}", exc_info=True)


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    settings_file = 'settings.json'
    
    # Default settings
    default_settings = {
        'ai_provider': 'openai',
        'openai_api_key': config.OPENAI_API_KEY or '',
        'openai_model': 'gpt-3.5-turbo',
        'anthropic_api_key': '',
        'anthropic_model': 'claude-3-haiku-20240307',
        'use_keyword_fallback': True
    }
    
    # Load saved settings
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                saved_settings = json.load(f)
                default_settings.update(saved_settings)
        except:
            pass
    
    return jsonify(default_settings)


@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save settings"""
    try:
        settings = request.get_json()
        settings_file = 'settings.json'
        
        # Save to file
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        # Update config in memory
        if settings.get('openai_api_key'):
            config.OPENAI_API_KEY = settings['openai_api_key']
            os.environ['OPENAI_API_KEY'] = settings['openai_api_key']
        
        # Reinitialize classifier with new settings
        global classifier, pdf_extractor
        custom_categories = settings.get('custom_categories', None)
        classifier = AIClassifier(custom_categories=custom_categories)
        
        # Reinitialize PDF extractor with vision setting
        use_vision = settings.get('use_vision_extraction', True)
        pdf_extractor = PDFExtractor(use_vision=use_vision, api_key=settings.get('openai_api_key'))
        
        return jsonify({'success': True, 'message': 'Settings saved successfully'})
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/test-api', methods=['POST'])
def test_api():
    """Test API connection"""
    try:
        data = request.get_json()
        provider = data.get('provider', 'openai')
        api_key = data.get('api_key', '')
        
        if not api_key:
            return jsonify({'success': False, 'message': 'API key is required'})
        
        if provider == 'openai':
            import openai
            openai.api_key = api_key
            # Test with a simple completion
            response = openai.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': 'test'}],
                max_tokens=5
            )
            return jsonify({'success': True, 'message': 'OpenAI API connection successful'})
        
        elif provider == 'anthropic':
            # Placeholder for Anthropic testing
            return jsonify({'success': True, 'message': 'Anthropic API testing not yet implemented'})
        
        return jsonify({'success': False, 'message': 'Unknown provider'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    
    print("\n" + "="*60)
    print("🚀 CataBot Web Application Starting...")
    print("="*60)
    print(f"\n📍 Access the application at: http://{host}:{port}")
    print(f"📊 API endpoint: http://{host}:{port}/api")
    print(f"🔧 Mode: {'Development' if debug else 'Production'}")
    print(f"\n⚙️  OpenAI API: {'✅ Configured' if config.OPENAI_API_KEY else '⚠️  Not configured (using keyword matching)'}")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=debug, host=host, port=port, threaded=True)
