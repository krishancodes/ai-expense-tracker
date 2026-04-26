---
title: PRD — AI Expense Tracker
version: 2.0
type: Product Requirements Document (Developer Edition)
stack: React + Zustand / FastAPI / SQLAlchemy + SQLite→MySQL
status: Final — Ready for Sprint Planning
date: April 2025
---

# AI Expense Tracker — Product Requirements Document
> Developer Edition v2.0 | Use this document for implementation and sprint planning.

Product Requirements Document  v2.0  Developer Edition

| **Stack** | **Audience** | **Status** | **Last Updated** |
| --- | --- | --- | --- |
| React + Zustand  /  FastAPI  /  SQLAlchemy + SQLite→MySQL | Engineering Team | Final — Ready for Sprint Planning | April 2025 |

## **Quick Reference**

| **Section** | **What You'll Find** |
| --- | --- |
| 1. Overview | Scope, out-of-scope, constraints |
| 2. Data Models | All DB tables with column specs |
| 3. API Contract | Every endpoint — method, path, auth, request, response, errors |
| 4. Feature Specs | Acceptance criteria per feature, no fluff |
| 5. Non-Functional Reqs | Hard numbers: perf, security, availability |
| 6. Tech Decisions | Stack choices, patterns, gotchas |
| 7. Success Metrics | KPIs that matter to engineering |

# **1. Overview**

## **1.1  What We're Building**

A web app for college students and young professionals to log expenses, track budgets, and receive AI-generated spending insights. Single-user, single-currency (v1.0).

## **1.2  Scope**

| **In Scope (v1.0)** | **Out of Scope (v1.0)** |
| --- | --- |
| JWT auth (email + password) | Bank/card API integration |
| Expense CRUD with categories | Native mobile apps |
| Monthly dashboard + charts | Multi-currency |
| Category & overall budgets with alerts | Shared / split expenses |
| AI insights panel (LLM API) | Tax features |
| User profile & preferences | Recurring expense automation |

## **1.3  Hard Constraints**

- **Frontend: **React (hooks only, no class components), Zustand for global state.

- **Backend: **FastAPI (Python 3.11+), async endpoints throughout.

- **ORM: **SQLAlchemy 2.0 with Alembic migrations. SQLite for dev, MySQL 8 for prod.

- **Auth: **JWT only — no OAuth/SSO in v1.0.

- **AI: **External LLM API call (OpenAI GPT-4o-mini primary, Claude Haiku fallback). No local model.

# **2. Data Models**

All tables include created_at DATETIME DEFAULT NOW() and updated_at DATETIME with ON UPDATE trigger unless noted.

## **2.1  users**

| **Column** | **Type** | **Constraints** | **Notes** |
| --- | --- | --- | --- |
| id | INT | PK, AUTO_INCREMENT |  |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Lowercase before insert |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt, cost=12 |
| full_name | VARCHAR(100) | NOT NULL |  |
| currency | CHAR(3) | DEFAULT "INR" | ISO 4217 |
| budget_reset_day | TINYINT | DEFAULT 1 | 1–28 |
| is_active | BOOLEAN | DEFAULT TRUE | Soft disable, not delete |

## **2.2  categories**

| **Column** | **Type** | **Constraints** | **Notes** |
| --- | --- | --- | --- |
| id | INT | PK, AUTO_INCREMENT |  |
| user_id | INT | FK → users.id, NULLABLE | NULL = system category |
| name | VARCHAR(50) | NOT NULL |  |
| icon | VARCHAR(10) |  | Emoji or icon slug |
| color | CHAR(7) |  | Hex color e.g. #3B82F6 |
| is_system | BOOLEAN | DEFAULT FALSE | System rows not deletable |

Seed 12 system categories on first migration: Food & Dining, Transport, Entertainment, Shopping, Health, Education, Housing, Utilities, Personal Care, Travel, Investments, Others.

## **2.3  expenses**

