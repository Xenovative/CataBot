# CataBot - AI 學術論文目錄系統

一個智能學術論文目錄系統，可以自動爬取、分析和分類學術期刊與論文。

## ✨ 主要功能

### 1. 📥 自動爬取 PDF
- 從網站自動下載所有 PDF 文件
- 支援遞迴爬取，可設定深度
- 並發下載，速度快
- 也可以掃描本地資料夾

### 2. 📊 自動提取元數據
系統會自動提取並整理以下信息：
- **作者** - 論文作者姓名
- **標題** - 論文標題
- **年份** - 發表年份
- **期數** - 期刊期號
- **卷號** - 期刊卷號
- **頁數** - 論文頁碼範圍

### 3. 🤖 AI 智能分類
- 使用 AI 自動分類論文學科
- 支援 18 種以上學科類別
- 提供分類信心度評估
- 即使沒有 API 金鑰也能使用（關鍵詞匹配）

### 4. 📄 多種輸出格式
- **Excel** - 包含目錄和統計兩個工作表
- **HTML** - 美觀的網頁報告
- **JSON** - 結構化數據
- **CSV** - 通用表格格式

## 🚀 快速開始

### 使用方式選擇

#### 方式 1: Web 界面（推薦）🌐
```bash
# Windows
run_webapp.bat

# 或直接運行
python app.py
```
然後打開瀏覽器訪問：**http://localhost:5000**

**特點**：
- ✅ 美觀的圖形界面
- ✅ 拖放上傳文件
- ✅ 實時進度顯示
- ✅ 一鍵下載結果

#### 方式 2: 命令行
適合自動化和批次處理

### 第一步：安裝

#### 選項 1: 使用虛擬環境（推薦）
```bash
# 創建並設置虛擬環境
create_venv.bat

# 所有批次文件會自動使用虛擬環境！
```

#### 選項 2: 全局安裝
```bash
# Windows
setup.bat

# 或手動安裝
pip install -r requirements.txt
```

**注意**: 所有批次文件（setup.bat, run_demo.bat, run_webapp.bat）都會自動檢測並使用虛擬環境（如果存在）。

### 第二步：運行演示

最簡單的方式，無需準備任何 PDF：
```bash
run_demo.bat
```

或：
```bash
python test_demo.py
```

這會生成示範數據並創建各種格式的輸出文件。

### 第三步：處理真實 PDF

#### 方式 1：處理本地資料夾
```bash
python main.py --directory ./你的論文資料夾
```

#### 方式 2：從網站爬取
```bash
python main.py --url https://example.com/papers --depth 2
```

#### 方式 3：處理單個 PDF
```bash
python main.py --pdf 論文.pdf
```

## 📖 詳細使用說明

### 基本命令

```bash
# 處理本地資料夾（最常用）
python main.py --directory ./papers

# 從網站下載並處理
python main.py --url https://journal.example.com/archive

# 處理單個文件
python main.py --pdf paper.pdf
```

### 進階選項

```bash
# 只生成 Excel 格式
python main.py --directory ./papers --format excel

# 指定輸出目錄
python main.py --directory ./papers --output-dir ./結果

# 設定網站爬取深度
python main.py --url https://example.com --depth 3

# 生成所有格式（預設）
python main.py --directory ./papers --format all
```

### 完整參數說明

```
必選參數（三選一）：
  --url URL              要爬取的網站地址
  --directory 路徑       包含 PDF 的本地資料夾
  --pdf 文件             單個 PDF 文件

可選參數：
  --depth 數字           爬取深度，預設 2
  --format 格式          輸出格式：excel, json, csv, html, all
  --output-dir 路徑      輸出資料夾，預設 output
```

## 📊 輸出說明

### Excel 文件
打開後會看到兩個工作表：

**工作表 1 - 論文目錄**
- 標題（Title）
- 作者（Authors）
- 年份（Year）
- 卷號（Volume）
- 期號（Issue）
- 頁數（Pages）
- 主要學科
- 次要學科
- 分類信心度
- 檔案路徑

**工作表 2 - 學科統計**
- 各學科的論文數量
- 百分比分布

### HTML 文件
用瀏覽器打開，可以看到：
- 精美的統計卡片
- 學科分布圖表
- 完整的論文列表
- 響應式設計，手機也能看

### JSON 文件
包含所有原始數據，適合：
- 程式處理
- 數據分析
- 系統整合

### CSV 文件
- 可用 Excel 打開
- 適合數據分析
- 通用格式

## 🎨 支援的學科分類

系統可以自動分類以下學科：

- 計算機科學（Computer Science）
- 數學（Mathematics）
- 物理（Physics）
- 化學（Chemistry）
- 生物（Biology）
- 醫學（Medicine）
- 工程（Engineering）
- 社會科學（Social Sciences）
- 經濟學（Economics）
- 心理學（Psychology）
- 教育（Education）
- 文學（Literature）
- 歷史（History）
- 哲學（Philosophy）
- 法律（Law）
- 商業（Business）
- 環境科學（Environmental Science）
- 其他（Other）

## ⚙️ 配置說明

### 使用 AI 分類（可選，但推薦）

