# CataBot 專案總覽 Project Overview

## 🎯 專案目標

創建一個智能學術論文目錄系統，實現：
1. **自動爬取** - 從網站或本地目錄收集 PDF
2. **元數據提取** - 自動提取作者、標題、年份、期數等信息
3. **AI 分類** - 使用 AI 進行學科分類
4. **多格式輸出** - 生成 Excel、HTML、JSON、CSV 等格式的目錄

## 📁 專案結構

```
CataBot/
├── 核心模組 Core Modules
│   ├── main.py                 # 主程式入口
│   ├── pdf_extractor.py       # PDF 元數據提取
│   ├── web_crawler.py         # 網頁爬蟲
│   ├── ai_classifier.py       # AI 分類器
│   └── catalog_generator.py   # 目錄生成器
│
├── 配置文件 Configuration
│   ├── config.py              # 系統配置
│   ├── .env.example           # 環境變數範本
│   └── requirements.txt       # Python 依賴
│
├── 文檔 Documentation
│   ├── README.md              # 完整說明文件
│   ├── QUICKSTART.md          # 快速開始指南
│   └── PROJECT_OVERVIEW.md    # 專案總覽（本文件）
│
├── 示範與測試 Demo & Testing
│   ├── test_demo.py           # 演示腳本
│   ├── example_usage.py       # 使用範例
│   └── run_demo.bat           # Windows 快速啟動
│
└── 輸出目錄 Output (自動創建)
    ├── output/                # 目錄輸出
    └── pdfs/                  # 下載的 PDF
```

## 🔧 核心功能模組

### 1. PDF Extractor (pdf_extractor.py)
**功能**: 從 PDF 提取元數據
- 使用 PyPDF2 和 pdfplumber 雙引擎
- 智能模式匹配提取標題、作者、年份
- 支援多種 PDF 格式
- 錯誤處理和容錯機制

**關鍵類**: `PDFExtractor`
**主要方法**:
- `extract_from_pdf()` - 提取完整元數據
- `_extract_metadata()` - 提取 PDF 屬性
- `_extract_text()` - 提取文本內容
- `_enhance_metadata()` - 增強元數據

### 2. Web Crawler (web_crawler.py)
**功能**: 爬取網站並下載 PDF
- 異步並發下載
- 遞迴爬取支援
- 智能 URL 去重
- 進度條顯示

**關鍵類**: `AcademicCrawler`
**主要方法**:
- `crawl_website()` - 爬取網站
- `_find_pdf_links()` - 遞迴查找 PDF
- `_download_pdf()` - 下載單個 PDF
- `crawl_directory()` - 掃描本地目錄

### 3. AI Classifier (ai_classifier.py)
**功能**: 智能學科分類
- OpenAI GPT 分類（可選）
- 關鍵詞匹配備用方案
- 支援 18+ 學科類別
- 信心度評估

**關鍵類**: `AIClassifier`
**主要方法**:
- `classify_paper()` - 分類單篇論文
- `_classify_with_ai()` - AI 分類
- `_classify_with_keywords()` - 關鍵詞分類
- `batch_classify()` - 批次分類

### 4. Catalog Generator (catalog_generator.py)
**功能**: 生成多格式目錄
- Excel（含統計工作表）
- HTML（美觀網頁報告）
- JSON（結構化數據）
- CSV（通用格式）

**關鍵類**: `CatalogGenerator`
**主要方法**:
- `generate_catalog()` - 生成目錄
- `_generate_excel()` - Excel 輸出
- `_generate_html()` - HTML 輸出
- `_generate_json()` - JSON 輸出

## 🚀 快速開始

### 方法 1: 運行演示（推薦新手）
```bash
# Windows 用戶
run_demo.bat

# 或直接運行
python test_demo.py
```

### 方法 2: 處理真實 PDF
```bash
# 安裝依賴
pip install -r requirements.txt

# 處理本地目錄
python main.py --directory ./your_papers

# 從網站爬取
python main.py --url https://example.com/papers
```

## 📊 輸出格式說明

### Excel 輸出
- **工作表 1**: 論文目錄
  - 標題、作者、年份、卷號、期號、頁數
  - 主要學科、次要學科、分類信心度
  - 檔案路徑
- **工作表 2**: 學科統計
  - 各學科論文數量
  - 百分比分布

### HTML 輸出
- 響應式設計
- 統計卡片展示
- 學科分布表格
- 完整論文列表
- 可直接用瀏覽器查看

### JSON 輸出
- 完整結構化數據
- 包含所有元數據
- 適合程式處理
- 易於整合其他系統

### CSV 輸出
- 通用表格格式
- 可用 Excel 打開
- 適合數據分析
- 支援 UTF-8 編碼

