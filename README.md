# CataBot - AI Academic Paper Cataloging System

一個智能學術論文目錄系統，可以自動爬取、分析和分類學術期刊與論文。

An intelligent academic paper cataloging system that automatically crawls, analyzes, and classifies academic periodicals and papers.

## 功能特點 Features

### 1. 📥 PDF 爬取 PDF Crawling
- 自動從網站爬取所有可用的 PDF 文件
- 支援遞迴爬取（可設定深度）
- 並發下載，提高效率
- 支援本地目錄掃描

### 2. 📊 元數據提取 Metadata Extraction
自動提取並生成文章總表，包含：
- **作者 (Authors)**: 從 PDF 元數據或內容中提取
- **標題 (Title)**: 智能識別論文標題
- **年份 (Year)**: 出版年份
- **期數 (Issue)**: 期刊期號
- **卷號 (Volume)**: 期刊卷號
- **頁數 (Pages)**: 頁碼範圍

### 3. 🤖 AI 學科分類 AI Subject Classification
- 使用 OpenAI GPT 進行智能分類
- 支援 18+ 個學科類別
- 提供主要學科和次要學科
- 包含分類信心度評估
- 備用關鍵詞分類方法（無需 API）

### 4. 📄 多格式輸出 Multiple Output Formats
- **Excel (.xlsx)**: 包含多個工作表（目錄、統計）
- **JSON**: 結構化數據，便於程式處理
- **CSV**: 通用表格格式
- **HTML**: 美觀的網頁報告，含統計圖表

## 安裝 Installation

### 前置需求 Prerequisites
- Python 3.8 或更高版本
- pip (Python 套件管理器)

### 步驟 Steps

1. **克隆或下載專案**
```bash
cd c:\AIapps\CataBot
```

2. **安裝依賴套件**
```bash
pip install -r requirements.txt
```

3. **配置 API 金鑰（可選）**
```bash
# 複製環境變數範本
copy .env.example .env

# 編輯 .env 文件，添加你的 OpenAI API 金鑰
# OPENAI_API_KEY=sk-your-key-here
```

> **注意**: 如果不配置 API 金鑰，系統會使用關鍵詞匹配進行分類（準確度較低但免費）

## 使用方法 Usage

### 基本命令 Basic Commands

#### 1. 處理本地目錄中的 PDF
```bash
python main.py --directory ./papers
```

#### 2. 從網站爬取並處理 PDF
```bash
python main.py --url https://example.com/papers --depth 2
```

#### 3. 處理單個 PDF 文件
```bash
python main.py --pdf paper.pdf
```

### 進階選項 Advanced Options

#### 指定輸出格式
```bash
# 只生成 Excel
python main.py --directory ./papers --format excel

# 只生成 JSON
python main.py --directory ./papers --format json

# 生成所有格式（預設）
python main.py --directory ./papers --format all
```

#### 自訂輸出目錄
```bash
python main.py --directory ./papers --output-dir ./results
```

#### 設定爬取深度
```bash
python main.py --url https://example.com --depth 3
```

### 完整參數說明 Full Parameters

```
python main.py [OPTIONS]

必選參數（三選一）:
  --url URL              要爬取的網站 URL
  --directory DIR        包含 PDF 的本地目錄
  --pdf FILE            單個 PDF 文件路徑

可選參數:
  --depth N             網站爬取深度 (預設: 2)
  --format FORMAT       輸出格式: excel, json, csv, html, all (預設: all)
  --output-dir DIR      輸出目錄 (預設: output)
```

## 輸出範例 Output Examples

### Excel 輸出
包含兩個工作表：
1. **論文目錄 (Catalog)**: 完整的論文列表
2. **學科統計 (Summary)**: 各學科論文數量統計

### JSON 輸出
```json
{
  "metadata": {
    "generated_at": "2024-01-01T12:00:00",
    "total_papers": 50
  },
  "papers": [
    {
      "title": "Machine Learning in Healthcare",
      "authors": "John Doe, Jane Smith",
      "year": "2023",
      "volume": "15",
      "issue": "3",
      "pages": "45-67",
      "classification": {
        "primary_subject": "Computer Science",
        "secondary_subjects": ["Medicine"],
        "confidence": "high"
      }
    }
  ]
}
```

