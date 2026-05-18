# 員工出勤管理系統 - 系統設計文件

| 版本 | 日期 | 作者 | 說明 |
|------|------|------|------|
| 1.0.0 | 2026-05-20 | Mavis | 初始版本 |

## 1. 專案概述
本系統為企業級員工出勤管理後台，提供員工資料維護、打卡紀錄、假勤申請、加班核算及公司行事曆管理功能。系統採用 B/S 架構，前端以 HTML/JavaScript 搭配 Tailwind CSS 建置，後端以 FastAPI 提供 RESTful API，資料庫使用 SQLite。

## 2. 技術選型
- **後端框架**: FastAPI (Python)
- **ORM**: SQLAlchemy 2.0
- **資料庫**: SQLite (生產環境可替換為 PostgreSQL)
- **前端樣式**: Tailwind CSS + Vanilla JS
- **部署方式**: Uvicorn / Gunicorn + Nginx

## 3. 系統架構
```
[Client Browser] ←→ [FastAPI Server] ←→ [SQLite Database]
       ↑                  ↑
   [Static Files]    [API Routers]
   [Templates]      [Services/Models]
```

### 3.1 模組劃分
| 模組 | 路徑 | 職責 |
|------|------|------|
| `main.py` | 根目錄 | 應用初始化、CORS、路由註冊 |
| `database.py` | 根目錄 | 連線池、Session 管理 |
| `models/` | 資料模型層 | ORM Mapping、關聯定義 |
| `schemas/` | 驗證層 | Pydantic 資料結構、型別檢查 |
| `services/` | 業務邏輯層 | CRUD 實作、規則運算 |
| `routers/` | 接口層 | HTTP 方法映射、權限驗證 |
| `templates/` | 視圖層 | HTML 模板、靜態資源 |

## 4. 資料庫設計

### 4.1 實體關聯圖 (ERD)
```
[Employee] 1 ──┬── * [AttendanceRecord]
              ├── * [LeaveRequest]
              └── * [OvertimeRequest]

[CalendarEvent] ──* [AttendanceRecord] (optional link)
[CalendarEvent] ──* [LeaveRequest] (optional link)
```

### 4.2 資料表結構

#### `employees` (員工表)
| 欄位 | 型別 | 說明 |
|------|------|------|
| id | INTEGER PK | 主鍵 |
| name | VARCHAR(150) | 姓名 |
| employee_code | VARCHAR(50) UK | 員工編號 |
| department | VARCHAR(100) | 部門 |
| position | VARCHAR(100) | 職位 |
| email | VARCHAR(150) UK | Email |
| phone | VARCHAR(30) | 電話 |
| status | ENUM | 狀態 (active/leave/resigned) |
| hire_date | DATE | 進用日期 |
| created_at/updated_at | DATETIME | 時間戳記 |

#### `attendance_records` (出勤紀錄表)
| 欄位 | 型別 | 說明 |
|------|------|------|
| id | INTEGER PK | 主鍵 |
| employee_id | FK → employees | 關聯員工 |
| check_date | DATE | 打卡日期 |
| clock_in_time | TIME | 上班打卡 |
| clock_out_time | TIME | 下班打卡 |
| status | ENUM | 狀態 (present/late/early_absent/absent) |
| notes | TEXT | 備註 |

#### `leave_requests` (請假申請表)
| 欄位 | 型別 | 說明 |
|------|------|------|
| id | INTEGER PK | 主鍵 |
| employee_id | FK → employees | 關聯員工 |
| leave_type | ENUM | 假別 (annual/personal/special/sick) |
| start_date/end_date | DATE | 假別日期區間 |
| reason | TEXT | 事由 |
| status | ENUM | 審核狀態 (pending/approved/rejected) |
| approved_by | INT | 核准人 |
| approved_at | DATETIME | 核准日期 |

#### `overtime_requests` (加班申請表)
| 欄位 | 型別 | 說明 |
|------|------|------|
| id | INTEGER PK | 主鍵 |
| employee_id | FK → employees | 關聯員工 |
| date | DATE | 加班日期 |
| start_time/end_time | TIME | 時段 |
| hours | DECIMAL(5,2) | 時數 |
| reason | TEXT | 事由 |
| status | ENUM | 狀態 (pending/approved/rejected) |

#### `calendar_events` (行事曆事件表)
| 欄位 | 型別 | 說明 |
|------|------|------|
| id | INTEGER PK | 主鍵 |
| event_date | DATE | 事件日期 |
| event_type | ENUM | 類型 (meeting/holiday/leave/overtime) |
| title | VARCHAR(255) | 標題 |
| description | TEXT | 描述 |
| location | VARCHAR(255) | 地點 |
| attendees | VARCHAR(500) | 參與人員 |
| is_imported | BOOLEAN | 是否為匯入資料 |

## 5. API 設計原則
- 使用 RESTful 風格 (GET/POST/PUT/DELETE)
- 統一回應格式：`{"code": 200, "message": "success", "data": {...}}`
- 分頁支援：`?page=1&per_page=20`
- 篩選支援：`?department=IT&status=active`
- 權限分級：Admin 可管理所有資料，一般員工僅能查看/申請個人資料

## 6. 安全性設計
- SQL 注入防護：SQLAlchemy ORM Parameterized Queries
- XSS 防護：Jinja2 Autoescape 預設開啟
- CSRF 防護：Form 表單搭配 Token 驗證
- 輸入驗證：Pydantic Strict Types + Regex

## 7. 延伸規劃
- [ ] 整合 LDAP/SSO 單點登入
- [ ] 增加 E-mail/Slack 通知機制
- [ ] 產出 PDF/Excel 報表匯出
- [ ] 支援多分公司/跨時區設定
- [ ] 增加 RBAC 權限管理模組

---
*本文檔由 Mavis 維護，最後更新 2026-05-20*
