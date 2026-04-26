---
title: TECHSTACK — AI Expense Tracker
version: 1.0
type: Technology Stack Document
frontend: React 18 + Vite + Tailwind CSS + Zustand + TanStack Query
backend: FastAPI + SQLAlchemy 2.0 + Alembic + MySQL
deployment: Vercel (frontend) + Render (backend) + Railway (MySQL)
date: April 2025
---

# AI Expense Tracker — Tech Stack Document
> Practical, developer-focused. Every decision includes justification and the exact package to install.

AI Expense Tracker  —  Technology Stack Document

| **Field** | **Value** |
| --- | --- |
| Project | AI Expense Tracker |
| Audience | Engineers, contributors, and code-generation tools (e.g. Antigravity) |
| Status | Finalised — v1.0  │  April 2025 |
| Depends on | PRD (Dev Edition v2.0), DESIGN.md v1.0 |

## **Document Contents**

| **§** | **Section** |
| --- | --- |
| 1 | Full Stack at a Glance — one-page summary table |
| 2 | Frontend Stack — React, Tailwind, libraries, justification |
| 3 | Backend Stack — FastAPI, Python libs, project conventions |
| 4 | Database — SQLAlchemy, SQLite/MySQL, Alembic migrations |
| 5 | State Management — Zustand + TanStack Query split |
| 6 | API Communication — Axios instance, interceptors, patterns |
| 7 | Charts & Visualisation — Recharts setup and config |
| 8 | Authentication — JWT flow, token storage, refresh strategy |
| 9 | Deployment — Render + Vercel, env vars, CI/CD outline |
| 10 | Folder Structure — complete frontend + backend tree |

# **1. Full Stack at a Glance**

| **Layer** | **Technology** | **Version** | **Role** |
| --- | --- | --- | --- |
| UI Framework | React | ^18.3 | Component tree, rendering |
| Language | JavaScript (ES2022) | — | No TypeScript in v1.0 to keep onboarding fast |
| Styling | Tailwind CSS | ^3.4 | Utility-first, design tokens from DESIGN.md |
| Component Base | shadcn/ui | latest | Accessible, unstyled primitives |
| State (server) | TanStack Query | ^5 | API data, caching, background refetch |
| State (client) | Zustand | ^4 | Auth tokens, UI state, toasts |
| Forms | React Hook Form | ^7 | Form state + validation |
| Validation | Zod | ^3 | Schema validation, shared with API shapes |
| Charts | Recharts | ^2.12 | Bar, Donut, RadialBar charts |
| Icons | Lucide React | ^0.383 | SVG icon set |
| HTTP Client | Axios | ^1.7 | API calls + interceptors |
| Routing | React Router | ^6 | Client-side routing, route guards |
| API Framework | FastAPI | ^0.111 | Async REST API, auto OpenAPI docs |
| Language | Python | 3.11+ |  |
| ORM | SQLAlchemy | ^2.0 | Async ORM, model definitions |
| Migrations | Alembic | ^1.13 | Schema versioning |
| Validation | Pydantic v2 | ^2.7 | Request/response schemas |
| Auth | python-jose + bcrypt | — | JWT signing, password hashing |
| Rate Limiting | slowapi | ^0.1 | Per-user rate limits on AI endpoints |
| DB (dev) | SQLite | — | Zero-config local dev |
| DB (prod) | MySQL 8 | 8.0+ | Managed instance on Railway/PlanetScale |
| Async DB driver | aiosqlite / aiomysql | — | Matches SQLite/MySQL env |
| Frontend host | Vercel | — | Free tier, auto-deploy from GitHub |
| Backend host | Render | — | Free tier web service, auto-deploy |
| AI Provider | OpenAI (gpt-4o-mini) | — | LLM insights. Claude Haiku as fallback |
| CI/CD | GitHub Actions | — | Lint + test on PR, deploy on merge to main |

# **2. Frontend Stack**

## **2.1  Core**

