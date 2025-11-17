# Job History and Re-classification Feature

## Overview
Added comprehensive job history tracking and re-classification capabilities to CataBot.

## New Features

### 1. **Persistent Job Storage**
- All completed jobs are automatically saved to `job_history/` directory
- Jobs persist across application restarts
- Each job stored as JSON with full metadata and results

### 2. **Job History Tab**
- New "📜 Job History" tab in the UI
- View all past processing jobs with:
  - Job type (Upload, Crawl, Directory, Re-classify)
  - Status (Completed/Failed)
  - Start time and duration
  - Number of papers processed
  - Error messages (if failed)

### 3. **View Job Details**
- Click "👁️ View Details" on any job to see:
  - Subject distribution chart
  - Download links for all output files
  - Preview of first 10 papers with metadata
  - Full classification results

### 4. **Re-classification**
- Click "🔄 Re-classify" on completed jobs to:
  - Re-run classification with current AI settings
  - Use updated custom categories
  - Generate new output files
  - Useful when you change AI models or categories

## Backend Changes

### New API Endpoints

#### `GET /api/history`
Returns list of all jobs from history
```json
{
  "jobs": [
    {
      "job_id": "job_1",
      "job_type": "upload",
      "status": "completed",
      "start_time": "2024-01-01T12:00:00",
      "end_time": "2024-01-01T12:05:00",
      "results_count": 25,
      "error": null
    }
  ]
}
```

#### `GET /api/history/<job_id>`
Returns full details of a specific job including papers and classifications

#### `POST /api/reclassify/<job_id>`
Re-classifies papers from a completed job
```json
{
  "format": "all"  // Optional: output format
}
```

### New Functions

- `save_job_to_history(job)` - Saves completed job to persistent storage
- `load_job_from_history(job_id)` - Loads job from storage
- `get_all_job_history()` - Returns all jobs sorted by date
- `reclassify_background(job_id, papers, output_format)` - Background task for re-classification

### ProcessingJob Class Updates

Added serialization methods:
- `to_dict()` - Convert job to dictionary for JSON storage
- `from_dict(data)` - Create job instance from dictionary

## Frontend Changes

### New UI Components

**History Tab** (`#history-tab`)
- Job list with cards showing status and metadata
- Expandable details section
- Action buttons for viewing and re-classifying

**CSS Classes**
- `.history-list` - Container for job cards
- `.history-item` - Individual job card
- `.history-header` - Job title and status badge
- `.history-status` - Status badge (completed/failed)
- `.history-actions` - Action button container
- `.job-details` - Expandable details section
- `.papers-table` - Table for displaying paper metadata

### New JavaScript Functions

- `loadJobHistory()` - Fetches and displays job history
- `createHistoryItem(job)` - Creates HTML for job card
- `viewJobDetails(jobId)` - Loads and displays job details
- `displayJobDetails(container, data)` - Renders job details
- `reclassifyJob(jobId)` - Initiates re-classification

## Usage

### Viewing History
1. Click on "📜 Job History" tab
2. Browse through past jobs
3. Click "👁️ View Details" to see full information

### Re-classifying Papers
1. Go to Job History tab
2. Find the job you want to re-classify
3. (Optional) Update AI settings or custom categories in Settings tab
4. Click "🔄 Re-classify" button
5. Confirm the action
6. Monitor progress in the progress view
7. Download new output files when complete

## Use Cases

### 1. **Changing Classification Categories**
- Process papers with default categories
- Define custom categories in Settings
- Re-classify existing jobs with new categories
- Compare results

### 2. **Upgrading AI Model**
- Initial processing with GPT-3.5 Turbo (fast/cheap)
- Review results
- Re-classify with GPT-4 for better accuracy
- No need to re-upload or re-crawl

### 3. **Batch Re-processing**
- Process multiple batches over time
- Later decide to standardize all with same settings
- Re-classify all past jobs with consistent settings

### 4. **Error Recovery**
- Job fails due to API issues
- Fix API configuration
- Re-run classification without re-extracting PDFs

## File Structure

```
CataBot/
├── job_history/           # New directory for persistent storage
│   ├── job_1.json        # Individual job files
│   ├── crawl_2.json
│   └── reclassify_3.json
├── app.py                 # Updated with history endpoints
└── templates/
    └── index.html         # Updated with history tab
```

## Technical Notes

- Jobs are saved automatically when status changes to 'completed'
- Job history is loaded on-demand when switching to History tab
- Re-classification creates a new job (doesn't overwrite original)
- All original output files remain accessible
- Job IDs are unique and sequential within session
- History persists across server restarts

## Future Enhancements

Possible improvements:
- Delete old jobs from history
- Export/import job history
- Search and filter jobs
- Bulk re-classification
- Job comparison view
- Statistics dashboard
