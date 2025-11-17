# Crawl Progress Display Fix

## Issue Fixed
**Problem:** During website crawling, the progress display didn't show the downloading phase properly. Users only saw "Crawling..." without knowing how many PDFs were being downloaded or the progress.

## Solution
Broke down the crawl process into distinct phases with detailed progress tracking:

### Phase 1: Scanning Website
```
Status: "Scanning website (depth: 2)..."
Progress: Indeterminate (searching for PDF links)
```

### Phase 2: Downloading PDFs
```
Status: "Downloading X PDFs..."
Progress: Y / X (updates as each PDF downloads)
Current File: "Downloaded: filename.pdf"
```

### Phase 3: Processing PDFs
```
Status: "Processing file.pdf"
Progress: Updates per file
(Existing behavior - already working)
```

## Implementation Details

### Before
```python
async def crawl_website_background(job_id, url, ...):
    job.current_file = f'Crawling {url}...'
    
    # Black box - no progress updates
    downloaded_files = await crawler.crawl_website(url, ...)
    
    # Then process files
    process_pdfs_background(job_id, pdf_files, ...)
```

### After
```python
async def crawl_website_background(job_id, url, ...):
    # Phase 1: Scanning
    job.current_file = f'Scanning website (depth: {max_depth})...'
    pdf_links = await crawler._find_pdf_links(url, max_depth)
    
    # Phase 2: Downloading with progress
    job.total = len(pdf_links)
    job.current_file = f'Downloading {len(pdf_links)} PDFs...'
    
    async def download_with_progress(pdf_url, output_dir):
        result = await crawler._download_pdf_with_semaphore(...)
        if result:
            job.progress += 1  # Update progress
            job.current_file = f'Downloaded: {filename}'
        return result
    
    tasks = [download_with_progress(url, 'pdfs') for url in pdf_links]
    await asyncio.gather(*tasks)
    
    # Phase 3: Processing (existing)
    process_pdfs_background(job_id, pdf_files, ...)
```

## Progress Updates

### Scanning Phase
- **Message**: "Scanning website (depth: X)..."
- **Progress**: 0 / 0 (indeterminate)
- **Duration**: Varies by website size and depth

### Download Phase
- **Message**: "Downloading X PDFs..."
- **Progress**: Updates from 0 to X
- **Current File**: Shows each downloaded file name
- **Duration**: Depends on number of PDFs and file sizes

### Processing Phase
- **Message**: Shows current PDF being processed
- **Progress**: Updates per file
- **Duration**: Depends on PDF complexity and AI processing

## User Experience

### Before
```
Status: "Crawling https://example.com..."
Progress: [████████████████████████████] 0 / 0
Files: 0 / 0
Papers: 0
Time: 45s

(User has no idea what's happening for 45 seconds)
```

### After
```
Status: "Scanning website (depth: 2)..."
Progress: [░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0 / 0
Files: 0 / 0
Papers: 0
Time: 5s

↓

Status: "Downloading 25 PDFs..."
Progress: [████████░░░░░░░░░░░░░░░░░░░░] 8 / 25
Files: 8 / 25
Papers: 0
Time: 20s
Current: "Downloaded: paper-2024.pdf"

↓

Status: "Processing paper-2024.pdf"
Progress: [████████████████░░░░░░░░░░░░] 15 / 25
Files: 15 / 25
Papers: 12
Time: 45s
```

## Cancellation Support

Added cancellation checks at each phase:

1. **After scanning**: Check before starting downloads
2. **During downloads**: Check before each download
3. **After downloads**: Check before processing

```python
# After scanning
if job.status == 'cancelled':
    save_job_to_history(job)
    return

# During downloads
async def download_with_progress(pdf_url, output_dir):
    if job.status == 'cancelled':
        return None
    # ... download

# After downloads
if job.status == 'cancelled':
    save_job_to_history(job)
    return
```

## Benefits

1. **Transparency**: Users see exactly what's happening
2. **Accurate Progress**: Real-time updates during downloads
3. **Better UX**: No more long "Crawling..." with no feedback
4. **Cancellable**: Can cancel during any phase
5. **Informative**: Shows how many PDFs found and downloaded

## Technical Notes

### Concurrent Downloads
- Uses `asyncio.Semaphore` to limit concurrent downloads
- Default: 5 concurrent downloads
- Progress updates are thread-safe (single job object)

### Progress Calculation
```python
# Download phase
job.total = len(pdf_links)      # Total PDFs to download
job.progress = 0                 # Start at 0
# Each successful download increments progress
job.progress += 1

# Processing phase (resets)
job.total = len(pdf_files)       # Total files to process
job.progress = 0                 # Reset to 0
# Each processed file increments progress
```

### Error Handling
- Failed downloads don't stop the process
- Only successful downloads increment progress
- Final check ensures at least some PDFs downloaded

## Testing

### Test Crawl Progress
1. Start crawl job on a site with many PDFs
2. Observe progress display:
   - "Scanning website..." appears first
   - "Downloading X PDFs..." appears with progress bar
   - Each download updates the counter
   - Current file name updates
3. Verify all phases show proper progress

### Test Cancellation
1. Start crawl job
2. Cancel during scanning phase
3. Cancel during download phase
4. Verify job stops and saves to history

## Future Enhancements

Possible improvements:
- Show download speed (MB/s)
- Show estimated time remaining
- Parallel scanning and downloading
- Resume failed downloads
- Download size progress (bytes downloaded)