| **Package** | **npm install** | **Why this, not the alternative** |
| --- | --- | --- |
| React 18 | react react-dom | Hooks-only. Concurrent features (Suspense) for skeleton loading states on AI panel. |
| Vite | vite @vitejs/plugin-react | Faster HMR than CRA. < 300ms cold start in dev. Simple config. |
| React Router v6 | react-router-dom | File-based mental model via createBrowserRouter. Loaders handle auth redirects cleanly. |
| Tailwind CSS 3 | tailwindcss postcss autoprefixer | No runtime CSS overhead. Design tokens map 1-to-1 with DESIGN.md. JIT mode only generates classes you use. |
| shadcn/ui | npx shadcn-ui@latest init | Copy-into-project model means no version lock-in. Radix primitives give ARIA/keyboard behaviour for free. |

## **2.2  Forms ****&**** Validation**

| **Package** | **npm install** | **Usage** |
| --- | --- | --- |
| React Hook Form | react-hook-form | Uncontrolled inputs = zero re-renders on keystroke. register() pattern. handleSubmit wraps async POST. |
| Zod | zod | Define schema once; use for both client validation and documenting the shape of API request bodies. |
| @hookform/resolvers | @hookform/resolvers | Bridges Zod schema into RHF resolver. One line: resolver: zodResolver(schema). |

## **2.3  UI Utilities**

| **Package** | **npm install** | **Usage** |
| --- | --- | --- |
| clsx | clsx | Conditional className merging. Use everywhere instead of template literals. |
| tailwind-merge | tailwind-merge | Resolves Tailwind class conflicts (e.g. p-4 + p-6 → p-6). Wrap with clsx: cn() helper. |
| class-variance-authority | class-variance-authority | Variant-based component classes (Button variants: primary/secondary/ghost/danger). |
| Lucide React | lucide-react | ~1000 SVG icons as React components. Pass size and strokeWidth props. Tree-shaken. |
| date-fns | date-fns | Date formatting (format, parseISO, startOfMonth). Lighter than moment/dayjs for what we need. |

## **2.4  Install Script**

| # 1. Scaffold |
| --- |
| npm create vite@latest ai-expense-tracker -- --template react |
| cd ai-expense-tracker |
|  |
| # 2. Tailwind |
| npm install -D tailwindcss postcss autoprefixer |
| npx tailwindcss init -p |
|  |
| # 3. Core deps |
| npm install react-router-dom axios zustand @tanstack/react-query |
| npm install react-hook-form zod @hookform/resolvers |
| npm install recharts lucide-react date-fns |
| npm install clsx tailwind-merge class-variance-authority |
|  |
| # 4. shadcn/ui |
| npx shadcn-ui@latest init |
| # Add components as needed: |
| npx shadcn-ui@latest add button input select dialog toast |

# **3. Backend Stack**

## **3.1  Core**

| **Package** | **pip install** | **Why** |
| --- | --- | --- |
| FastAPI | fastapi | Async-native. Auto OpenAPI docs at /docs. Pydantic integration built-in. Best DX for Python APIs in 2025. |
| Uvicorn | uvicorn[standard] | ASGI server. --reload in dev, --workers 2 in prod on Render free tier. |
| Pydantic v2 | pydantic | Faster than v1 (Rust core). Strict mode catches bad data at the boundary. Powers FastAPI schemas. |
| pydantic-settings | pydantic-settings | Loads .env into a typed Settings class. Single source of truth for all env vars. |
| python-dotenv | python-dotenv | Loads .env in dev. Pydantic-settings uses it automatically. |

## **3.2  Database ****&**** ORM**

| **Package** | **pip install** | **Why** |
| --- | --- | --- |
| SQLAlchemy 2.0 | sqlalchemy | 2.0 style (select(), session.execute()) is cleaner and async-compatible. Avoid legacy 1.x patterns. |
| Alembic | alembic | Auto-generates migration scripts from model changes. Run: alembic revision --autogenerate -m "desc". |
| aiosqlite | aiosqlite | Async driver for SQLite (dev). Drop-in, no config change needed. |
| aiomysql | aiomysql | Async driver for MySQL 8 (prod). Switch by changing DATABASE_URL only. |
| greenlet | greenlet | Required by SQLAlchemy async mode. Install alongside sqlalchemy. |

