# Download Phase Cancellation Fix

## Issue Fixed

**Problem:** When cancelling a crawl job during the download phase, the job status changed to "cancelled" but downloads continued running in the background.

**Example:**
```
User clicks "Cancel Job"
    ↓
Job status = 'cancelled'
    ↓
But downloads keep going...
INFO: Downloaded: file1.pdf
INFO: Downloaded: file2.pdf
INFO: Downloaded: file3.pdf
... (continues for all remaining files)
```

## Root Cause

The original implementation downloaded all PDFs in one large batch:
```python
tasks = [download_with_progress(pdf_url, 'pdfs') for pdf_url in pdf_links]
await asyncio.gather(*tasks)  # All tasks run to completion
```

Once `asyncio.gather()` starts, it runs all tasks to completion. The cancellation check only happened:
- Before starting the first download
- Inside each download function (but download already started)

## Solution

### Batch Processing
Download PDFs in smaller batches with cancellation checks between batches:

```python
# Download in batches of 10
batch_size = 10
for i in range(0, len(pdf_links), batch_size):
    # Check if cancelled before each batch
    if job.status == 'cancelled':
        logger.info(f"Job cancelled during batch {i//batch_size + 1}")
        save_job_to_history(job)
        return
    
    # Download this batch
    batch = pdf_links[i:i+batch_size]
    tasks = [download_with_progress(url, 'pdfs') for url in batch]
    await asyncio.gather(*tasks)
```

### Multiple Cancellation Checks

**1. Before each batch (every 10 files):**
```python
if job.status == 'cancelled':
    logger.info(f"Cancelled during download batch {i//batch_size + 1}")
    save_job_to_history(job)
    return
```

**2. Before each individual download:**
```python
async def download_with_progress(pdf_url, output_dir):
    if job.status == 'cancelled':
        return None
    result = await crawler._download_pdf_with_semaphore(...)
```

**3. After each individual download:**
```python
async def download_with_progress(pdf_url, output_dir):
    result = await crawler._download_pdf_with_semaphore(...)
    if job.status == 'cancelled':
        return None
    # Update progress...
```

**4. After all batches complete:**
```python
if job.status == 'cancelled':
    logger.info(f"Cancelled during download")
    save_job_to_history(job)
    return
```

## How It Works Now

### Cancellation Flow:

```
User clicks "Cancel Job"
    ↓
Backend: job.status = 'cancelled'
    ↓
Current batch finishes (max 10 files)
    ↓
Check before next batch: status == 'cancelled'
    ↓
Stop immediately, save to history
    ↓
No more downloads!
```

### Timeline Example:

```
Downloading 100 PDFs...

Batch 1 (files 1-10): ████████████ ✓
Batch 2 (files 11-20): ████████████ ✓
Batch 3 (files 21-30): ████████████ ✓
[User clicks Cancel]
Batch 4 (files 31-40): ████████░░░░ (in progress, finishes)
Check: status == 'cancelled' → STOP
Batch 5-10: Not started ✗

Result: Stopped after ~40 files instead of all 100
```

## Benefits

### 1. **Responsive Cancellation**
- Stops within 10 downloads (or less)
- Much faster than waiting for all downloads
- User sees immediate effect

### 2. **Resource Efficient**
- No wasted bandwidth
- No unnecessary disk writes
- Frees up system resources quickly

### 3. **Clean State**
- Properly saves partial results
- Job marked as cancelled in history
- No orphaned background tasks

### 4. **Graceful Handling**
- Completes current batch
- Doesn't interrupt mid-download
- No corrupted files

## Performance Impact

### Before:
- **Cancellation time**: Wait for all downloads (could be minutes)
- **Wasted resources**: All remaining downloads complete
- **User experience**: Frustrating, seems broken

### After:
- **Cancellation time**: ~10 downloads (seconds)
- **Wasted resources**: Minimal (only current batch)
- **User experience**: Responsive, works as expected

## Batch Size Considerations

### Current: `batch_size = 10`

**Pros:**
- Quick cancellation response
- Frequent checks
- Good balance

**Cons:**
- Slightly more overhead from checks

### Alternative Sizes:

**`batch_size = 5`:**
- Even faster cancellation
- More overhead
- Better for slow downloads

**`batch_size = 20`:**
- Less overhead
- Slower cancellation
- Better for fast downloads

**`batch_size = 1`:**
- Instant cancellation
- Maximum overhead
- Not recommended

## Concurrent Downloads

The batch system works with concurrent downloads:

```python
semaphore = asyncio.Semaphore(5)  # 5 concurrent downloads

# Batch of 10 files
# Downloads 5 at a time (2 waves)
# Checks cancellation between batches
```

**Example with 100 files:**
- Batch 1: Files 1-10 (2 waves of 5)
- Check cancellation
- Batch 2: Files 11-20 (2 waves of 5)
- Check cancellation
- ... and so on

## Edge Cases Handled

### 1. **Cancel During First Batch**
```python
# Check before batch 1
if job.status == 'cancelled':
    return  # Stops immediately
```

### 2. **Cancel During Last Batch**
```python
# After all batches
if job.status == 'cancelled':
    save_job_to_history(job)
    return
```

### 3. **Cancel Between Downloads in Batch**
```python
# Check after each download
if job.status == 'cancelled':
    return None  # Skip rest of batch
```

### 4. **Multiple Rapid Cancels**
- Idempotent: Safe to call multiple times
- Status already 'cancelled'
- Checks pass through quickly

## Logging

### Successful Cancellation:
```
INFO: Job crawl_1 cancelled by user and saved to history
INFO: Crawl job crawl_1 was cancelled during download batch 4
```

### Partial Downloads:
```
INFO: Successfully downloaded 35 PDFs
INFO: Crawl job crawl_1 was cancelled during download
```

## Testing

### Test Cancellation During Download:
1. Start crawl job with many PDFs (50+)
2. Wait for download phase to start
3. Click "Cancel Job"
4. Observe:
   - Current batch finishes
   - No more downloads start
   - Job saved to history
   - Status shows cancelled

### Verify Batch Processing:
1. Check logs for batch messages
2. Count downloads after cancel
3. Should be ≤ batch_size more than when cancelled

### Test Edge Cases:
1. Cancel before first download
2. Cancel during last batch
3. Cancel multiple times rapidly
4. Cancel then refresh page

## Comparison: Before vs After

### Before:
```
100 PDFs to download
User cancels after 30
Downloads continue: 31, 32, 33, ... 100
Total: 100 downloads (70 wasted)
Time: Full duration
```

### After:
```
100 PDFs to download
User cancels after 30
Current batch finishes: 31-40
Stops at 40
Total: 40 downloads (10 wasted)
Time: Reduced by 60%
```

## Future Enhancements

Possible improvements:
1. **Configurable batch size** - Let users choose responsiveness vs overhead
2. **Task cancellation** - Use `asyncio.Task.cancel()` for instant stop
3. **Progress persistence** - Resume downloads from where stopped
4. **Partial results** - Process downloaded files even if cancelled
5. **Download queue** - Better control over concurrent downloads

## Related Features

This fix complements:
- **Job cancellation** - Cancel button in UI
- **Job persistence** - Cancelled jobs saved to history
- **Progress display** - Shows download progress
- **Re-fetch feature** - Can re-fetch cancelled jobs

## Summary

The download phase now respects cancellation requests by:
- Processing downloads in batches of 10
- Checking cancellation status between batches
- Stopping quickly (within ~10 downloads)
- Saving partial results to history
- Providing responsive user experience

Users can now effectively cancel crawl jobs during the download phase! ⏹️
