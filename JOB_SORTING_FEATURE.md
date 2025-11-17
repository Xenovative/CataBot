# Job History Sorting Feature

## Overview
Added comprehensive sorting options for the job history, allowing users to organize and find jobs based on different criteria.

## Sorting Options

### 1. **Date (Newest First)** - Default
- Sorts jobs by start time, newest first
- Most recent jobs appear at the top
- Best for finding recent work

### 2. **Date (Oldest First)**
- Sorts jobs by start time, oldest first
- Historical jobs appear at the top
- Useful for reviewing early work

### 3. **Status**
- Groups jobs by completion status
- Order: Completed → Failed → Cancelled
- Within each group, sorted by date (newest first)
- Quickly see all successful jobs

### 4. **Papers (Most First)**
- Sorts by number of papers found
- Jobs with most papers appear first
- Useful for finding large datasets

### 5. **Papers (Least First)**
- Sorts by number of papers found
- Jobs with fewest papers appear first
- Useful for finding incomplete or small jobs

### 6. **Job Type**
- Groups by job type (crawl, directory, reclassify, upload)
- Alphabetically ordered types
- Within each type, sorted by date (newest first)
- Useful for finding specific operation types

## Implementation

### Frontend Changes

**HTML (index.html):**
```html
<div class="input-group">
    <label data-i18n="history_sort_label">Sort by:</label>
    <select id="historySortBy" onchange="sortJobHistory()">
        <option value="date_desc">Date (Newest First)</option>
        <option value="date_asc">Date (Oldest First)</option>
        <option value="status">Status</option>
        <option value="papers_desc">Papers (Most First)</option>
        <option value="papers_asc">Papers (Least First)</option>
        <option value="type">Job Type</option>
    </select>
</div>
```

**JavaScript:**
```javascript
let allJobs = []; // Store all jobs for sorting

async function loadJobHistory() {
    // Fetch jobs from API
    allJobs = data.jobs;
    sortJobHistory(); // Apply current sort
}

function sortJobHistory() {
    const sortBy = document.getElementById('historySortBy').value;
    let sortedJobs = [...allJobs];
    
    switch(sortBy) {
        case 'date_desc':
            sortedJobs.sort((a, b) => 
                new Date(b.start_time) - new Date(a.start_time));
            break;
        case 'date_asc':
            sortedJobs.sort((a, b) => 
                new Date(a.start_time) - new Date(b.start_time));
            break;
        case 'status':
            // Group by status, then by date
            const statusOrder = { 'completed': 0, 'failed': 1, 'cancelled': 2 };
            sortedJobs.sort((a, b) => {
                const orderDiff = statusOrder[a.status] - statusOrder[b.status];
                if (orderDiff !== 0) return orderDiff;
                return new Date(b.start_time) - new Date(a.start_time);
            });
            break;
        case 'papers_desc':
            sortedJobs.sort((a, b) => 
                (b.results_count || 0) - (a.results_count || 0));
            break;
        case 'papers_asc':
            sortedJobs.sort((a, b) => 
                (a.results_count || 0) - (b.results_count || 0));
            break;
        case 'type':
            // Group by type, then by date
            sortedJobs.sort((a, b) => {
                const typeDiff = a.job_type.localeCompare(b.job_type);
                if (typeDiff !== 0) return typeDiff;
                return new Date(b.start_time) - new Date(a.start_time);
            });
            break;
    }
    
    historyList.innerHTML = sortedJobs.map(job => createHistoryItem(job)).join('');
}
```

**CSS Enhancement:**
```css
.history-status.cancelled {
    background: #fff3e0;
    color: #f57c00;
}
```

### Translations (i18n.js)

**English:**
- `history_sort_label`: "Sort by:"
- `history_sort_date_desc`: "Date (Newest First)"
- `history_sort_date_asc`: "Date (Oldest First)"
- `history_sort_status`: "Status"
- `history_sort_papers_desc`: "Papers (Most First)"
- `history_sort_papers_asc`: "Papers (Least First)"
- `history_sort_type`: "Job Type"

**Traditional Chinese:**
- `history_sort_label`: "排序方式："
- `history_sort_date_desc`: "日期（最新優先）"
- `history_sort_date_asc`: "日期（最舊優先）"
- `history_sort_status`: "狀態"
- `history_sort_papers_desc`: "論文數（最多優先）"
- `history_sort_papers_asc`: "論文數（最少優先）"
- `history_sort_type`: "工作類型"

## User Experience

### Before
```
Job History
[🔄 Refresh]

Jobs displayed in random/insertion order
No way to organize or find specific jobs
```

### After
```
Job History
[Sort by: Date (Newest First) ▼] [🔄 Refresh]

Jobs organized by selected criteria
Instant re-sorting without reloading
Easy to find specific jobs
```

## Use Cases

### 1. Find Recent Work
**Sort by:** Date (Newest First)
- Default view
- See what you worked on recently
- Quick access to latest results

### 2. Review All Successful Jobs
**Sort by:** Status
- All completed jobs grouped together
- See success rate at a glance
- Ignore failed/cancelled jobs

### 3. Find Large Datasets
**Sort by:** Papers (Most First)
- Identify most productive jobs
- Find comprehensive collections
- Prioritize large catalogs

### 4. Find Specific Operation
**Sort by:** Job Type
- Group all crawl jobs together
- Find all reclassification jobs
- Organize by operation type

### 5. Historical Review
**Sort by:** Date (Oldest First)
- Review early experiments
- See how usage evolved
- Find original datasets

## Technical Details

### Sorting Algorithm
- **Client-side sorting**: Fast, no server requests
- **Stable sort**: Maintains relative order for equal elements
- **Multi-level sorting**: Secondary sort by date when primary is equal
- **Null handling**: Treats missing values as 0 for numeric sorts

### Performance
- **O(n log n)**: Standard JavaScript sort
- **Instant**: No network latency
- **Cached**: Jobs stored in memory
- **Efficient**: Only re-renders HTML, doesn't refetch data

### State Management
```javascript
allJobs = [];  // Global array stores all jobs
sortJobHistory();  // Re-sorts and re-renders
// No API calls needed for sorting
```

## Status Display

### Three Status Types:

**Completed:**
- Color: Green (#388e3c)
- Icon: ✓
- Background: Light green (#e8f5e9)

**Failed:**
- Color: Red (#c62828)
- Icon: ✗
- Background: Light red (#ffebee)

**Cancelled:**
- Color: Orange (#f57c00)
- Icon: ⊗
- Background: Light orange (#fff3e0)

## Benefits

1. **Better Organization**: Find jobs quickly
2. **Flexible Views**: Multiple sorting criteria
3. **No Reload**: Instant re-sorting
4. **Persistent**: Sort preference maintained during session
5. **Intuitive**: Clear labels and logical ordering
6. **Bilingual**: Full translation support

## Future Enhancements

Possible improvements:
- Save sort preference to localStorage
- Add filtering options (by status, type, date range)
- Search functionality
- Reverse sort toggle button
- Multi-column sorting
- Export sorted list
- Pagination for large histories