## **3.3  Auth ****&**** Security**

| **Package** | **pip install** | **Usage** |
| --- | --- | --- |
| python-jose[cryptography] | python-jose[cryptography] | JWT encode/decode. Algorithm: HS256. Tokens signed with SECRET_KEY from env. |
| passlib[bcrypt] | passlib[bcrypt] | Password hashing. CryptContext(schemes=["bcrypt"], deprecated="auto"). Cost factor 12. |
| slowapi | slowapi | Rate limiting via Limiter. Attach to FastAPI app. Limit AI regenerate endpoint to 10/hour/user. |

## **3.4  Dev Tools**

| **Package** | **pip install** | **Usage** |
| --- | --- | --- |
| pytest | pytest pytest-asyncio httpx | Test suite. httpx AsyncClient hits FastAPI without a real server. |
| pytest-cov | pytest-cov | Coverage report. Target: 80%+. Run: pytest --cov=app --cov-report=term. |
| ruff | ruff | Linter + formatter in one. Replaces flake8 + black. Fast. Add to pre-commit. |
| pre-commit | pre-commit | Runs ruff on staged files before every commit. Config: .pre-commit-config.yaml. |

## **3.5  requirements.txt**

| fastapi>=0.111.0 |
| --- |
| uvicorn[standard]>=0.29.0 |
| pydantic>=2.7.0 |
| pydantic-settings>=2.2.0 |
| python-dotenv>=1.0.0 |
| sqlalchemy>=2.0.29 |
| alembic>=1.13.0 |
| aiosqlite>=0.20.0        # dev |
| aiomysql>=0.2.0          # prod |
| greenlet>=3.0.0 |
| python-jose[cryptography]>=3.3.0 |
| passlib[bcrypt]>=1.7.4 |
| slowapi>=0.1.9 |
| httpx>=0.27.0            # test client |
| pytest>=8.1.0 |
| pytest-asyncio>=0.23.0 |
| pytest-cov>=5.0.0 |
| ruff>=0.4.0 |

# **4. Database**

## **4.1  Environment Strategy**

| **Environment** | **Engine** | **DATABASE_URL format** | **Why** |
| --- | --- | --- | --- |
| Dev (local) | SQLite | sqlite+aiosqlite:///./dev.db | Zero setup. File lives in project root. .gitignore it. |
| Test (CI) | SQLite | sqlite+aiosqlite:///./test.db | Fast, isolated. Each test run gets a fresh db via scope="session" fixture. |
| Production | MySQL 8 | mysql+aiomysql://user:pass@host:3306/expensedb | Managed on Railway (free) or PlanetScale serverless. SSL enforced. |

## **4.2  SQLAlchemy Setup Pattern**

| # app/core/db.py |
| --- |
| from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker |
| from app.core.config import settings |
|  |
| engine = create_async_engine(settings.DATABASE_URL, echo=False) |
| AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False) |
|  |
| async def get_db(): |
| async with AsyncSessionLocal() as session: |
| yield session |

## **4.3  Migration Workflow**

| **Command** | **When to run** |
| --- | --- |
| alembic init alembic | Once, during project setup |
| alembic revision --autogenerate -m "add users" | After every model change |
| alembic upgrade head | Before starting the dev server + in CI before tests |
| alembic downgrade -1 | To rollback last migration locally |
| alembic history | To inspect migration chain |

- **Rule: **Never ALTER TABLE manually in prod. Always go through Alembic.

- **CI: **Run alembic upgrade head as a step before pytest in GitHub Actions.

# **5. State Management**

Two separate tools with a clear division of responsibility. Do not mix them.

