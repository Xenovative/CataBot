// Internationalization (i18n) for CataBot
// Supports English and Traditional Chinese

const translations = {
    'en': {
        // Header
        'app_title': 'CataBot',
        'app_subtitle': 'AI Academic Paper Cataloging System',
        
        // Tabs
        'tab_upload': '📤 Upload Files',
        'tab_crawl': '🌐 Crawl Website',
        'tab_directory': '📁 Local Directory',
        'tab_history': '📜 Job History',
        'tab_settings': '⚙️ Settings',
        
        // Upload Tab
        'upload_drop_title': 'Drop PDF files here or click to browse',
        'upload_drop_subtitle': 'Support multiple files',
        'upload_format_label': 'Output Format:',
        'upload_button': '🚀 Start Processing',
        
        // Crawl Tab
        'crawl_url_label': 'Website URL:',
        'crawl_url_placeholder': 'https://example.com/papers',
        'crawl_depth_label': 'Crawl Depth:',
        'crawl_depth_1': '1 - Current page only',
        'crawl_depth_2': '2 - Recommended',
        'crawl_depth_3': '3 - Deep crawl',
        'crawl_format_label': 'Output Format:',
        'crawl_js_rendering': 'Enable JavaScript Rendering (for dynamic sites)',
        'crawl_js_help': 'Use this for sites that load content with JavaScript (slower but more thorough)',
        'crawl_button': '🌐 Start Crawling',
        
        // Directory Tab
        'dir_note': '<strong>Note:</strong> Enter the full path to a directory containing PDF files on your server.',
        'dir_path_label': 'Directory Path:',
        'dir_path_placeholder': 'C:\\Papers or /home/user/papers',
        'dir_format_label': 'Output Format:',
        'dir_button': '📁 Process Directory',
        
        // History Tab
        'history_title': 'Job History',
        'history_refresh': '🔄 Refresh',
        'history_info': '<strong>Note:</strong> View and manage your past processing jobs. You can re-classify papers with updated settings.',
        'history_sort_label': 'Sort by:',
        'history_sort_date_desc': 'Date (Newest First)',
        'history_sort_date_asc': 'Date (Oldest First)',
        'history_sort_status': 'Status',
        'history_sort_papers_desc': 'Papers (Most First)',
        'history_sort_papers_asc': 'Papers (Least First)',
        'history_sort_type': 'Job Type',
        'history_view_details': 'View Details',
        'history_reclassify': 'Re-classify',
        'history_refetch': 'Re-fetch & Re-classify',
        
        // Format Options
        'format_all': 'All Formats (Excel, HTML, JSON, CSV)',
        'format_excel': 'Excel Only',
        'format_html': 'HTML Only',
        'format_json': 'JSON Only',
        'format_csv': 'CSV Only',
        
        // Progress
        'progress_title': 'Processing...',
        'progress_init': 'Initializing...',
        'progress_overall': 'Overall Progress',
        'progress_current_task': 'Current Task:',
        'progress_cancel': '✕ Cancel Job',
        'progress_files': 'Files Processed',
        'progress_papers': 'Papers Found',
        'progress_time': 'Elapsed Time',
        'progress_log': 'Processing Log',
        'progress_log_show': 'Show Details',
        'progress_log_hide': 'Hide Details',
        'progress_cancel_confirm': 'Are you sure you want to cancel this job?',
        'progress_cancelled': 'Job cancelled successfully',
        'progress_cancel_failed': 'Failed to cancel job',
        
        // Results
        'results_title': '✅ Processing Complete!',
        'results_stats_papers': 'Papers Processed',
        'results_stats_categories': 'Subject Categories',
        'results_stats_time': 'Processing Time',
        'results_download_title': 'Download Results:',
        'results_download_excel': '📥 Download EXCEL',
        'results_download_html': '📥 Download HTML',
        'results_download_json': '📥 Download JSON',
        'results_download_csv': '📥 Download CSV',
        'results_subject_title': 'Subject Distribution:',
        'results_reset_button': '🔄 Process More Files',
        
        // Config
        'config_title': '⚙️ System Configuration',
        'config_ai': 'AI Classification:',
        'config_ai_configured': '✅ OpenAI API Configured',
        'config_ai_free': '⚠️ Keyword Matching (Free)',
        'config_categories': 'Supported Categories:',
        'config_loading': 'Loading...',
        
        // Messages
        'msg_no_url': 'Please enter a URL',
        'msg_no_directory': 'Please enter a directory path',
        'msg_error': 'Error: ',
        'msg_job_resumed': 'Resuming previous job...',
        'msg_reclassify_confirm': 'Re-classify papers with current settings? This will create a new job.',
        'msg_reclassify_started': 'Re-classification started! Job ID:',
        'msg_refetch_confirm': 'Re-fetch papers from the original URL and re-classify them? This will create a new job.',
        'msg_refetch_started': 'Re-fetch started! Job ID:',
        
        // Settings Tab
        'settings_title': 'AI Configuration Settings',
        'settings_provider_label': 'AI Provider:',
        'settings_provider_openai': 'OpenAI',
        'settings_provider_anthropic': 'Anthropic Claude',
        'settings_provider_keyword': 'Keyword Matching (Free)',
        'settings_openai_section': 'OpenAI Settings',
        'settings_openai_key_label': 'API Key:',
        'settings_openai_key_placeholder': 'sk-...',
        'settings_openai_model_label': 'Model:',
        'settings_anthropic_section': 'Anthropic Settings',
        'settings_anthropic_key_label': 'API Key:',
        'settings_anthropic_key_placeholder': 'sk-ant-...',
        'settings_anthropic_model_label': 'Model:',
        'settings_fallback_label': 'Use Keyword Fallback:',
        'settings_fallback_help': 'Use keyword matching if AI classification fails',
        'settings_test_button': '🧪 Test Connection',
        'settings_save_button': '💾 Save Settings',
        'settings_save_success': 'Settings saved successfully!',
        'settings_save_error': 'Failed to save settings',
        'settings_test_success': 'API connection successful!',
        'settings_test_error': 'API connection failed',
        'settings_vision_extraction': 'Enable Vision-based Metadata Extraction (GPT-4 Vision)',
        'settings_vision_help': 'Uses AI to analyze PDF images for better metadata accuracy (requires OpenAI API)',
        'settings_categories_title': 'Custom Classification Categories',
        'settings_categories_help': 'Define your own subject categories for classification. Enter one category per line. Leave empty to use default categories.',
        'settings_categories_label': 'Categories (one per line):',
        'settings_categories_placeholder': 'Computer Science\nMathematics\nPhysics\n...',
        'settings_categories_default': '📋 Load Default Categories',
        'settings_categories_example': '📚 Load Example (Chinese Theology)',
        'settings_fast_mode': '⚡ Fast Mode (Text-only extraction)',
        'settings_fast_mode_help': 'Faster processing but lower accuracy. Skips vision extraction and uses cache.',
        'settings_info': '<strong>Note:</strong> API keys are stored locally and used for classification. OpenAI provides better accuracy than keyword matching.',
        
        // Language
        'lang_switch': '切換至繁體中文'
    },
    
    'zh-TW': {
        // Header
        'app_title': 'CataBot',
        'app_subtitle': 'AI 學術論文目錄系統',
        
        // Tabs
        'tab_upload': '📤 上傳檔案',
        'tab_crawl': '🌐 爬取網站',
        'tab_directory': '📁 本地目錄',
        'tab_history': '📜 工作歷史',
        'tab_settings': '⚙️ 設定',
        
        // Upload Tab
        'upload_drop_title': '拖放 PDF 檔案到此處或點擊瀏覽',
        'upload_drop_subtitle': '支援多個檔案',
        'upload_format_label': '輸出格式：',
        'upload_button': '🚀 開始處理',
        
        // Crawl Tab
        'crawl_url_label': '網站網址：',
        'crawl_url_placeholder': 'https://example.com/papers',
        'crawl_depth_label': '爬取深度：',
        'crawl_depth_1': '1 - 僅當前頁面',
        'crawl_depth_2': '2 - 推薦',
        'crawl_depth_3': '3 - 深度爬取',
        'crawl_format_label': '輸出格式：',
        'crawl_js_rendering': '啟用 JavaScript 渲染（用於動態網站）',
        'crawl_js_help': '用於載入內容時使用 JavaScript 的網站（較慢但更全面）',
        'crawl_button': '🌐 開始爬取',
        
        // Directory Tab
        'dir_note': '<strong>注意：</strong>請輸入伺服器上包含 PDF 檔案的目錄完整路徑。',
        'dir_path_label': '目錄路徑：',
        'dir_path_placeholder': 'C:\\Papers 或 /home/user/papers',
        'dir_format_label': '輸出格式：',
        'dir_button': '📁 處理目錄',
        
        // History Tab
        'history_title': '工作歷史',
        'history_refresh': '🔄 重新整理',
        'history_info': '<strong>注意：</strong>查看和管理您過去的處理工作。您可以使用更新的設定重新分類論文。',
        'history_sort_label': '排序方式：',
        'history_sort_date_desc': '日期（最新優先）',
        'history_sort_date_asc': '日期（最舊優先）',
        'history_sort_status': '狀態',
        'history_sort_papers_desc': '論文數（最多優先）',
        'history_sort_papers_asc': '論文數（最少優先）',
        'history_sort_type': '工作類型',
        'history_view_details': '查看詳情',
        'history_reclassify': '重新分類',
        'history_refetch': '重新抓取並分類',
        
        // Format Options
        'format_all': '所有格式（Excel、HTML、JSON、CSV）',
        'format_excel': '僅 Excel',
        'format_html': '僅 HTML',
        'format_json': '僅 JSON',
        'format_csv': '僅 CSV',
        
        // Progress
        'progress_title': '處理中...',
        'progress_init': '初始化中...',
        'progress_overall': '整體進度',
        'progress_current_task': '目前任務：',
        'progress_cancel': '✕ 取消工作',
        'progress_files': '已處理檔案',
        'progress_papers': '已找到論文',
        'progress_time': '經過時間',
        'progress_log': '處理記錄',
        'progress_log_show': '顯示詳情',
        'progress_log_hide': '隱藏詳情',
        'progress_cancel_confirm': '確定要取消此工作嗎？',
        'progress_cancelled': '工作已成功取消',
        'progress_cancel_failed': '取消工作失敗',
        
        // Results
        'results_title': '✅ 處理完成！',
        'results_stats_papers': '已處理論文',
        'results_stats_categories': '學科類別',
        'results_stats_time': '處理時間',
        'results_download_title': '下載結果：',
        'results_download_excel': '📥 下載 EXCEL',
        'results_download_html': '📥 下載 HTML',
        'results_download_json': '📥 下載 JSON',
        'results_download_csv': '📥 下載 CSV',
        'results_subject_title': '學科分布：',
        'results_reset_button': '🔄 處理更多檔案',
        
        // Config
        'config_title': '⚙️ 系統配置',
        'config_ai': 'AI 分類：',
        'config_ai_configured': '✅ 已配置 OpenAI API',
        'config_ai_free': '⚠️ 關鍵詞匹配（免費）',
        'config_categories': '支援的類別：',
        'config_loading': '載入中...',
        
        // Messages
        'msg_no_url': '請輸入網址',
        'msg_no_directory': '請輸入目錄路徑',
        'msg_error': '錯誤：',
        'msg_job_resumed': '正在恢復先前的工作...',
        'msg_reclassify_confirm': '使用目前設定重新分類論文？這將建立一個新工作。',
        'msg_reclassify_started': '重新分類已開始！工作 ID：',
        'msg_refetch_confirm': '從原始網址重新抓取論文並重新分類？這將建立一個新工作。',
        'msg_refetch_started': '重新抓取已開始！工作 ID：',
        
        // Settings Tab
        'settings_title': 'AI 配置設定',
        'settings_provider_label': 'AI 提供商：',
        'settings_provider_openai': 'OpenAI',
        'settings_provider_anthropic': 'Anthropic Claude',
        'settings_provider_keyword': '關鍵詞匹配（免費）',
        'settings_openai_section': 'OpenAI 設定',
        'settings_openai_key_label': 'API 金鑰：',
        'settings_openai_key_placeholder': 'sk-...',
        'settings_openai_model_label': '模型：',
        'settings_anthropic_section': 'Anthropic 設定',
        'settings_anthropic_key_label': 'API 金鑰：',
        'settings_anthropic_key_placeholder': 'sk-ant-...',
        'settings_anthropic_model_label': '模型：',
        'settings_fallback_label': '使用關鍵詞備用：',
        'settings_fallback_help': '如果 AI 分類失敗，使用關鍵詞匹配',
        'settings_test_button': '🧪 測試連接',
        'settings_save_button': '💾 儲存設定',
        'settings_save_success': '設定已成功儲存！',
        'settings_save_error': '儲存設定失敗',
        'settings_test_success': 'API 連線成功！',
        'settings_test_error': 'API 連線失敗',
        'settings_vision_extraction': '啟用視覺化元數據提取（GPT-4 Vision）',
        'settings_vision_help': '使用 AI 分析 PDF 圖像以提高元數據準確性（需要 OpenAI API）',
        'settings_categories_title': '自訂分類類別',
        'settings_categories_help': '定義您自己的主題類別進行分類。每行輸入一個類別。留空則使用預設類別。',
        'settings_categories_label': '類別（每行一個）：',
        'settings_categories_placeholder': '電腦科學\n數學\n物理學\n...',
        'settings_categories_default': '📋 載入預設類別',
        'settings_categories_example': '📚 載入範例（中文神學）',
        'settings_fast_mode': '⚡ 快速模式（純文字提取）',
        'settings_fast_mode_help': '處理速度更快但準確度較低。跳過視覺提取並使用快取。',
        'settings_info': '<strong>注意：</strong>API 金鑰儲存在本地並用於分類。OpenAI 提供比關鍵詞匹配更好的準確度。',
        
        // Language
        'lang_switch': 'Switch to English'
    }
};

// Get current language from localStorage or default to English
let currentLang = localStorage.getItem('catabot_lang') || 'en';

// Translation function
function t(key) {
    return translations[currentLang][key] || key;
}

// Update all translatable elements
function updateLanguage() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);
        
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            if (element.hasAttribute('placeholder')) {
                element.placeholder = translation;
            }
        } else if (element.innerHTML.includes('<')) {
            // Contains HTML, use innerHTML
            element.innerHTML = translation;
        } else {
            element.textContent = translation;
        }
    });
    
    // Update HTML lang attribute
    document.documentElement.lang = currentLang;
    
    // Update language switcher button
    const langBtn = document.getElementById('langSwitch');
    if (langBtn) {
        langBtn.textContent = t('lang_switch');
    }
    
    // Save to localStorage
    localStorage.setItem('catabot_lang', currentLang);
}

// Toggle language
function toggleLanguage() {
    currentLang = currentLang === 'en' ? 'zh-TW' : 'en';
    updateLanguage();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateLanguage();
});
