# Job Cancellation Fix

## Issues Fixed

### 1. Backend Continues Processing After Cancellation
**Problem:** When user clicked "Cancel Job", the frontend stopped monitoring but the backend thread continued processing PDFs.

**Solution:** Added cancellation checks at multiple points in background tasks:
- Before processing each PDF file
- Before classification phase
- Before catalog generation

### 2. Cancelled Jobs Not Saved to History
**Problem:** Cancelled jobs disappeared and weren't visible in job history.

**Solution:** 
- Save job to history when cancellation is detected
- Save job to history when cancel endpoint is called
- Also fixed: Failed jobs now saved to history too

## Implementation Details

### Cancellation Check Points

**In `process_pdfs_background()`:**
```python
# Check 1: Before processing each file
for i, pdf_path in enumerate(pdf_files):
    if job.status == 'cancelled':
        logger.info(f"Job {job_id} was cancelled, stopping processing")
        save_job_to_history(job)
        return
    # ... process file

# Check 2: Before classification
if job.status == 'cancelled':
    logger.info(f"Job {job_id} was cancelled before classification")
    save_job_to_history(job)
    return

# Check 3: Before catalog generation
if job.status == 'cancelled':
    logger.info(f"Job {job_id} was cancelled before catalog generation")
    save_job_to_history(job)
    return
```

**In `reclassify_background()`:**
```python
# Check 1: Before re-classification
if job.status == 'cancelled':
    save_job_to_history(job)
    return

# Check 2: Before catalog generation
if job.status == 'cancelled':
    save_job_to_history(job)
    return
```

**In `cancel_job()` endpoint:**
```python
# Mark as cancelled and save immediately
job.status = 'cancelled'
job.error = 'Cancelled by user'
job.end_time = datetime.now()
save_job_to_history(job)  # <-- Added this
```

### Save on All Termination Paths

**Completed:**
```python
job.status = 'completed'
job.end_time = datetime.now()
save_job_to_history(job)  # Already existed
```

**Failed:**
```python
except Exception as e:
    job.status = 'failed'
    job.error = str(e)
    job.end_time = datetime.now()
    save_job_to_history(job)  # <-- Added this
```

**Cancelled:**
```python
if job.status == 'cancelled':
    save_job_to_history(job)  # <-- Added this
    return
```

## How It Works

### Cancellation Flow
```
User clicks "Cancel Job"
        ↓
Frontend calls POST /api/cancel/<job_id>
        ↓
Backend sets job.status = 'cancelled'
        ↓
Backend saves to history immediately
        ↓
Background thread checks status
        ↓
Finds status == 'cancelled'
        ↓
Stops processing and returns
        ↓
Job saved to history (if not already)
```

### Check Frequency
- **File processing loop**: Checked before each file (every few seconds)
- **Between phases**: Checked before classification and catalog generation
- **Immediate**: Cancel endpoint saves immediately

## Benefits

### 1. **Responsive Cancellation**
- Stops within seconds (after current file completes)
- No wasted processing time
- Frees up system resources

### 2. **Complete History**
- All jobs visible in history (completed, failed, cancelled)
- Can see what was cancelled and when
- Useful for debugging and tracking

### 3. **Clean State**
- No orphaned background threads
- Proper cleanup on all exit paths
- Consistent behavior

### 4. **User Feedback**
- Clear indication in history that job was cancelled
- Shows how much was processed before cancellation
- Papers extracted before cancellation are saved

## Testing

### Test Cancellation
1. Start a large job (many PDFs)
2. Click "Cancel Job" after a few seconds
3. Verify:
   - Processing stops quickly
   - Job appears in history with "cancelled" status
   - Papers processed before cancellation are saved

### Test History
1. Check job history tab
2. Verify cancelled jobs appear with:
   - Status: cancelled
   - Error: "Cancelled by user"
   - Partial results (if any)
   - Correct timestamps

## Edge Cases Handled

1. **Cancel during file processing**: Stops after current file
2. **Cancel during classification**: Stops before classification starts
3. **Cancel during catalog generation**: Stops before generation starts
4. **Multiple cancels**: Idempotent - safe to call multiple times
5. **Already finished**: Returns error if job already completed/failed

## Performance Impact

- **Minimal overhead**: Simple status check (microseconds)
- **No polling**: Uses existing job object
- **Efficient**: Stops at natural breakpoints
- **Resource-friendly**: Immediate cleanup

## Future Enhancements

Possible improvements:
- Cancel during classification (requires AI client support)
- Cancel during vision extraction (requires OpenAI client support)
- Partial results download for cancelled jobs
- Resume cancelled jobs
- Batch cancel multiple jobs
