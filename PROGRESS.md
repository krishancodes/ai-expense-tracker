# AI Expense Tracker — Build Progress

## Stack
- Frontend: React 18 + Vite + Tailwind CSS + Zustand + TanStack Query + React Router v6
- Backend: FastAPI + SQLAlchemy 2.0 + Alembic + SQLite (dev) / MySQL (prod)
- Auth: JWT (access token in memory, refresh token in HttpOnly cookie)
- Charts: Recharts
- Icons: Lucide React
- Forms: React Hook Form + Zod

## Status: IN PROGRESS

## Completed Tasks
- [X] 1. FastAPI project scaffold + folder structure
- [X] 2. Core config (app/core/config.py)
- [X] 3. Database connection (app/core/db.py)
- [X] 4. All 6 DB models (user, category, expense, budget, refresh_token, insight_cache)
- [X] 5. Alembic init + first migration
- [X] 6. Security utils (app/core/security.py)
- [X] 7. Auth dependency (app/dependencies.py)
- [X] 8. Auth endpoints (routers/auth.py + services/auth_service.py)
- [X] 9. Category endpoints (router + service)
- [X] 10. Expense endpoints (router + service)
- [X] 11. Budget endpoints (router + service)
- [X] 12. Dashboard summary endpoint (router + service)
- [X] 13. AI Insights endpoint (router + service + LLM call)
- [X] 14. Users endpoint (router + service)
- [X] 15. main.py (app init, CORS, router registration)

## In Progress
(none)

## Remaining (in order)
### Backend





### Frontend
- [ ] 16. Vite + React scaffold
- [ ] 17. Tailwind CSS setup
- [ ] 18. Folder structure + router setup
- [ ] 19. Axios client + interceptors
- [ ] 20. Zustand stores (authStore, uiStore)
- [ ] 21. Auth pages (Login, Register)
- [ ] 22. App shell (Sidebar, Navbar, layout)
- [ ] 23. shadcn/ui setup + base components
- [ ] 24. StatCard component
- [ ] 25. Dashboard page
- [ ] 26. ExpenseTable + FilterBar components
- [ ] 27. AddExpenseModal + EditExpenseModal
- [ ] 28. Expenses page
- [ ] 29. BudgetCard + ProgressBar components
- [ ] 30. Budgets page
- [ ] 31. InsightCard + Skeleton components
- [ ] 32. Insights page
- [ ] 33. Settings page
- [ ] 34. Mobile responsive (bottom nav, bottom sheets)

### Final
- [ ] 35. Git init + .gitignore + first commit
- [ ] 36. Deploy backend to Render
- [ ] 37. Deploy frontend to Vercel

## Important Decisions
- JWT access token: stored in Zustand memory (NOT localStorage)
- Refresh token: HttpOnly cookie set by backend
- DB dev: sqlite+aiosqlite:///./dev.db
- DB prod: mysql+aiomysql://
- AI model: OpenAI gpt-4o-mini (primary), Claude Haiku fallback
- LLM input: aggregated stats only, never raw transaction descriptions
- Insight cache: invalidated when expense added/edited/deleted for that month
- No TypeScript in v1.0 — plain JavaScript throughout frontend
- All 6 models use SQLAlchemy 2.0 style (Mapped, mapped_column, DeclarativeBase)
- PaymentMethod is a Python str enum: Cash, UPI, Card, NetBanking