---
title: DESIGN — AI Expense Tracker
version: 1.0
type: UI/UX Design Document
stack: React 18 + Tailwind CSS 3 + shadcn/ui + Recharts
aesthetic: Dark sidebar, light content area, indigo/violet accent, card-based
date: April 2025
---

# AI Expense Tracker — Design Document
> Inspiration: Dribbble Personal Finance Dashboard. Implement with React + Tailwind CSS.

AI Expense Tracker  —  UI/UX Design Document

| **Field** | **Value** |
| --- | --- |
| Design Inspiration | Dribbble — Personal Finance Expense Tracker Dashboard |
| Aesthetic | Dark sidebar + light content area, indigo/violet accent, card-based |
| Frontend Stack | React 18 + Tailwind CSS 3 + shadcn/ui + Recharts |
| Version | 1.0  —  April 2025 |
| Audience | Frontend engineers implementing the UI |

## **Document Contents**

| **Section** | **Topic** |
| --- | --- |
| 1 | Layout Structure — shell, sidebar, navbar, content grid |
| 2 | Page Breakdown — every page with zone map |
| 3 | Component Breakdown — cards, tables, charts, forms, modals |
| 4 | UI Style Guide — colors, typography, spacing, buttons |
| 5 | Design System — reusable Tailwind component classes |
| 6 | User Flow — annotated path from login to insights |
| 7 | Responsive Strategy — breakpoints, mobile adaptations |

# **1. Layout Structure**

The app uses a classic app-shell pattern: fixed dark sidebar on the left, sticky top navbar, and a scrollable main content area. On mobile the sidebar collapses into a bottom tab bar.

## **1.1  App Shell (Desktop — ≥1024px)**

| +--sidebar (w-64, fixed, dark)--+--navbar (h-16, sticky, light)----+ |
| --- |
| │                               │  Search │ Alerts │ Avatar        │ |
| │  Logo                         +--------------------------------------+ |
| │  ─────────────────            │                                      │ |
| │  Nav items (icon + label)     │   MAIN CONTENT AREA                  │ |
| │                               │   (scrollable, bg-slate-50)          │ |
| │                               │                                      │ |
| │  ─────────────────            │                                      │ |
| │  User profile block           │                                      │ |
| +───────────────────────────────+──────────────────────────────────────+ |

| **Zone** | **Tailwind Classes** | **Notes** |
| --- | --- | --- |
| App wrapper | flex h-screen overflow-hidden | Root flex container |
| Sidebar | w-64 flex-shrink-0 bg-slate-900 flex flex-col fixed h-full | Always visible ≥lg |
| Main wrapper | flex-1 flex flex-col ml-64 overflow-hidden | Offset by sidebar width |
| Navbar | h-16 bg-white border-b border-slate-200 flex items-center px-6 sticky top-0 z-10 |  |
| Content area | flex-1 overflow-y-auto bg-slate-50 p-6 | Page-level scroll here |

## **1.2  Sidebar Anatomy**

| **Sub-zone** | **Content** | **Tailwind** |
| --- | --- | --- |
| Logo bar | App icon + "SpendAI" wordmark | px-6 py-5 border-b border-slate-700/50 |
| Nav items | 5 items with icon + label | flex flex-col gap-1 px-3 py-4 flex-1 |
| Active nav item | Indigo pill highlight | bg-indigo-600 text-white rounded-lg |
| Inactive nav item | Muted text, icon at 60% opacity | text-slate-400 hover:bg-slate-800 hover:text-white |
| User profile block | Avatar + name + email, bottom of sidebar | px-4 py-4 border-t border-slate-700/50 mt-auto |

## **1.3  Navbar Anatomy**

| **Slot** | **Content** | **Alignment** |
| --- | --- | --- |
| Left | Page title (h1, 20px, semibold) | flex-1 |
| Center | Global search input (hidden on mobile) | hidden lg:flex |
| Right | Notification bell (with badge), user avatar dropdown | flex items-center gap-3 |

## **1.4  Content Grid**

All pages use an 12-column CSS grid inside the content area. Use these responsive column spans:

| **Use case** | **Desktop (lg)** | **Tablet (md)** | **Mobile (sm)** |
| --- | --- | --- | --- |
| Stat cards (4 across) | col-span-3 | col-span-6 | col-span-12 |
| Pie chart + trend bar | col-span-7 / col-span-5 | col-span-12 | col-span-12 |
| Full-width table | col-span-12 | col-span-12 | col-span-12 |
| Budget progress list | col-span-5 | col-span-12 | col-span-12 |
| AI insights panel | col-span-4 | col-span-12 | col-span-12 |