| **Column** | **Type** | **Constraints** | **Notes** |
| --- | --- | --- | --- |
| id | INT | PK, AUTO_INCREMENT |  |
| user_id | INT | FK → users.id, NOT NULL | Cascade delete |
| category_id | INT | FK → categories.id, NOT NULL |  |
| amount | DECIMAL(10,2) | NOT NULL, CHECK > 0 |  |
| date | DATE | NOT NULL | User-supplied, not server time |
| description | VARCHAR(200) | NULLABLE |  |
| payment_method | ENUM | NOT NULL | Cash │ UPI │ Card │ NetBanking |

Index: (user_id, date DESC) — primary query pattern.

## **2.4  budgets**

| **Column** | **Type** | **Constraints** | **Notes** |
| --- | --- | --- | --- |
| id | INT | PK, AUTO_INCREMENT |  |
| user_id | INT | FK → users.id, NOT NULL |  |
| category_id | INT | FK → categories.id, NULLABLE | NULL = overall budget |
| amount | DECIMAL(10,2) | NOT NULL, CHECK > 0 |  |
| month | TINYINT | NOT NULL | 1–12 |
| year | SMALLINT | NOT NULL |  |

Unique constraint: (user_id, category_id, month, year). NULL category_id counts as a distinct value in this constraint.

## **2.5  refresh_tokens**

| **Column** | **Type** | **Constraints** | **Notes** |
| --- | --- | --- | --- |
| id | INT | PK, AUTO_INCREMENT |  |
| user_id | INT | FK → users.id, NOT NULL | Cascade delete |
| token_hash | VARCHAR(255) | UNIQUE, NOT NULL | SHA-256 hash of raw token |
| expires_at | DATETIME | NOT NULL |  |
| revoked | BOOLEAN | DEFAULT FALSE |  |

Index on token_hash. Cron job or background task deletes rows where expires_at < NOW() daily.

## **2.6  insight_cache**

| **Column** | **Type** | **Constraints** | **Notes** |
| --- | --- | --- | --- |
| id | INT | PK, AUTO_INCREMENT |  |
| user_id | INT | FK → users.id, NOT NULL |  |
| month | TINYINT | NOT NULL |  |
| year | SMALLINT | NOT NULL |  |
| insights_json | TEXT | NOT NULL | Serialized JSON string |
| generated_at | DATETIME | NOT NULL |  |

Unique: (user_id, month, year). Invalidate (delete row) whenever a new expense is added for that user + month.

# **3. API Contract**

| Base URL: /api/v1 |
| --- |
| Auth: Bearer <access_token> in Authorization header for all protected routes. |
| Errors: { "detail": "string", "code": "ERROR_CODE" }  —  use standard HTTP status codes. |
| Pagination params: ?page=1&limit=20 (max limit=100). Response includes: { data: [], total, page, limit }. |

## **3.1  Auth  /auth**

| **Method** | **Path** | **Auth** | **Request Body** | **Success** | **Errors** |
| --- | --- | --- | --- | --- | --- |
| POST | /register | None | { email, password, full_name } | 201 { user, access_token, refresh_token } | 409 email exists, 422 validation |
| POST | /login | None | { email, password } | 200 { user, access_token, refresh_token } | 401 bad credentials, 423 account locked |
| POST | /refresh | Refresh token (cookie or body) | { refresh_token } | 200 { access_token, refresh_token } | 401 invalid/expired/revoked |
| POST | /logout | Bearer | { refresh_token } | 204 No Content | 401 |

Refresh token rotation: on /refresh, old token is revoked immediately. New pair issued.

Account lock: 5 consecutive failures → locked for 15 min. Track in Redis or a failed_attempts column on users.

## **3.2  Expenses  /expenses**