## **5.1  Division of Responsibility**

| **State Type** | **Tool** | **Examples** |
| --- | --- | --- |
| Server state (async, cached) | TanStack Query (React Query v5) | Expenses list, budgets, dashboard summary, AI insights |
| Client / UI state | Zustand | Auth tokens, current user, toast queue, open modals, sidebar collapse |
| Form state | React Hook Form | All form fields, validation errors, submit status |
| URL state | React Router searchParams | Active filters (date range, category, page number) — survives page refresh |

## **5.2  Zustand Stores**

| // src/stores/authStore.js |
| --- |
| export const useAuthStore = create((set) => ({ |
| user: null, |
| accessToken: null, |
| setAuth: (user, token) => set({ user, accessToken: token }), |
| clearAuth: () => set({ user: null, accessToken: null }), |
| })) |
|  |
| // src/stores/uiStore.js |
| export const useUIStore = create((set) => ({ |
| toasts: [], |
| addToast: (toast) => set((s) => ({ toasts: [...s.toasts, toast] })), |
| removeToast: (id) => set((s) => ({ toasts: s.toasts.filter(t => t.id !== id) })), |
| sidebarOpen: false, |
| toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })), |
| })) |

## **5.3  TanStack Query Keys Convention**

| **Query Key** | **Endpoint** | **Stale Time** |
| --- | --- | --- |
| ['expenses', filters] | GET /expenses | 30 seconds — user edits frequently |
| ['budgets', month, year] | GET /budgets | 1 minute |
| ['dashboard', month, year] | GET /dashboard/summary | 1 minute |
| ['insights', month, year] | GET /insights | 1 hour — matches backend cache TTL |
| ['categories'] | GET /categories | Infinity — rarely changes |
| ['user', 'me'] | GET /users/me | 5 minutes |

- **Invalidation: **After POST/PUT/DELETE /expenses, call queryClient.invalidateQueries({ queryKey: ['expenses'] }) and ['dashboard'].

# **6. API Communication**

## **6.1  Axios Instance**

| // src/api/client.js |
| --- |
| import axios from 'axios' |
| import { useAuthStore } from '@/stores/authStore' |
|  |
| const api = axios.create({ |
| baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1', |
| timeout: 15000, |
| }) |
|  |
| // REQUEST: attach token |
| api.interceptors.request.use((config) => { |
| const token = useAuthStore.getState().accessToken |
| if (token) config.headers.Authorization = `Bearer ${token}` |
| return config |
| }) |
|  |
| // RESPONSE: silent refresh on 401 |
| api.interceptors.response.use( |
| (res) => res, |
| async (err) => { |
| const orig = err.config |
| if (err.response?.status === 401 && !orig._retry) { |
| orig._retry = true |
| const { data } = await axios.post('/api/v1/auth/refresh', { |
| refresh_token: getCookie('refresh_token'), |
| }) |
| useAuthStore.getState().setAuth(data.user, data.access_token) |
| orig.headers.Authorization = `Bearer ${data.access_token}` |
| return api(orig) |
| } |
| if (err.response?.status === 401) useAuthStore.getState().clearAuth() |
| return Promise.reject(err) |
| } |
| ) |
|  |
| export default api |

## **6.2  Per-Resource API Files**

| **File** | **Exports** | **Consumed by** |
| --- | --- | --- |
| src/api/expenses.js | getExpenses(filters), createExpense(data), updateExpense(id,data), deleteExpense(id) | useExpenses, AddExpenseModal |
| src/api/budgets.js | getBudgets(month,year), setBudget(data), deleteBudget(id) | useBudgets, BudgetPage |
| src/api/dashboard.js | getDashboardSummary(month,year) | useDashboard, DashboardPage |
| src/api/insights.js | getInsights(month,year), regenerateInsights(month,year) | useInsights, InsightsPage |
| src/api/auth.js | login(creds), register(data), refresh(token), logout(token) | authStore, Login/Register pages |
| src/api/users.js | getMe(), updateMe(data) | useUser, SettingsPage |