## 🎨 學科分類類別

系統支援 18 個主要學科：
1. Computer Science (計算機科學)
2. Mathematics (數學)
3. Physics (物理)
4. Chemistry (化學)
5. Biology (生物)
6. Medicine (醫學)
7. Engineering (工程)
8. Social Sciences (社會科學)
9. Economics (經濟學)
10. Psychology (心理學)
11. Education (教育)
12. Literature (文學)
13. History (歷史)
14. Philosophy (哲學)
15. Law (法律)
16. Business (商業)
17. Environmental Science (環境科學)
18. Other (其他)

## 🔑 配置選項

### config.py 主要配置
```python
# API 配置
OPENAI_API_KEY          # OpenAI API 金鑰（可選）

# 爬蟲配置
MAX_CONCURRENT_DOWNLOADS = 5    # 並發下載數
REQUEST_TIMEOUT = 30            # 請求超時（秒）

# 輸出配置
OUTPUT_DIR = 'output'           # 輸出目錄
```

### .env 環境變數
```
OPENAI_API_KEY=sk-your-key-here
```

## 📈 使用場景

### 場景 1: 學術機構
- 整理期刊論文庫
- 建立論文索引
- 學科統計分析

### 場景 2: 研究人員
- 管理個人論文收藏
- 快速查找論文
- 分類整理文獻

### 場景 3: 圖書館
- 數位化館藏管理
- 自動化編目
- 提供檢索服務

### 場景 4: 出版社
- 期刊內容管理
- 論文分類歸檔
- 統計報告生成

## 🛠️ 技術棧

### Python 核心庫
- **asyncio**: 異步編程
- **aiohttp**: 異步 HTTP 請求
- **BeautifulSoup4**: HTML 解析

### PDF 處理
- **PyPDF2**: PDF 元數據提取
- **pdfplumber**: 高級文本提取

### AI & 數據處理
- **OpenAI API**: GPT 分類（可選）
- **pandas**: 數據處理
- **openpyxl**: Excel 生成

### 輔助工具
- **tqdm**: 進度條
- **python-dotenv**: 環境變數管理

## 🔄 工作流程

```
1. 輸入來源
   ├─ 網站 URL → 爬蟲下載 PDF
   ├─ 本地目錄 → 掃描 PDF 文件
   └─ 單個 PDF → 直接處理
           ↓
2. PDF 處理
   ├─ 提取元數據（標題、作者等）
   ├─ 提取文本內容
   └─ 錯誤處理
           ↓
3. AI 分類
   ├─ OpenAI GPT 分類（如有 API）
   └─ 關鍵詞匹配（備用方案）
           ↓
4. 生成目錄
   ├─ Excel 報表
   ├─ HTML 網頁
   ├─ JSON 數據
   └─ CSV 文件
           ↓
5. 輸出結果
   └─ 保存到 output/ 目錄
```

## 📝 開發建議

### 擴展功能
1. **支援更多文件格式**: DOC, DOCX, TXT
2. **增強元數據提取**: DOI, ISSN, 關鍵詞
3. **多語言支援**: 更好的中文處理
4. **數據庫整合**: MySQL, PostgreSQL
5. **Web 界面**: Flask/Django 網頁版

### 性能優化
1. **緩存機制**: 避免重複處理
2. **並行處理**: 多進程加速
3. **增量更新**: 只處理新文件
4. **批次優化**: 大量文件處理

### 質量提升
1. **單元測試**: pytest 測試框架
2. **日誌系統**: 詳細的運行日誌
3. **錯誤恢復**: 斷點續傳
4. **數據驗證**: 元數據準確性檢查

## 🐛 常見問題

### Q: 沒有 API 金鑰可以用嗎？
A: 可以！系統會自動使用關鍵詞分類，準確度約 70-80%。

### Q: 支援中文論文嗎？
A: 支援，但英文論文效果更好。建議中文論文使用關鍵詞分類。

### Q: 可以處理多少 PDF？
A: 理論無限制，建議單次 < 1000 個以確保性能。

### Q: 分類不準確怎麼辦？
A: 可以手動編輯輸出的 Excel 文件，或調整 config.py 中的分類類別。

### Q: 如何自訂學科類別？
A: 編輯 `config.py` 中的 `SUBJECT_CATEGORIES` 列表。

## 📞 支援與貢獻

- **問題報告**: 開 GitHub Issue
- **功能建議**: Pull Request 歡迎
- **文檔改進**: 隨時提交

## 📄 授權

MIT License - 自由使用、修改、分發

---

**開始使用 CataBot，讓 AI 幫你整理學術論文！** 🚀📚