| **Method** | **Path** | **Auth** | **Notes** |
| --- | --- | --- | --- |
| GET | /expenses | Bearer | Filters: ?category_id, date_from, date_to, payment_method, search, page, limit, sort_by, order |
| POST | /expenses | Bearer | Body: { amount, category_id, date, description?, payment_method }. Invalidates insight_cache for that month. |
| GET | /expenses/{id} | Bearer | 404 if not owned by requesting user |
| PUT | /expenses/{id} | Bearer | Partial update OK. Re-invalidate cache if date or amount changed. |
| DELETE | /expenses/{id} | Bearer | 204. Cascade: invalidate insight_cache. |

## **3.3  Categories  /categories**

| **Method** | **Path** | **Auth** | **Notes** |
| --- | --- | --- | --- |
| GET | /categories | Bearer | Returns system categories + user's custom categories. |
| POST | /categories | Bearer | Body: { name, icon?, color? }. Max 20 custom categories per user. |
| PUT | /categories/{id} | Bearer | Only custom (user-owned) categories editable. 403 on system category. |
| DELETE | /categories/{id} | Bearer | 409 if category has linked expenses. 403 on system category. |

## **3.4  Budgets  /budgets**

| **Method** | **Path** | **Auth** | **Notes** |
| --- | --- | --- | --- |
| GET | /budgets | Bearer | Filters: ?month, year. Returns budgets + real-time spent amount per budget. |
| POST | /budgets | Bearer | Body: { category_id?, amount, month, year }. Upsert behavior — update if row exists. |
| DELETE | /budgets/{id} | Bearer | 204. |

GET /budgets response must include computed spent and utilization_pct per budget row. Calculate on the fly from expenses table.

## **3.5  Dashboard  /dashboard**

| **Method** | **Path** | **Auth** | **Response Fields** |
| --- | --- | --- | --- |
| GET | /dashboard/summary | Bearer | { total_spent, overall_budget, budget_remaining, utilization_pct, top_categories[{name,spent,pct}], monthly_trend[{month,year,total}x6], category_breakdown[{category,spent,budget,utilization_pct}] } |

Query param: ?month=&year= (default: current month). All computed server-side. No client-side aggregation.

## **3.6  AI Insights  /insights**

| **Method** | **Path** | **Auth** | **Notes** |
| --- | --- | --- | --- |
| GET | /insights | Bearer | Params: ?month, year. Returns cached insights if fresh (< 1 hr old AND no expense changes). Triggers LLM call if cache miss. |
| POST | /insights/regenerate | Bearer | Force-refresh: delete cache row, call LLM, return new insights. Rate-limited: 10 calls/hour/user. |

LLM input: aggregated stats only (category totals, day-of-week breakdown, prev month comparison). Never send raw transaction descriptions to LLM.

LLM output schema (enforce via system prompt + JSON mode):

{ "insights": [string], "anomalies": [string], "suggestions": [string], "confidence": float }

Graceful degradation: if LLM API errors, return 200 with { "insights": [], "error": "AI temporarily unavailable" }. Do not 500.

## **3.7  Users  /users**

| **Method** | **Path** | **Auth** | **Notes** |
| --- | --- | --- | --- |
| GET | /users/me | Bearer | Returns user profile + preferences |
| PUT | /users/me | Bearer | Updatable: full_name, currency, budget_reset_day |
| DELETE | /users/me | Bearer | Soft delete: set is_active=false. Schedule hard delete after 30 days. |

# **4. Feature Specs  (Acceptance Criteria)**

## **4.1  Authentication**

### **Registration**

- Accepts email (RFC 5322), password (min 8 chars, ≥1 uppercase, ≥1 digit), full_name.

- Normalizes email to lowercase before uniqueness check and storage.

- Returns 409 if email already registered.

- Issues access token (15-min TTL) + refresh token (7-day TTL) on success.

### **Login ****&**** Sessions**

- Returns 401 with same message for wrong email AND wrong password (no enumeration).

- Locks account for 15 min after 5 failed attempts — returns 423.

- Refresh token stored as SHA-256 hash in DB; raw token sent to client only.

- Logout revokes refresh token server-side; subsequent /refresh with same token returns 401.

## **4.2  Expense Management**

### **Create / Edit**