## **6.3  Error Handling Pattern**

| // In React Query mutations |
| --- |
| const mutation = useMutation({ |
| mutationFn: createExpense, |
| onSuccess: () => { |
| queryClient.invalidateQueries({ queryKey: ['expenses'] }) |
| queryClient.invalidateQueries({ queryKey: ['dashboard'] }) |
| addToast({ type: 'success', message: 'Expense added' }) |
| }, |
| onError: (err) => { |
| const msg = err.response?.data?.detail ?? 'Something went wrong' |
| addToast({ type: 'error', message: msg }) |
| }, |
| }) |

# **7. Charts ****&**** Visualisation**

All charts use Recharts wrapped in ResponsiveContainer so they fill their card width. No fixed pixel widths.

| **Chart** | **Component** | **Key Config** |
| --- | --- | --- |
| Monthly Spend Trend | BarChart | data: last 6 months. Bar fill="#6366F1". Rounded top corners: radius={[4,4,0,0]}. No vertical gridlines. Tooltip formatted as currency. |
| Category Breakdown | PieChart | PieChart > Pie > Cell. innerRadius=60, outerRadius=90 (donut). Legend below with category name + amount + %. Custom label line. |
| Overall Budget Gauge | RadialBarChart | Single RadialBar. startAngle=180, endAngle=0. Fill changes: green <80%, amber 80–99%, red ≥100%. Center label shows "X% used". |
| Budget Progress Bars | Native div | Custom: bg-slate-100 track div, colored fill div with transition-all duration-700. No library needed. Amber >80%, red >100%. |

## **7.1  Recharts Tips**

- **Always wrap: **Use <ResponsiveContainer width="100%" height={240}> — never set width/height on the chart directly.

- **Tooltip formatter: **formatter={(value) => [`₹${value.toLocaleString('en-IN')}`, 'Amount']}

- **Custom colours: **Pass COLORS array from your design tokens. Map with <Cell key={i} fill={COLORS[i % COLORS.length]} />.

- **Animation: **Disable on re-renders with isAnimationActive={false} after first mount to prevent flicker on React Query refetch.

- **Accessibility: **Add aria-label to the ResponsiveContainer div wrapper. Provide a sr-only <table> with the same data below the chart.

# **8. Authentication**

## **8.1  Token Strategy**

| **Token** | **Storage** | **TTL** | **Sent via** |
| --- | --- | --- | --- |
| Access token | Zustand authStore (memory only — NOT localStorage) | 15 minutes | Authorization: Bearer header on every API request |
| Refresh token | HttpOnly cookie (set by backend Set-Cookie) | 7 days | Automatically sent by browser on POST /auth/refresh |

- **Why memory for access token: **Immune to XSS attacks. Tab close clears it. Axios interceptor handles silent refresh.

- **Why HttpOnly cookie for refresh: **JS cannot read it, so XSS cannot steal it. CSRF risk is mitigated because /auth/refresh only accepts the token, not a state-changing operation.

## **8.2  Backend JWT Implementation**

| # app/core/security.py |
| --- |
| from jose import jwt |
| from passlib.context import CryptContext |
| from datetime import datetime, timedelta, timezone |
| from app.core.config import settings |
|  |
| pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") |
|  |
| def hash_password(plain: str) -> str: |
| return pwd_context.hash(plain) |
|  |
| def verify_password(plain: str, hashed: str) -> bool: |
| return pwd_context.verify(plain, hashed) |
|  |
| def create_access_token(sub: str) -> str: |
| expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) |
| return jwt.encode({"sub": sub, "exp": expire}, settings.SECRET_KEY, algorithm=settings.ALGORITHM) |
|  |
| def decode_token(token: str) -> dict: |
| return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]) |

## **8.3  Auth Dependency (FastAPI)**