# **2. Page Breakdown**

## **2.1  Dashboard  /dashboard**

| **Zone** | **Component** | **Data** |
| --- | --- | --- |
| Row 1 — Stat Cards | 4x StatCard | Total Spent, Budget Left, Top Category, Savings Rate |
| Row 2 Left (7 cols) | MonthlyBarChart | Last 6 months spend totals |
| Row 2 Right (5 cols) | CategoryDonutChart | Spend % by category this month |
| Row 3 Left (8 cols) | RecentExpensesTable | Last 10 transactions, truncated |
| Row 3 Right (4 cols) | BudgetSummaryList | Per-category progress bars |
| Floating panel | AIInsightsCard | 3 insight bullets from LLM |

## **2.2  Expenses  /expenses**

| **Zone** | **Component** | **Notes** |
| --- | --- | --- |
| Top bar | PageHeader + AddExpenseButton | Button opens AddExpenseModal |
| Filter bar | FilterBar | Category picker, date range, search, payment method, sort |
| Main | ExpenseTable | Paginated, sortable, inline edit via row action menu |
| Empty state | EmptyStateCard | Shown when filters return no results |

## **2.3  Budgets  /budgets**

| **Zone** | **Component** | **Notes** |
| --- | --- | --- |
| Header | PageHeader + SetBudgetButton |  |
| Overall budget card | OverallBudgetGauge | Large arc gauge, big number display |
| Category grid | BudgetCategoryGrid | 12 cards in 3-col grid, each with progress bar + spent/limit |
| Alert banner | BudgetAlertBanner | Shown inline when any category hits 80% threshold |

## **2.4  Insights  /insights**

| **Zone** | **Component** | **Notes** |
| --- | --- | --- |
| Insights header | PageHeader + RegenerateButton | Spinner on active LLM call |
| Insight cards | InsightCard (x3–5) | Icon + category badge + body text + confidence pip |
| Anomaly row | AnomalyAlert (x1–3) | Amber warning card with spike percentage |
| Suggestions list | SuggestionCard (x2–4) | Green card, actionable tip text |
| Empty / loading | InsightSkeleton | 3 skeleton cards with shimmer animation |

## **2.5  Settings  /settings**

| **Zone** | **Component** | **Fields** |
| --- | --- | --- |
| Profile section | ProfileForm | full_name, email (read-only), currency select, budget_reset_day |
| Password section | PasswordChangeForm | current_password, new_password, confirm |
| Danger zone | DangerZoneCard | "Delete Account" button — red border card, confirmation modal |

# **3. Component Breakdown**

## **3.1  StatCard**

| **Prop** | **Type** | **Notes** |
| --- | --- | --- |
| title | string | e.g. "Total Spent" |
| value | string | Formatted currency string |
| change | number | Month-over-month % delta |
| trend | "up" │ "down" │ "neutral" | Controls arrow icon color |
| icon | ReactNode | Lucide icon, rendered in colored circle |
| iconColor | string | Tailwind bg class e.g. bg-indigo-100 |

Anatomy: white card, rounded-xl shadow-sm, p-6. Icon circle top-left. Title in text-slate-500 text-sm. Value in text-slate-900 text-2xl font-bold. Change badge bottom-right.

## **3.2  ExpenseTable**

| **Column** | **Width** | **Notes** |
| --- | --- | --- |
| Date | w-28 | Formatted as "Apr 12" |
| Description | flex-1 | Truncated, full text on hover tooltip |
| Category | w-36 | Colored badge with emoji icon |
| Payment | w-28 | Pill badge: Cash / UPI / Card |
| Amount | w-28 | Right-aligned, red for expense |
| Actions | w-16 | Three-dot menu: Edit, Delete |

Row hover: bg-slate-50. Selected row: bg-indigo-50. Sticky header. Empty state shows illustration + CTA button.

## **3.3  Charts**

| **Chart** | **Library** | **Config** |
| --- | --- | --- |
| MonthlyBarChart | Recharts BarChart | ResponsiveContainer, rounded bars (radius=[4,4,0,0]), indigo fill, XAxis month labels, no gridlines except horizontal |
| CategoryDonutChart | Recharts PieChart | innerRadius=60, outerRadius=90, custom label line, legend below with category name + % |
| BudgetProgressBar | Native HTML | Custom div-based bar: bg-slate-100 track, colored fill, amber when >80%, red when >100% |
| OverallBudgetGauge | Recharts RadialBarChart | Single arc, startAngle=180, endAngle=0, label in center showing spent/total |

