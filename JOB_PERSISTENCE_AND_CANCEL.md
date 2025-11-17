# Job Persistence and Cancellation Feature

## Overview
Added job persistence across page refreshes and tab switches, plus the ability to cancel running jobs.

## New Features

### 1. **Job Persistence**
Jobs now persist across:
- Page refreshes (F5)
- Browser tab switches
- Accidental navigation away
- Browser crashes (when reopened)

**How it works:**
- Current job ID stored in `localStorage`
- On page load, checks for ongoing job
- Automatically resumes progress monitoring
- Clears storage when job completes/fails

### 2. **Cancel Job Button**
- Red "✕ Cancel Job" button in progress view
- Confirmation dialog before cancelling
- Immediately stops job processing
- Updates job status to 'cancelled'
- Clears localStorage and resets UI

## Technical Implementation

### Frontend Changes

**localStorage Keys:**
- `catabot_current_job`: Stores current job ID

**New Functions:**
- `checkJobStatus()`: Checks if saved job is still running on page load
- `cancelJob()`: Sends cancel request to backend

**Modified Functions:**
- `uploadFiles()`, `startCrawl()`, `processDirectory()`, `reclassifyJob()`: Save job ID to localStorage
- `checkStatus()`: Clear localStorage when job completes/fails/cancelled
- `resetForm()`: Clear localStorage when resetting

**Page Load Handler:**
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const savedJobId = localStorage.getItem('catabot_current_job');
    if (savedJobId) {
        currentJobId = savedJobId;
        checkJobStatus();
    }
});
```

### Backend Changes

**New Endpoint:**
```
POST /api/cancel/<job_id>
```

**Response:**
```json
{
  "success": true,
  "message": "Job cancelled successfully"
}
```

**Job Status:**
- Added 'cancelled' status to job states
- Job marked as cancelled with error message
- End time recorded for cancelled jobs

## User Experience

### Before
- Refreshing page lost all progress
- No way to stop a running job
- Had to wait for job to complete or restart server

### After
- **Seamless continuity** - refresh page and progress continues
- **Cancel anytime** - stop unwanted jobs immediately
- **Automatic recovery** - browser crash? Job resumes when you return
- **Clear feedback** - log shows cancellation

## Usage

### Job Persistence
1. Start any processing job
2. Refresh the page (F5) or close/reopen tab
3. Progress automatically resumes
4. All metrics and logs restored

### Cancelling Jobs
1. While job is running, click "✕ Cancel Job"
2. Confirm cancellation in dialog
3. Job stops immediately
4. Status shows as cancelled in history

## Edge Cases Handled

1. **Job completed while away**: Shows results when returning
2. **Job failed while away**: Shows error message
3. **Job not found**: Clears localStorage silently
4. **Multiple tabs**: Each tab can monitor same job
5. **Cancel already finished job**: Returns error message

## Benefits

1. **Reliability**: No lost progress from accidental refreshes
2. **Control**: Can stop long-running jobs
3. **Flexibility**: Switch tabs/windows without worry
4. **Professional**: Matches behavior of modern web apps
5. **User-friendly**: Automatic recovery without user action

## Implementation Details

### localStorage Flow
```
Start Job → Save ID → Monitor Progress
                ↓
         Page Refresh
                ↓
    Load ID → Check Status → Resume Monitoring
                ↓
         Job Completes
                ↓
         Clear Storage
```

### Cancel Flow
```
User Clicks Cancel → Confirm Dialog
                ↓
         POST /api/cancel
                ↓
    Backend Marks Cancelled
                ↓
    Frontend Clears Storage
                ↓
         Reset UI
```

## Security Considerations

- Job IDs stored in localStorage (client-side only)
- No sensitive data stored
- Job IDs are session-specific
- Backend validates job ownership (same session)

## Future Enhancements

Possible improvements:
- Pause/resume functionality
- Job queue management
- Multiple concurrent jobs
- Job priority settings
- Scheduled job execution
- Job templates/presets