- Amount must be positive decimal, max 2 decimal places.

- Date is user-supplied (allow backdating up to 365 days; reject future dates).

- description is optional; strip leading/trailing whitespace before storage.

- Editing amount or date triggers insight_cache invalidation for the affected month.

### **List / Search**

- Default sort: date DESC, then created_at DESC.

- search param does case-insensitive LIKE match on description.

- All filters are combinable (AND logic).

- Response always includes category name and color alongside category_id.

## **4.3  Budget Tracking**

- A user may have one overall budget and one budget per category per month.

- POST /budgets upserts: if (user_id, category_id, month, year) exists, update amount.

- GET /budgets returns real-time utilization_pct = (sum of expenses for category in month) / budget amount × 100.

- Backend emits alert flags in the GET /budgets response: "alert_80": true when utilization_pct ≥ 80, "alert_100": true when ≥ 100.

- Frontend reads these flags and shows toast notifications. Do not rely on polling — check on every dashboard load and after each expense creation.

## **4.4  Dashboard**

- Single endpoint GET /dashboard/summary returns all data needed. No client-side aggregation.

- monthly_trend returns last 6 calendar months including current. Months with no expenses return total: 0.

- category_breakdown includes all categories that have either expenses OR a budget set for the month.

- All monetary values in the user's chosen currency (no conversion in v1.0 — display only).

## **4.5  AI Insights**

- Cache hit condition: insight_cache row for (user, month, year) exists AND generated_at > NOW() - 1hr AND no expense added/edited/deleted since generated_at.

- Insight response must always have 3–5 insights, 1–3 anomaly flags, and 2–4 suggestions.

- If LLM returns malformed JSON or omits required keys, retry once then return the degraded response.

- Rate limit 10 manual regenerations/hour/user via slowapi. Return 429 with Retry-After header.

- Loading state: endpoint should respond within 300ms if cached; frontend shows skeleton loader for live LLM calls.

# **5. Non-Functional Requirements**

| **Category** | **Requirement** | **Hard Target** |
| --- | --- | --- |
| Performance | API p95 latency (non-AI endpoints) | < 300 ms |
| Performance | Dashboard LCP | < 2.5 s |
| Performance | AI insight response (cache miss) | < 8 s  (show skeleton loader) |
| Performance | AI insight response (cache hit) | < 300 ms |
| Availability | Backend API uptime | 99.5% monthly |
| Scalability | Concurrent users (v1.0) | 500 simultaneous |
| Security | Passwords | bcrypt cost=12, never logged or returned |
| Security | Transport | TLS 1.2+ only, HSTS enabled |
| Security | CORS | Whitelist frontend origin only |
| Security | SQL injection | SQLAlchemy ORM — no raw string queries |
| Security | XSS | Pydantic strips input; React escapes output by default |
| Security | Secrets | .env only — never commit API keys |
| Reliability | LLM failure handling | Degrade gracefully, never 500 the dashboard |
| Reliability | DB backups | Daily automated backup, 7-day retention |
| Usability | Mobile responsiveness | Functional at viewport ≥ 360 px |
| Usability | Accessibility | WCAG 2.1 AA — keyboard nav, ARIA labels on charts |
| Maintainability | Backend test coverage | ≥ 80% (unit + integration) |
| Maintainability | API docs | FastAPI auto-generated /docs (OpenAPI 3.0) |
| Maintainability | DB migrations | Alembic only — no ad-hoc ALTER in prod |

# **6. Tech Decisions ****&**** Patterns**

## **6.1  Backend (FastAPI)**

- **Router structure: **/api/v1/auth, /expenses, /categories, /budgets, /dashboard, /insights, /users — one file per router.

- **Dependency injection: **Depends(get_db) for DB session, Depends(get_current_user) as auth guard on all protected routes.

- **Async: **All route handlers are async def. Use asyncio-compatible DB driver (aiomysql in prod, aiosqlite in dev).