## **3.4  AddExpenseModal**

| **Field** | **Input Type** | **Validation** |
| --- | --- | --- |
| Amount | number input | Required, > 0, max 2 decimal places |
| Category | Select with emoji + color swatches | Required |
| Date | Date picker (native input type=date) | Required, no future dates |
| Description | text input | Optional, max 200 chars, char counter shown |
| Payment Method | Segmented control (4 options) | Required |

Modal: max-w-md, centered, backdrop bg-black/40. Header with title + close X. Footer with Cancel (ghost) + Save (primary) buttons. Form uses react-hook-form. Errors shown inline below each field in text-red-500 text-xs.

## **3.5  Other Core Components**

| **Component** | **Description** |
| --- | --- |
| FilterBar | Horizontal row of filter controls. Collapses to a single "Filters" button on mobile that opens a bottom drawer. |
| CategoryBadge | Pill with emoji + category name. Background uses the category color at 15% opacity, text at 100%. |
| BudgetAlertBanner | Full-width amber banner with icon. Dismissible. Shows category name and % used. |
| AIInsightsCard | Indigo-gradient card. "AI" sparkle icon header. Bullet list of insight strings. "Regenerate" link bottom-right. |
| EmptyStateCard | Centered illustration (SVG), h2 title, body text, optional CTA button. Used on all list pages. |
| ConfirmModal | Small modal (max-w-sm) for destructive actions. Red "Confirm" button, Cancel ghost button. |
| ToastNotification | Bottom-right stack. green=success, amber=warning (budget alert), red=error. Auto-dismiss 4s. |
| SkeletonLoader | Gray shimmer blocks matching the shape of the actual content. Used during data fetch. |

# **4. UI Style Guide**

## **4.1  Color System**

All colors map to Tailwind CSS utility classes. Use CSS variables for theming in tailwind.config.js.

### **Brand Colors**

| **Token** | **Hex** | **Tailwind Class** | **Usage** |
| --- | --- | --- | --- |
| primary | #6366F1 | indigo-500 | Primary buttons, active nav, links |
| primary-dark | #4F46E5 | indigo-600 | Button hover state, headings |
| accent | #A78BFA | violet-400 | Highlights, AI panel gradient |
| success | #10B981 | emerald-500 | Budget OK, income, positive delta |
| warning | #F59E0B | amber-500 | Budget alerts (80%), anomaly banners |
| danger | #EF4444 | red-500 | Budget exceeded (100%), errors, delete |

### **Surface Colors (Sidebar ****&**** Dark Zones)**

| **Token** | **Hex** | **Tailwind Class** | **Usage** |
| --- | --- | --- | --- |
| surface-900 | #0F172A | slate-900 | Sidebar background |
| surface-800 | #1E293B | slate-800 | Sidebar hover, dark card bg |
| surface-700 | #334155 | slate-700 | Sidebar active item bg |
| surface-600 | #475569 | slate-600 | Sidebar borders, dividers |

### **Content Colors (Main Area ****&**** Cards)**

| **Token** | **Hex** | **Tailwind Class** | **Usage** |
| --- | --- | --- | --- |
| page-bg | #F8FAFC | slate-50 | Main content area background |
| card-bg | #FFFFFF | white | Card / panel backgrounds |
| border | #E2E8F0 | slate-200 | Card borders, table dividers |
| text-primary | #0F172A | slate-900 | Headings, values |
| text-secondary | #64748B | slate-500 | Labels, meta text, captions |
| text-muted | #94A3B8 | slate-400 | Placeholders, disabled text |

## **4.2  Typography**

| **Role** | **Font** | **Size** | **Weight** | **Tailwind** |
| --- | --- | --- | --- | --- |
| Page title | Inter | 20px | 600 | text-xl font-semibold text-slate-900 |
| Section heading | Inter | 16px | 600 | text-base font-semibold text-slate-900 |
| Stat value | Inter | 28px | 700 | text-3xl font-bold text-slate-900 |
| Card label | Inter | 13px | 500 | text-sm font-medium text-slate-500 |
| Body text | Inter | 14px | 400 | text-sm text-slate-600 |
| Caption / meta | Inter | 12px | 400 | text-xs text-slate-400 |
| Code / mono | JetBrains Mono | 13px | 400 | font-mono text-sm |
| Nav item | Inter | 14px | 500 | text-sm font-medium |
| Button | Inter | 14px | 500 | text-sm font-medium |
| Badge / pill | Inter | 12px | 500 | text-xs font-medium |