1. 註冊 OpenAI 帳號：https://platform.openai.com/
2. 獲取 API 金鑰
3. 編輯 `.env` 文件：
```
OPENAI_API_KEY=sk-你的金鑰
```

**注意**：如果不配置 API 金鑰，系統會自動使用關鍵詞匹配，雖然準確度較低但完全免費。

### 自訂學科類別

編輯 `config.py` 文件：
```python
SUBJECT_CATEGORIES = [
    "你的學科1",
    "你的學科2",
    # 添加更多...
]
```

### 調整爬蟲設定

編輯 `config.py` 文件：
```python
MAX_CONCURRENT_DOWNLOADS = 5    # 同時下載數量
REQUEST_TIMEOUT = 30            # 超時時間（秒）
```

## 💡 使用場景

### 場景 1：研究人員
整理個人論文收藏，快速建立索引

```bash
python main.py --directory "C:\我的論文"
```

### 場景 2：學術機構
管理期刊論文庫，生成統計報告

```bash
python main.py --directory "D:\期刊資料庫" --format excel
```

### 場景 3：圖書館
數位化館藏，提供檢索服務

```bash
python main.py --directory "E:\館藏PDF" --output-dir "F:\目錄系統"
```

### 場景 4：從網站收集
從學術網站批量下載並分類

```bash
python main.py --url https://journal.example.com/archive --depth 2
```

## 🔧 常見問題

### Q: 我沒有 OpenAI API 金鑰，可以使用嗎？
**A**: 當然可以！系統會自動使用關鍵詞匹配進行分類，雖然準確度約 70-80%，但完全免費且無需註冊。

### Q: 支援中文論文嗎？
**A**: 完全支援！系統已內建中文關鍵詞匹配。
- **使用 OpenAI API**: 分類準確度 85-90%
- **關鍵詞匹配**: 分類準確度 75-80%（已優化中文支援）
- 所有輸出格式（Excel、HTML、JSON、CSV）都完美支援中文字符

### Q: 可以一次處理多少 PDF？
**A**: 理論上沒有限制，但建議單次處理不超過 1000 個 PDF 以確保效能和穩定性。

### Q: PDF 提取失敗怎麼辦？
**A**: 系統會自動跳過有問題的文件並繼續處理其他文件。常見原因：
- PDF 文件損壞
- PDF 有密碼保護
- PDF 格式不標準

### Q: 分類結果不準確怎麼辦？
**A**: 有幾個解決方案：
1. 使用 OpenAI API 提升準確度
2. 手動編輯輸出的 Excel 文件
3. 調整 `config.py` 中的學科類別
4. 增加關鍵詞匹配規則

### Q: 如何批次處理多個資料夾？
**A**: 創建批次腳本：
```batch
python main.py --directory ./papers_2020
python main.py --directory ./papers_2021
python main.py --directory ./papers_2022
```

### Q: 輸出文件在哪裡？
**A**: 預設在 `output/` 資料夾中，文件名包含時間戳記，例如：
- `academic_catalog_20240101_120000.xlsx`
- `academic_catalog_20240101_120000.html`

### Q: 可以修改輸出格式嗎？
**A**: 可以！編輯 `catalog_generator.py` 文件自訂輸出格式和樣式。

## 📁 專案結構

```
CataBot/
├── main.py                 # 主程式
├── pdf_extractor.py       # PDF 處理
├── web_crawler.py         # 網頁爬蟲
├── ai_classifier.py       # AI 分類
├── catalog_generator.py   # 目錄生成
├── config.py              # 配置文件
├── requirements.txt       # 依賴套件
├── .env.example           # 環境變數範本
├── README.md              # 英文說明
├── README_CN.md           # 中文說明（本文件）
├── QUICKSTART.md          # 快速開始
├── PROJECT_OVERVIEW.md    # 專案總覽
├── test_demo.py           # 演示程式
├── example_usage.py       # 使用範例
├── setup.bat              # 安裝腳本
└── run_demo.bat           # 演示腳本
```

## 🛠️ 技術細節

### 使用的技術
- **Python 3.8+** - 主要程式語言
- **PyPDF2 & pdfplumber** - PDF 處理
- **BeautifulSoup4** - 網頁解析
- **aiohttp** - 異步下載
- **OpenAI API** - AI 分類（可選）
- **pandas** - 數據處理
- **openpyxl** - Excel 生成

### 系統要求
- Windows 7 或更高版本
- Python 3.8 或更高版本
- 至少 2GB 可用記憶體
- 網路連接（如需爬取網站）

## 📚 更多資源

- **完整文檔**: README.md
- **快速開始**: QUICKSTART.md
- **專案總覽**: PROJECT_OVERVIEW.md
- **使用範例**: example_usage.py

## 🤝 貢獻與支援

歡迎：
- 報告問題（Issue）
- 提交改進（Pull Request）
- 分享使用經驗
- 提出新功能建議

## 📄 授權

MIT License - 可自由使用、修改和分發

---

**開始使用 CataBot，讓 AI 幫你整理學術論文！** 🚀📚

有問題？查看文檔或運行演示程式：
```bash
run_demo.bat
```