| # app/dependencies.py |
| --- |
| from fastapi import Depends, HTTPException, status |
| from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials |
|  |
| bearer = HTTPBearer() |
|  |
| async def get_current_user( |
| credentials: HTTPAuthorizationCredentials = Depends(bearer), |
| db: AsyncSession = Depends(get_db), |
| ) -> User: |
| try: |
| payload = decode_token(credentials.credentials) |
| user = await db.get(User, int(payload["sub"])) |
| except Exception: |
| raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) |
| if not user or not user.is_active: |
| raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) |
| return user |

## **8.4  Frontend Route Guard**

| // src/router.jsx  — React Router v6 loader pattern |
| --- |
| const protectedLoader = () => { |
| const token = useAuthStore.getState().accessToken |
| if (!token) return redirect("/login") |
| return null |
| } |
|  |
| const router = createBrowserRouter([ |
| { path: "/login",     element: <LoginPage /> }, |
| { path: "/register",  element: <RegisterPage /> }, |
| { |
| element: <AppShell />, |
| loader: protectedLoader, |
| children: [ |
| { path: "/dashboard",  element: <DashboardPage /> }, |
| { path: "/expenses",   element: <ExpensesPage /> }, |
| { path: "/budgets",    element: <BudgetsPage /> }, |
| { path: "/insights",   element: <InsightsPage /> }, |
| { path: "/settings",   element: <SettingsPage /> }, |
| ], |
| }, |
| ]) |

# **9. Deployment Strategy**

## **9.1  Hosting Targets**

| **Service** | **What it hosts** | **Plan** | **Notes** |
| --- | --- | --- | --- |
| Vercel | React frontend (Vite build) | Hobby (free) | Auto-deploy on push to main. Set VITE_API_URL env var in Vercel dashboard. |
| Render | FastAPI backend (Uvicorn) | Free web service | Set all .env vars in Render Environment. Build: pip install -r requirements.txt. Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT. |
| Railway | MySQL 8 database | Starter (free $5 credit/mo) | Provision MySQL plugin. Copy DATABASE_URL into Render env vars. Enable SSL. |
| GitHub | Code + CI/CD | Free | Push triggers GitHub Actions. Actions deploy to Vercel/Render via CLI or webhooks. |

## **9.2  Environment Variables**

| **Variable** | **Where set** | **Example** |
| --- | --- | --- |
| DATABASE_URL | Render + local .env | mysql+aiomysql://user:pass@host/expensedb |
| SECRET_KEY | Render | 64-char random hex string |
| ALGORITHM | Render | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Render | 15 |
| REFRESH_TOKEN_EXPIRE_DAYS | Render | 7 |
| OPENAI_API_KEY | Render | sk-... |
| ANTHROPIC_API_KEY | Render (optional) | sk-ant-... |
| FRONTEND_ORIGIN | Render | https://your-app.vercel.app |
| VITE_API_URL | Vercel | https://your-api.onrender.com/api/v1 |

## **9.3  GitHub Actions CI/CD**

| # .github/workflows/ci.yml |
| --- |
| on: [push, pull_request] |
|  |
| jobs: |
| backend: |
| runs-on: ubuntu-latest |
| steps: |
| - uses: actions/checkout@v4 |
| - uses: actions/setup-python@v5 |
| with: { python-version: "3.11" } |
| - run: pip install -r requirements.txt |
| - run: alembic upgrade head |
| - run: pytest --cov=app --cov-fail-under=80 |
| - run: ruff check app/ |
|  |
| frontend: |
| runs-on: ubuntu-latest |
| steps: |
| - uses: actions/checkout@v4 |
| - uses: actions/setup-node@v4 |
| with: { node-version: "20" } |
| - run: npm ci |
| - run: npm run build   # fails on type/lint errors if configured |

## **9.4  Local Dev Setup (First-time)**

