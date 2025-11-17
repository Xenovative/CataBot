# Re-fetch & Re-classify Feature

## Overview
Added the ability to re-fetch papers from the original URL and re-classify them, allowing users to get updated content from websites without manually re-entering the URL.

## Use Cases

### 1. **Get Latest Papers**
- Website has new papers since last crawl
- Re-fetch to get updated content
- Automatically classify new papers

### 2. **Improved Extraction**
- First crawl had incomplete metadata
- HTML metadata extraction now improved
- Re-fetch to get better results

### 3. **Different Settings**
- Want to use different crawl depth
- Want to enable/disable JS rendering
- Re-fetch with new settings

### 4. **Fix Failed Crawls**
- Previous crawl failed or was incomplete
- Re-fetch to try again
- Uses same URL automatically

## Implementation

### Backend Changes (app.py)

**1. Added `source_url` to ProcessingJob:**
```python
class ProcessingJob:
    def __init__(self, job_id, job_type, source_url=None):
        # ... existing fields
        self.source_url = source_url  # Store original URL
```

**2. Store URL in crawl jobs:**
```python
@app.route('/api/crawl', methods=['POST'])
def crawl_website():
    job = ProcessingJob(job_id, 'crawl', source_url=url)
```

**3. New `/api/refetch/<job_id>` endpoint:**
```python
@app.route('/api/refetch/<job_id>', methods=['POST'])
def refetch_job(job_id):
    # Load original job
    original_job = load_job_from_history(job_id)
    
    # Validate: must be crawl job with source URL
    if original_job.job_type != 'crawl':
        return error
    if not original_job.source_url:
        return error
    
    # Create new crawl job with same URL
    new_job = ProcessingJob(new_job_id, 'crawl', source_url=original_job.source_url)
    
    # Start crawling
    asyncio.run(crawl_website_background(...))
```

**4. Persist source_url:**
```python
def to_dict(self):
    return {
        # ... existing fields
        'source_url': self.source_url
    }

def from_dict(data):
    job = ProcessingJob(data['job_id'], data['job_type'], data.get('source_url'))
```

### Frontend Changes (index.html)

**1. Show re-fetch button for crawl jobs:**
```javascript
${job.job_type === 'crawl' && job.source_url ? `
    <button onclick="refetchJob('${job.job_id}')">
        🔃 Re-fetch & Re-classify
    </button>
` : ''}
```

**2. Re-fetch function:**
```javascript
async function refetchJob(jobId) {
    if (!confirm('Re-fetch papers from the original URL?')) return;
    
    const response = await fetch(`/api/refetch/${jobId}`, {
        method: 'POST',
        body: JSON.stringify({
            format: 'all',
            depth: 2,
            use_js_rendering: false
        })
    });
    
    // Switch to upload tab and show progress
    currentJobId = data.job_id;
    switchTab('upload');
    showProgress();
    startStatusCheck();
}
```

### Translations (i18n.js)

**English:**
- `history_refetch`: "Re-fetch & Re-classify"
- `msg_refetch_confirm`: "Re-fetch papers from the original URL and re-classify them? This will create a new job."
- `msg_refetch_started`: "Re-fetch started! Job ID:"

**Traditional Chinese:**
- `history_refetch`: "重新抓取並分類"
- `msg_refetch_confirm`: "從原始網址重新抓取論文並重新分類？這將建立一個新工作。"
- `msg_refetch_started`: "重新抓取已開始！工作 ID："

## User Experience

### Before
```
Job History
┌─────────────────────────────────┐
│ 🌐 Crawl Job                    │
│ Status: ✓ Completed             │
│ Papers: 25                      │
│                                 │
│ [View Details] [Re-classify]   │
└─────────────────────────────────┘

To get updated papers:
1. Go to Crawl tab
2. Re-enter URL manually
3. Configure settings again
4. Start new crawl
```

### After
```
Job History
┌─────────────────────────────────┐
│ 🌐 Crawl Job                    │
│ Status: ✓ Completed             │
│ Papers: 25                      │
│                                 │
│ [View Details] [Re-classify]   │
│ [🔃 Re-fetch & Re-classify]    │ ← NEW
└─────────────────────────────────┘

To get updated papers:
1. Click "Re-fetch & Re-classify"
2. Confirm
3. Done! Automatically crawls same URL
```

## Button Visibility Logic