- **Validation: **Pydantic v2 for all request/response schemas. Define separate Request and Response models — never expose ORM objects directly.

- **Background tasks: **Use FastAPI BackgroundTasks for LLM calls when pre-warming cache. Do not block the response.

- **Rate limiting: **slowapi with in-memory store for dev, Redis-backed for prod.

- **Error handling: **Single global exception handler converts all unhandled exceptions to { "detail": ..., "code": ... }.

## **6.2  Frontend (React + Zustand)**

### **Store Boundaries**

| **Store** | **State** | **Actions** |
| --- | --- | --- |
| authStore | user, accessToken, isAuthenticated | login, logout, refreshToken |
| expenseStore | expenses[], filters, pagination, isLoading | fetchExpenses, addExpense, updateExpense, deleteExpense |
| budgetStore | budgets[], alerts[] | fetchBudgets, setBudget, deleteBudget |
| uiStore | toasts[], modals{}, theme | addToast, openModal, closeModal |

- **Server state: **Use React Query (TanStack Query) for all API data fetching, caching, and background refresh. Zustand handles UI-only state.

- **Token refresh: **Axios interceptor — on 401, silently call /auth/refresh, update authStore, retry original request once.

- **Charts: **Recharts — pie/donut for categories, bar for monthly trend. Must be accessible (ARIA labels, keyboard tooltip).

- **Forms: **React Hook Form + Zod. All validation client-side first, then server errors mapped to field errors.

- **Code splitting: **Lazy-load: Dashboard, Insights, Settings. Eager-load: Login, Register, ExpenseList.

## **6.3  AI Integration**

### **Prompt Template (system prompt)**

| You are a personal finance analyst. Given monthly expense statistics, return ONLY a JSON object with this exact shape: |
| --- |
| { "insights": [string x3-5], "anomalies": [string x1-3], "suggestions": [string x2-4], "confidence": float 0-1 } |
| Be specific and data-driven. No preamble, no markdown, no explanation outside the JSON. |

### **Input to LLM (user message)**

| Send aggregated stats: { month, year, total_spent, category_totals: {}, prev_month_totals: {}, day_of_week_breakdown: {}, top_5_days: [] } |
| --- |
| NEVER send raw descriptions or transaction notes — privacy + token cost. |

### **Provider Priority**

- Primary: openai gpt-4o-mini (model="gpt-4o-mini", response_format={"type":"json_object"})

- Fallback: anthropic claude-haiku-4-5 with explicit JSON instruction in system prompt

- If both fail: return degraded 200 response (empty arrays, error field set)

## **6.4  Database**

- **Dev: **SQLite via aiosqlite. DATABASE_URL=sqlite+aiosqlite:///./dev.db

- **Prod: **MySQL 8 via aiomysql. DATABASE_URL=mysql+aiomysql://user:pass@host/db

- **Migrations: **alembic init, all schema changes via alembic revision --autogenerate. No manual ALTER TABLE in prod.

- **Session: **AsyncSession with expire_on_commit=False. Yield session in Depends(get_db), close on exit.

# **7. Success Metrics**

Metrics the engineering team owns or directly influences:

| **Metric** | **Target** | **How to Measure** |
| --- | --- | --- |
| API p95 latency (non-AI) | < 300 ms | FastAPI middleware timer → logs |
| API error rate (5xx) | < 0.5% | Error tracking (Sentry) |
| AI insight cache hit rate | > 70% | Log cache hits vs misses in app |
| Time to add expense (UI) | < 30 sec | Frontend perf event timing |
| Dashboard LCP | < 2.5 s | Lighthouse CI on PR merge |
| Test coverage (backend) | ≥ 80% | pytest-cov report in CI |
| Uptime | ≥ 99.5% / month | Uptime monitoring (UptimeRobot) |
| Activation rate | > 70% add ≥1 expense post-signup | DB query on cohorts |

# **Appendix**

## **A. Environment Variables**