| # Backend |
| --- |
| cd backend |
| python -m venv .venv && source .venv/bin/activate |
| pip install -r requirements.txt |
| cp .env.example .env          # fill in values |
| alembic upgrade head |
| uvicorn app.main:app --reload |
|  |
| # Frontend (separate terminal) |
| cd frontend |
| npm install |
| cp .env.example .env.local    # set VITE_API_URL=http://localhost:8000/api/v1 |
| npm run dev |
|  |
| # Visit: http://localhost:5173  (frontend) |
| # API docs: http://localhost:8000/docs |

# **10. Folder Structure**

## **10.1  Repository Root**

| ai-expense-tracker/ |
| --- |
| ├── frontend/                  # Vite + React app |
| ├── backend/                   # FastAPI app |
| ├── .github/workflows/         # CI/CD |
| ├── .gitignore |
| └── README.md |

## **10.2  Frontend**

| frontend/ |
| --- |
| ├── public/ |
| ├── src/ |
| │   ├── api/                   # Axios functions (one file per resource) |
| │   │   ├── client.js          # Axios instance + interceptors |
| │   │   ├── auth.js |
| │   │   ├── expenses.js |
| │   │   ├── budgets.js |
| │   │   ├── dashboard.js |
| │   │   ├── insights.js |
| │   │   └── users.js |
| │   ├── components/ |
| │   │   ├── ui/                # Primitives: Button, Input, Badge, Card, Modal, Toast |
| │   │   ├── layout/            # AppShell, Sidebar, Navbar, BottomNav, PageHeader |
| │   │   ├── dashboard/         # StatCard, MonthlyBarChart, CategoryDonutChart, RecentTable |
| │   │   ├── expenses/          # ExpenseTable, AddExpenseModal, EditExpenseModal, FilterBar |
| │   │   ├── budgets/           # BudgetGrid, BudgetCard, BudgetProgressBar, OverallGauge |
| │   │   ├── insights/          # InsightCard, AnomalyAlert, SuggestionCard, InsightSkeleton |
| │   │   └── shared/            # EmptyState, ConfirmModal, CategoryBadge, SkeletonLoader |
| │   ├── hooks/                 # React Query wrappers (useExpenses, useBudgets, useInsights…) |
| │   ├── pages/                 # One file per route |
| │   │   ├── Login.jsx |
| │   │   ├── Register.jsx |
| │   │   ├── Dashboard.jsx |
| │   │   ├── Expenses.jsx |
| │   │   ├── Budgets.jsx |
| │   │   ├── Insights.jsx |
| │   │   ├── Settings.jsx |
| │   │   └── NotFound.jsx |
| │   ├── stores/                # Zustand stores |
| │   │   ├── authStore.js |
| │   │   └── uiStore.js |
| │   ├── lib/                   # Helpers: cn(), formatCurrency(), date helpers |
| │   ├── router.jsx             # createBrowserRouter + protected loader |
| │   ├── main.jsx               # ReactDOM.createRoot, QueryClientProvider, RouterProvider |
| │   └── index.css              # Tailwind @tailwind directives only |
| ├── .env.example |
| ├── index.html |
| ├── tailwind.config.js |
| ├── vite.config.js |
| └── package.json |

## **10.3  Backend**