### Re-fetch button shows when:
- ✅ Job type is 'crawl'
- ✅ Job has `source_url` stored
- ✅ Any status (completed, failed, cancelled)

### Re-classify button shows when:
- ✅ Job status is 'completed'
- ✅ Job has results (papers found)
- ✅ Any job type

### Examples:

**Crawl job (completed, has URL):**
- [View Details] [Re-classify] [Re-fetch & Re-classify]

**Crawl job (failed, has URL):**
- [View Details] [Re-fetch & Re-classify]

**Upload job (completed):**
- [View Details] [Re-classify]

**Old crawl job (no URL stored):**
- [View Details] [Re-classify]

## Technical Details

### Source URL Storage
```python
# When crawling
job = ProcessingJob(job_id, 'crawl', source_url='https://example.com')

# Saved to job_history/crawl_1.json
{
    "job_id": "crawl_1",
    "job_type": "crawl",
    "source_url": "https://example.com",
    ...
}

# Loaded from history
job = load_job_from_history('crawl_1')
job.source_url  # 'https://example.com'
```

### Re-fetch Flow
```
User clicks "Re-fetch & Re-classify"
        ↓
Frontend: confirm dialog
        ↓
POST /api/refetch/crawl_1
        ↓
Backend: Load original job
        ↓
Backend: Validate (crawl job + has URL)
        ↓
Backend: Create new job with same URL
        ↓
Backend: Start crawl_website_background
        ↓
Frontend: Switch to upload tab
        ↓
Frontend: Show progress
        ↓
User sees real-time progress
```

### Job ID Format
- Original: `crawl_1`
- Re-fetch: `refetch_2`
- Both stored in history independently

### Settings
Re-fetch uses default settings:
- Format: 'all'
- Depth: 2
- JS rendering: false

Future enhancement: Allow customizing these settings in UI.

## Benefits

### 1. **Convenience**
- No need to remember/re-enter URL
- One-click operation
- Automatic configuration

### 2. **Consistency**
- Same URL guaranteed
- No typos or mistakes
- Reliable re-crawling

### 3. **Efficiency**
- Faster than manual re-entry
- Less prone to errors
- Better user experience

### 4. **Flexibility**
- Can re-fetch any old crawl job
- Works with failed jobs too
- Independent from original job

## Comparison: Re-fetch vs Re-classify

### Re-classify
- **What**: Re-classify existing papers
- **When**: Papers already extracted, want different classification
- **Use**: Changed AI settings, want better categories
- **Speed**: Fast (no download/extraction)
- **Data**: Uses cached papers

### Re-fetch
- **What**: Re-crawl URL and re-classify
- **When**: Want updated/new papers from website
- **Use**: Website has new content, want fresh data
- **Speed**: Slow (full crawl + extraction)
- **Data**: Fresh from website

## Error Handling

### Validation Errors:

**Job not found:**
```json
{
    "error": "Job not found"
}
```

**Not a crawl job:**
```json
{
    "error": "Only crawl jobs can be re-fetched"
}
```

**No source URL:**
```json
{
    "error": "No source URL available for this job"
}
```

### User Messages:
- Clear error messages
- Confirmation before starting
- Success notification with job ID
- Automatic progress display

## Future Enhancements

Possible improvements:
1. **Customizable settings in UI**
   - Depth slider
   - JS rendering toggle
   - Format selector

2. **Compare results**
   - Show diff between old and new
   - Highlight new papers
   - Show removed papers

3. **Scheduled re-fetch**
   - Automatic periodic re-crawling
   - Email notifications
   - Cron-like scheduling

4. **Incremental fetch**
   - Only fetch new papers
   - Skip already-processed PDFs
   - Faster updates

5. **Batch re-fetch**
   - Re-fetch multiple jobs at once
   - Queue management
   - Progress for all jobs

## Testing

### Test Re-fetch:
1. Complete a crawl job
2. Go to History tab
3. Find the crawl job
4. Click "Re-fetch & Re-classify"
5. Confirm dialog
6. Verify:
   - New job created
   - Progress shown
   - Same URL used
   - Papers extracted

### Test Validation:
1. Try re-fetch on upload job → Error
2. Try re-fetch on old job without URL → Error
3. Try re-fetch on non-existent job → Error

### Test UI:
1. Crawl jobs show re-fetch button
2. Upload jobs don't show re-fetch button
3. Button has correct translation
4. Confirmation dialog appears