Font import: Add Inter + JetBrains Mono from Google Fonts. Set font-family: "Inter", sans-serif as default in tailwind.config.js under theme.fontFamily.sans.

## **4.3  Spacing Scale**

Use the default Tailwind spacing scale. Key values:

| **Token** | **px** | **Usage** |
| --- | --- | --- |
| p-1 / gap-1 | 4px | Icon padding, tight badge padding |
| p-2 / gap-2 | 8px | Badge inner padding, small button padding |
| p-3 / gap-3 | 12px | Input padding, nav item padding |
| p-4 / gap-4 | 16px | Card inner padding (mobile), list item spacing |
| p-5 | 20px | Card padding (standard) |
| p-6 / gap-6 | 24px | Card padding (large), content area padding |
| p-8 / gap-8 | 32px | Section spacing |
| gap-4 | 16px | Default grid gap (cards, form fields) |
| gap-6 | 24px | Section-level gap |

## **4.4  Button Styles**

| **Variant** | **Base Classes** | **Hover** | **Disabled** |
| --- | --- | --- | --- |
| Primary | bg-indigo-600 text-white rounded-lg px-4 py-2 text-sm font-medium shadow-sm | hover:bg-indigo-700 | opacity-50 cursor-not-allowed |
| Secondary | bg-white text-slate-700 border border-slate-300 rounded-lg px-4 py-2 text-sm font-medium | hover:bg-slate-50 | opacity-50 |
| Ghost | bg-transparent text-slate-600 rounded-lg px-4 py-2 text-sm font-medium | hover:bg-slate-100 | opacity-50 |
| Danger | bg-red-600 text-white rounded-lg px-4 py-2 text-sm font-medium | hover:bg-red-700 | opacity-50 |
| Icon | p-2 rounded-lg text-slate-500 | hover:bg-slate-100 hover:text-slate-900 | opacity-50 |

All buttons: transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2. Min touch target: h-10.

## **4.5  Border Radius ****&**** Shadows**

| **Token** | **Value** | **Usage** |
| --- | --- | --- |
| rounded-lg | 8px | Buttons, inputs, small cards |
| rounded-xl | 12px | Stat cards, filter bar, modals |
| rounded-2xl | 16px | Large dashboard panels, insight cards |
| rounded-full | 9999px | Avatars, category dot indicators, toggle pills |
| shadow-sm | 0 1px 2px rgba(0,0,0,0.05) | Cards (default) |
| shadow-md | 0 4px 6px rgba(0,0,0,0.07) | Dropdowns, modals |
| shadow-lg | 0 10px 15px rgba(0,0,0,0.1) | Floating panels, popovers |

# **5. Design System**

Implement as a component library in src/components/ui/. Base components on shadcn/ui primitives where possible.

## **5.1  Tailwind Config Additions**

| // tailwind.config.js |
| --- |
| theme: { |
| extend: { |
| fontFamily: { sans: ["Inter", "sans-serif"], mono: ["JetBrains Mono", "monospace"] }, |
| colors: { |
| brand: { DEFAULT: "#6366F1", dark: "#4F46E5", light: "#A78BFA" }, |
| }, |
| animation: { shimmer: "shimmer 1.5s infinite" }, |
| keyframes: { shimmer: { "0%,100%": { opacity: 1 }, "50%": { opacity: 0.5 } } }, |
| }, |
| }, |

## **5.2  Component File Structure**

| src/components/ |
| --- |
| ui/                    # Primitives (Button, Input, Badge, Card, Modal, Toast) |
| layout/                # AppShell, Sidebar, Navbar, PageHeader |
| dashboard/             # StatCard, MonthlyBarChart, CategoryDonutChart, RecentExpensesTable |
| expenses/              # ExpenseTable, AddExpenseModal, FilterBar, ExpenseRow |
| budgets/               # BudgetCategoryGrid, BudgetProgressBar, OverallBudgetGauge, BudgetAlertBanner |
| insights/              # InsightCard, AnomalyAlert, SuggestionCard, InsightSkeleton |
| shared/                # EmptyStateCard, SkeletonLoader, ConfirmModal, CategoryBadge |

## **5.3  Reusable Class Compositions (CVA patterns)**

Use class-variance-authority (CVA) for variant-based components:

| // Card base — use everywhere |
| --- |
| const card = "bg-white rounded-xl shadow-sm border border-slate-200 p-6" |
|  |
| // Section label |
| const label = "text-sm font-medium text-slate-500 uppercase tracking-wide" |
|  |
| // Stat value |
| const statValue = "text-3xl font-bold text-slate-900 tabular-nums" |
|  |
| // Category badge |
| const badge = (color) => `inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[${color}]/15 text-[${color}]` |
|  |
| // Page container |
| const page = "max-w-7xl mx-auto space-y-6" |

## **5.4  Icon System**

- **Library: **lucide-react (already in most React setups).

- **Sidebar icons: **LayoutDashboard, Receipt, PiggyBank, Sparkles, Settings

- **Stat card icons: **TrendingUp, Wallet, Tag, Target

- **Action icons: **Plus, Pencil, Trash2, RefreshCw, Download, ChevronDown

- **Status icons: **AlertTriangle (warning), CheckCircle (success), XCircle (error), Info

- Always use size={16} or size={18}. Never scale with CSS — pass size prop.

## **5.5  Animation Tokens**

| **Animation** | **CSS / Tailwind** | **Used On** |
| --- | --- | --- |
| Page transition | opacity-0 → opacity-100 duration-200 | Route changes |
| Modal enter | scale-95 opacity-0 → scale-100 opacity-100 duration-150 | Modal open |
| Toast slide | translate-x-full → translate-x-0 duration-300 | Toast appear |
| Skeleton shimmer | custom keyframe (see config) | All skeleton loaders |
| Progress bar fill | transition-all duration-700 ease-out | Budget progress bars on mount |
| Button press | active:scale-95 transition-transform duration-75 | All buttons |

# **6. User Flow**

Annotated flow for the primary path. Each step notes the component shown, action available, and transition.

## **6.1  Full Flow: Login → Dashboard → Add Expense → View Insights**

| **Step** | **Route** | **Screen / Component** | **Key Actions** | **Transition To** |
| --- | --- | --- | --- | --- |
| 1 | /login | LoginPage: centered card, email + password inputs, Submit button, "Register" link | Submit → POST /auth/login | If success → /dashboard |
| 2 | /register | RegisterPage: same card style, email + name + password, "Already have account" link | Submit → POST /auth/register | Success → /dashboard |
| 3 | /dashboard | AppShell loads. Dashboard renders 4 StatCards + charts + RecentExpensesTable + AIInsightsCard | Click "+ Add Expense" in navbar or FAB | AddExpenseModal opens (no route change) |
| 4 | Modal (dashboard) | AddExpenseModal: amount, category, date, description, payment method form | Fill form → Submit → POST /expenses | Modal closes, table + stats refresh via React Query invalidation |
| 5 | /expenses | Full expense list with FilterBar. User adjusts date range filter. | Click row action menu → Edit | EditExpenseModal opens pre-filled |
| 6 | /budgets | OverallBudgetGauge + 12 BudgetCategoryGrid cards. User sees amber alert on Food category. | Click "Set Budget" on a category card | SetBudgetModal opens for that category |
| 7 | /insights | InsightSkeleton shows for 3–8s (LLM call). Then InsightCards + AnomalyAlerts + SuggestionCards render. | Click "Regenerate" button | Skeleton reappears, new insights load. Rate limit toast if >10/hour. |
| 8 | /settings | ProfileForm pre-filled. User updates currency to USD. | Save → PUT /users/me | Success toast "Profile updated". All currency values re-render. |

## **6.2  Auth Guard Logic**

- **Protected routes: **/dashboard, /expenses, /budgets, /insights, /settings

- **If no access token: **Redirect to /login immediately (React Router loader).

- **If access token expired (401 from API): **Axios interceptor calls /auth/refresh silently. If refresh also fails → redirect /login.

- **On login success: **Store access token in memory (Zustand authStore). Refresh token in HttpOnly cookie (set by backend).

# **7. Responsive Design Strategy**

## **7.1  Breakpoints**

| **Breakpoint** | **Width** | **Tailwind Prefix** | **Layout Mode** |
| --- | --- | --- | --- |
| Mobile (default) | < 640px | (none) | Single column, bottom nav, stacked cards |
| Small | 640–767px | sm: | 2-column card grid, no sidebar |
| Medium (tablet) | 768–1023px | md: | 2-column grid, sidebar as overlay drawer |
| Large (desktop) | ≥ 1024px | lg: | Sidebar fixed, 12-column grid, all zones visible |
| XL | ≥ 1280px | xl: | Wider content area, 4 stat cards fully comfortable |