| backend/ |
| --- |
| ├── app/ |
| │   ├── main.py                # FastAPI() init, CORS, router registration, lifespan |
| │   ├── dependencies.py        # get_db(), get_current_user() |
| │   ├── core/ |
| │   │   ├── config.py          # Settings (pydantic-settings), reads .env |
| │   │   ├── db.py              # engine, AsyncSessionLocal, get_db() |
| │   │   └── security.py        # hash_password, verify_password, create/decode_token |
| │   ├── models/                # SQLAlchemy ORM models (one file per table) |
| │   │   ├── user.py |
| │   │   ├── expense.py |
| │   │   ├── category.py |
| │   │   ├── budget.py |
| │   │   ├── refresh_token.py |
| │   │   └── insight_cache.py |
| │   ├── schemas/               # Pydantic request + response models |
| │   │   ├── auth.py |
| │   │   ├── expense.py |
| │   │   ├── budget.py |
| │   │   ├── dashboard.py |
| │   │   ├── insight.py |
| │   │   └── user.py |
| │   ├── routers/               # One file per resource group |
| │   │   ├── auth.py            # /auth endpoints |
| │   │   ├── expenses.py        # /expenses endpoints |
| │   │   ├── categories.py |
| │   │   ├── budgets.py |
| │   │   ├── dashboard.py |
| │   │   ├── insights.py |
| │   │   └── users.py |
| │   └── services/              # Business logic (no DB calls in routers) |
| │       ├── auth_service.py |
| │       ├── expense_service.py |
| │       ├── budget_service.py |
| │       ├── dashboard_service.py |
| │       └── insight_service.py # LLM call, cache read/write, prompt building |
| ├── alembic/                   # Migration scripts |
| │   ├── env.py |
| │   └── versions/ |
| ├── tests/ |
| │   ├── conftest.py            # AsyncClient fixture, test DB setup |
| │   ├── test_auth.py |
| │   ├── test_expenses.py |
| │   ├── test_budgets.py |
| │   └── test_insights.py |
| ├── .env.example |
| ├── alembic.ini |
| ├── requirements.txt |
| └── ruff.toml |

# **Appendix**

## **A. Why Not These Alternatives**

| **Alternative** | **Rejected in favour of** | **Reason** |
| --- | --- | --- |
| Next.js | Vite + React Router | No SSR/SSG needed. Dashboard is fully client-rendered behind auth. Next adds complexity (server components, app router) with no benefit here. |
| TypeScript | JavaScript (v1.0) | Faster to build in v1.0. Zod schemas document types at runtime boundaries. Add TS in v2.0 when the team is stable. |
| Redux Toolkit | Zustand | RTK is powerful but verbose for this scale. Zustand is 1kb, zero boilerplate, and does everything we need. |
| SWR | TanStack Query | TanStack Query has better mutation support, optimistic updates, and window-focus refetch out of the box. |
| Django REST | FastAPI | FastAPI is async-native, auto-generates OpenAPI docs, and Pydantic v2 is significantly faster than DRF serializers. |
| PostgreSQL | MySQL 8 | Both work equally well. MySQL chosen because Railway and PlanetScale offer better free tiers for MySQL vs Postgres. |
| Chart.js | Recharts | Recharts is React-native (no useEffect + canvas imperative code). Better integration with React state and data flow. |
| localStorage | Memory (Zustand) | localStorage is vulnerable to XSS. Access tokens in memory + HttpOnly cookie for refresh is the standard secure pattern. |

## **B. Key Developer Conventions**

- **No raw SQL: **Use SQLAlchemy ORM select() statements only. Never f-string a query.

- **No class components: **React hooks only throughout the frontend.

- **No direct fetch(): **All HTTP through the Axios client.js instance so interceptors always run.

- **No logic in routers: **FastAPI router files call service functions only. All business logic lives in services/.

- **No secrets in code: **All config via pydantic-settings + .env. CI injects secrets from GitHub Secrets.

- **One component per file: **No barrel re-exports in components. Import directly from the file path.

## **C. Version Lock Summary**

| **Package** | **Pinned version** | **Breaking change risk if upgraded** |
| --- | --- | --- |
| React | 18.3.x | React 19 changes ref API + form actions — wait for ecosystem |
| TanStack Query | 5.x | v5 broke v4 API significantly. Do not mix versions. |
| SQLAlchemy | 2.0.x | 2.0 style is incompatible with 1.x patterns |
| Pydantic | 2.x | v2 validators syntax differs from v1. Do not use v1 patterns. |
| React Router | 6.x | v6 data APIs (loader/action) differ from v5. Pick one style. |
| shadcn/ui | latest | Copy-paste model — no version. Regenerate components manually if needed. |

AI Expense Tracker  —  TECHSTACK.md v1.0  —  For Engineering Use

AI Expense Tracker — TECHSTACK.md  |  Page