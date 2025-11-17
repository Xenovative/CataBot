# 快速開始指南 Quick Start Guide

## 5 分鐘快速上手

### 步驟 1: 安裝依賴
```bash
pip install -r requirements.txt
```

### 步驟 2: 準備 PDF 文件
將你的 PDF 文件放在一個資料夾中，例如 `./test_papers/`

### 步驟 3: 運行程式
```bash
python main.py --directory ./test_papers
```

### 步驟 4: 查看結果
結果會保存在 `output/` 目錄中：
- `academic_catalog_YYYYMMDD_HHMMSS.xlsx` - Excel 格式
- `academic_catalog_YYYYMMDD_HHMMSS.html` - 網頁報告
- `academic_catalog_YYYYMMDD_HHMMSS.json` - JSON 數據
- `academic_catalog_YYYYMMDD_HHMMSS.csv` - CSV 格式

## 使用場景範例

### 場景 1: 整理本地論文庫
```bash
# 處理你電腦上的論文資料夾
python main.py --directory "C:\Users\YourName\Documents\Papers"
```

### 場景 2: 從期刊網站爬取
```bash
# 從學術網站下載並分類
python main.py --url https://journal.example.com/archive --depth 2
```

### 場景 3: 快速查看單篇論文
```bash
# 分析單個 PDF
python main.py --pdf "research_paper.pdf"
```

### 場景 4: 只生成 Excel 報告
```bash
# 只要 Excel 格式
python main.py --directory ./papers --format excel
```

## 提升 AI 分類準確度

### 選項 1: 使用 OpenAI API（推薦）
1. 註冊 OpenAI 帳號: https://platform.openai.com/
2. 獲取 API 金鑰
3. 創建 `.env` 文件：
```
OPENAI_API_KEY=sk-your-key-here
```

### 選項 2: 使用免費關鍵詞分類
不需要任何設定，直接運行即可。準確度約 70-80%。

## 常用命令速查

```bash
# 基本使用
python main.py --directory ./papers

# 從網站爬取
python main.py --url https://example.com/papers

# 單個文件
python main.py --pdf paper.pdf

# 自訂輸出位置
python main.py --directory ./papers --output-dir ./results

# 只生成特定格式
python main.py --directory ./papers --format excel
python main.py --directory ./papers --format json
python main.py --directory ./papers --format html
```

## 輸出文件說明

### Excel 文件
- **論文目錄** 工作表: 所有論文的詳細信息
- **學科統計** 工作表: 各學科的論文數量

### HTML 文件
用瀏覽器打開，可以看到：
- 總論文數和學科類別數
- 學科分布圖表
- 完整論文列表

### JSON 文件
適合程式處理，包含所有原始數據

### CSV 文件
可用 Excel 或其他表格軟體打開

## 疑難排解

### 問題: 找不到 PDF
**解決**: 確認目錄路徑正確，使用絕對路徑或相對路徑

### 問題: 提取失敗
**解決**: 某些 PDF 可能受保護或損壞，系統會跳過並繼續處理其他文件

### 問題: 分類不準確
**解決**: 
1. 使用 OpenAI API 提升準確度
2. 編輯 `config.py` 自訂學科類別
3. 手動調整輸出的 Excel 文件

### 問題: 網站爬取失敗
**解決**:
1. 檢查網站是否可訪問
2. 某些網站可能有反爬蟲機制
3. 嘗試降低並發數（編輯 `config.py`）

## 進階技巧

### 批次處理多個資料夾
創建批次腳本 `batch_process.bat`:
```batch
python main.py --directory ./papers_2020 --output-dir ./output_2020
python main.py --directory ./papers_2021 --output-dir ./output_2021
python main.py --directory ./papers_2022 --output-dir ./output_2022
```

### 自訂學科分類
編輯 `config.py`:
```python
SUBJECT_CATEGORIES = [
    "你的學科1",
    "你的學科2",
    # ... 添加更多
]
```

### 調整爬蟲設定
編輯 `config.py`:
```python
MAX_CONCURRENT_DOWNLOADS = 3  # 降低並發數
REQUEST_TIMEOUT = 60  # 增加超時時間
```

## 下一步

- 閱讀完整的 [README.md](README.md)
- 查看 [範例輸出](output/)
- 自訂配置文件 `config.py`
- 整合到你的工作流程

---

**開始整理你的學術論文庫吧！** 🚀
