# 安裝指南 (Installation Guide)

| 版本 | 日期 | 作者 | 說明 |
|------|------|------|------|
| 1.0.0 | 2026-05-20 | Mavis | 初始版本 |

## 環境需求
- **Python**: 3.10 或更高版本
- **作業系統**: Linux, macOS, Windows (WSL 推薦)
- **資料庫**: SQLite 3 (內建於 Python，無需額外安裝)
- **套件管理**: `pip` 或 `uv`

## 步驟 1: 複製專案
```bash
git clone https://github.com/Mavisy75106/attendance-system.git
cd attendance-system
```

## 步驟 2: 建立虛擬環境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
```

## 步驟 3: 安裝依賴套件
```bash
pip install -r requirements.txt
```

## 步驟 4: 環境變數設定 (可選)
若需切換資料庫，請建立 `.env` 檔案：
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## 步驟 5: 初始化資料庫與種子資料
```bash
python seed_data.py
```
此腳本會自動建立資料表並填入測試用的員工與假日資料。

## 步驟 6: 啟動開發伺服器
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
伺服器啟動後，於瀏覽器開啟 `http://localhost:8000`。

## 常見問題 (FAQ)

### Q1: 啟動時報 `ModuleNotFoundError`
請確認已啟用虛擬環境：`source venv/bin/activate`，並確認 `venv/lib/python3.x/site-packages` 已包含所需套件。

### Q2: 資料庫檔案無法寫入
檢查資料夾權限，或手動建立資料夾：
```bash
mkdir -p data
chmod 755 data
```

### Q3: 如何切換到 PostgreSQL？
修改 `.env` 中的 `DATABASE_URL`，並安裝 `psycopg2-binary`：
```bash
pip install psycopg2-binary
uvicorn main:app --reload
```

## 生產環境部署建議
1. 使用 `gunicorn` 搭配 `workers` 參數提升並發處理能力：
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
2. 將 `DATABASE_URL` 指向外部 PostgreSQL 或 MySQL。
3. 配置 Nginx 反向代理與 SSL/TLS 憑證。
4. 設定 `DEBUG=False` 與 `SECRET_KEY`。

---
*安裝文件由 Mavis 編寫，如需協助請提 Issue 至 GitHub 儲存庫*