### HTML 輸出
生成美觀的網頁報告，包含：
- 統計摘要卡片
- 學科分布表格
- 完整論文列表
- 響應式設計

## 學科分類類別 Subject Categories

系統支援以下學科分類：

- Computer Science (計算機科學)
- Mathematics (數學)
- Physics (物理)
- Chemistry (化學)
- Biology (生物)
- Medicine (醫學)
- Engineering (工程)
- Social Sciences (社會科學)
- Economics (經濟學)
- Psychology (心理學)
- Education (教育)
- Literature (文學)
- History (歷史)
- Philosophy (哲學)
- Law (法律)
- Business (商業)
- Environmental Science (環境科學)
- Other (其他)

## 專案結構 Project Structure

```
CataBot/
├── main.py                 # 主程式入口
├── config.py              # 配置文件
├── pdf_extractor.py       # PDF 元數據提取
├── web_crawler.py         # 網頁爬蟲和 PDF 下載
├── ai_classifier.py       # AI 學科分類
├── catalog_generator.py   # 目錄生成器
├── requirements.txt       # Python 依賴
├── .env.example          # 環境變數範本
├── README.md             # 說明文件
├── output/               # 輸出目錄（自動創建）
└── pdfs/                 # 下載的 PDF（自動創建）
```

## 部署 Deployment

### Linux 服務器部署 Linux Server Deployment

快速部署到 Linux 服務器（Ubuntu/Debian）：

```bash
# 一鍵部署
chmod +x deploy.sh
sudo ./deploy.sh
```

部署腳本會自動：
- 安裝所有依賴
- 創建 systemd 服務
- 配置 Nginx 反向代理
- 設置日誌輪換和備份

### 部署後驗證 Post-Deployment Verification

```bash
# 運行驗證腳本
chmod +x verify_deployment.sh
sudo ./verify_deployment.sh

# 運行診斷工具
chmod +x diagnose.sh
sudo ./diagnose.sh
```

### 部署文檔 Deployment Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 完整部署指南
- **[DEPLOYMENT_FIXES.md](DEPLOYMENT_FIXES.md)** - 部署問題修復說明
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 常用命令快速參考

### 服務管理 Service Management

```bash
# 啟動服務
sudo systemctl start catabot

# 查看狀態
sudo systemctl status catabot

# 查看日誌
sudo journalctl -u catabot -f
```

更多命令請參考 [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

## 技術棧 Tech Stack

- **Python 3.8+**: 主要程式語言
- **Flask**: Web 框架
- **PyPDF2 & pdfplumber**: PDF 處理
- **BeautifulSoup4**: HTML 解析
- **aiohttp**: 異步 HTTP 請求
- **OpenAI API**: AI 分類（可選）
- **pandas**: 數據處理
- **openpyxl**: Excel 生成
- **Nginx**: 反向代理（生產環境）
- **systemd**: 服務管理（Linux）

## 常見問題 FAQ

### Q: 沒有 OpenAI API 金鑰可以使用嗎？
A: 可以！系統會自動使用關鍵詞匹配進行分類，雖然準確度較低，但完全免費且無需註冊。

### Q: 支援哪些語言的論文？
A: 系統支援多語言，但 AI 分類對英文論文效果最佳。中文論文也能處理，但建議使用關鍵詞分類。

### Q: 可以處理多少 PDF？
A: 理論上沒有限制，但建議單次處理不超過 1000 個 PDF 以確保效能。

### Q: PDF 提取失敗怎麼辦？
A: 系統會記錄錯誤並繼續處理其他文件。檢查 PDF 是否損壞或受密碼保護。

### Q: 如何自訂學科分類？
A: 編輯 `config.py` 中的 `SUBJECT_CATEGORIES` 列表。

## 貢獻 Contributing

歡迎提交 Issue 和 Pull Request！

## 授權 License

MIT License

## 聯絡 Contact

如有問題或建議，請開 Issue。

---

**享受自動化的學術目錄管理！ Enjoy automated academic cataloging!** 📚✨