## **7.2  Mobile-Specific Changes**

| **Element** | **Desktop** | **Mobile (****<****lg)** |
| --- | --- | --- |
| Navigation | Fixed left sidebar (w-64) | Bottom tab bar with 5 icon-only tabs |
| Sidebar | Always visible | Hidden. Hamburger opens full-screen overlay drawer. |
| Stat cards | 4 in a row (col-span-3) | 2x2 grid (col-span-6) |
| Charts | Side by side | Stacked vertically |
| Expense table | Full columns visible | Show only Date, Description (truncated), Amount. Actions in swipe gesture. |
| Add expense | Modal (centered) | Bottom sheet sliding up from screen bottom |
| Filter bar | Full horizontal row | "Filters" button opens bottom drawer |
| Navbar | Search bar visible | Search icon only, tapping expands full-width input |
| Page padding | p-6 | p-4 |

## **7.3  Tailwind Responsive Pattern**

Apply mobile-first: default classes target mobile, then add lg: prefix for desktop overrides.

| // App shell example |
| --- |
| <div className="flex flex-col lg:flex-row h-screen"> |
| <Sidebar className="hidden lg:flex lg:w-64 lg:flex-col" /> |
| <div className="flex-1 flex flex-col"> |
| <Navbar /> |
| <main className="flex-1 overflow-y-auto p-4 lg:p-6 bg-slate-50"> |
| {children} |
| </main> |
| </div> |
| <BottomNav className="lg:hidden" />  {/* Mobile only */} |
| </div> |

## **7.4  Touch Targets ****&**** Accessibility**

- **Minimum touch target: **All interactive elements min h-10 w-10 (40px). Use p-2 on icon buttons to meet this.

- **Focus rings: **Always visible — focus:ring-2 focus:ring-indigo-500. Never outline-none without a replacement.

- **Color contrast: **All text/background pairs meet WCAG AA (4.5:1 for body, 3:1 for large text). Indigo-600 on white passes. Slate-500 on white does NOT — use slate-600 or darker for body.

- **Charts: **Include aria-label on all SVG chart containers. Add sr-only data table for screen readers.

- **Modals: **Trap focus inside modal when open. Escape key closes. Return focus to trigger element on close.

# **Appendix**

## **A. Tailwind CSS Setup for This Design**

| // Install |
| --- |
| npm install -D tailwindcss postcss autoprefixer |
| npm install class-variance-authority clsx tailwind-merge |
| npm install lucide-react |
| npm install recharts |
|  |
| // For shadcn/ui components |
| npx shadcn-ui@latest init |
| // Then add as needed: npx shadcn-ui@latest add button input select dialog toast |

## **B. Font Setup**

| // index.html <head> |
| --- |
| <link rel="preconnect" href="https://fonts.googleapis.com"> |
| <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet"> |

## **C. Page Route Map**

| **Path** | **Component File** | **Auth Required** |
| --- | --- | --- |
| /login | pages/Login.jsx | No (redirect to /dashboard if already authed) |
| /register | pages/Register.jsx | No |
| /dashboard | pages/Dashboard.jsx | Yes |
| /expenses | pages/Expenses.jsx | Yes |
| /budgets | pages/Budgets.jsx | Yes |
| /insights | pages/Insights.jsx | Yes |
| /settings | pages/Settings.jsx | Yes |
| * | pages/NotFound.jsx | No |

## **D. Design Decisions ****&**** Rationale**

| **Decision** | **Rationale** |
| --- | --- |
| Dark sidebar, light content | Clear visual separation between navigation and data. Reduces eye fatigue vs full dark mode for data-heavy dashboards. |
| Indigo-600 as primary | Conveys trust and clarity (common in fintech). High contrast on white. Avoids the blue of banking (differentiation). |
| Card-based layout | Each data zone is self-contained. Easy to rearrange for different viewports and future drag-drop customization. |
| No animation on data | Numbers and charts render instantly. Animation only on UI chrome (modals, toasts). Prevents distraction from financial data. |
| Bottom sheet on mobile for add expense | Native feel on mobile. Keeps the full form visible without zoom issues. Standard pattern users already know. |
| Skeleton loaders over spinners | Reduces perceived load time. Preserves layout stability (no CLS). Critical for the AI insights panel which can take 3–8s. |

AI Expense Tracker  —  DESIGN.md v1.0  —  For Frontend Engineering Use

AI Expense Tracker — DESIGN.md  |  Page