| **Variable** | **Required** | **Example / Notes** |
| --- | --- | --- |
| DATABASE_URL | Yes | sqlite+aiosqlite:///./dev.db  or  mysql+aiomysql://... |
| SECRET_KEY | Yes | 256-bit random string — used to sign JWTs |
| ALGORITHM | Yes | "HS256" |
| ACCESS_TOKEN_EXPIRE_MINUTES | Yes | "15" |
| REFRESH_TOKEN_EXPIRE_DAYS | Yes | "7" |
| OPENAI_API_KEY | Yes | sk-... |
| ANTHROPIC_API_KEY | No | Fallback LLM provider |
| AI_RATE_LIMIT | No | Default: "10/hour" |
| FRONTEND_ORIGIN | Yes | "http://localhost:5173" or prod URL (CORS) |
| REDIS_URL | No | Required if using Redis-backed rate limiting in prod |

## **B. Project Structure**

| backend/ |
| --- |
| app/ |
| main.py              # FastAPI app init, CORS, middleware, router registration |
| dependencies.py      # get_db(), get_current_user() |
| models/              # SQLAlchemy ORM models (one file per table) |
| schemas/             # Pydantic request/response models |
| routers/             # auth.py, expenses.py, budgets.py, dashboard.py, insights.py, users.py |
| services/            # business logic layer (auth_service, expense_service, insight_service) |
| core/                # config.py (settings via pydantic-settings), security.py (JWT), db.py |
| alembic/               # migrations |
| tests/                 # pytest, mirrors app/ structure |
|  |
| frontend/ |
| src/ |
| stores/              # authStore.js, expenseStore.js, budgetStore.js, uiStore.js |
| pages/               # Login, Register, Dashboard, Expenses, Budgets, Settings |
| components/          # shared UI components |
| hooks/               # useExpenses, useBudgets, useInsights (React Query wrappers) |
| api/                 # axios instance + per-resource request functions |
| lib/                 # zod schemas, utils |

## **C. API Error Codes**

| **Code** | **HTTP** | **Meaning** |
| --- | --- | --- |
| AUTH_EMAIL_EXISTS | 409 | Email already registered |
| AUTH_INVALID_CREDENTIALS | 401 | Wrong email or password |
| AUTH_ACCOUNT_LOCKED | 423 | Too many failed attempts |
| AUTH_TOKEN_EXPIRED | 401 | Access token expired — use /refresh |
| AUTH_TOKEN_INVALID | 401 | Malformed or revoked token |
| EXPENSE_NOT_FOUND | 404 | Expense does not exist or not owned by user |
| EXPENSE_FUTURE_DATE | 422 | Date is in the future |
| CATEGORY_NOT_FOUND | 404 |  |
| CATEGORY_SYSTEM_READONLY | 403 | Cannot modify system category |
| CATEGORY_HAS_EXPENSES | 409 | Cannot delete category with linked expenses |
| BUDGET_CONFLICT | 409 | Budget for this category/month already exists (should upsert, not error) |
| INSIGHT_RATE_LIMITED | 429 | Too many regeneration requests |
| AI_UNAVAILABLE | 200 | LLM call failed — degraded response returned, not an error |

## **D. Expense Category Seed Data**

| **name** | **icon** | **color** |
| --- | --- | --- |
| Food & Dining | 🍽️ | #F59E0B |
| Transport | 🚗 | #3B82F6 |
| Entertainment | 🎬 | #8B5CF6 |
| Shopping | 🛍️ | #EC4899 |
| Health & Medical | 🏥 | #10B981 |
| Education | 📚 | #06B6D4 |
| Housing | 🏠 | #6366F1 |
| Utilities | 💡 | #F97316 |
| Personal Care | 💆 | #14B8A6 |
| Travel | ✈️ | #0EA5E9 |
| Investments | 📈 | #22C55E |
| Others | 📦 | #9CA3AF |

AI Expense Tracker  —  Dev PRD v2.0  —  For Internal Engineering Use

AI Expense Tracker — Dev PRD v2.0  |  Page