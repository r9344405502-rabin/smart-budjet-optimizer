# ⚡ SMART BUDGET OPTIMISER
### Enterprise AI-Powered Personal Finance & Wealth Architecture

**Smart Budget Optimiser** is a personal finance SaaS application engineered with **Python (Django)**, **MySQL**, and **Artificial Intelligence**. It eliminates manual spreadsheet bookkeeping by automatically categorizing transactions, exposing subscription waste, computing 50/30/20 budget allocations, and guiding wealth accumulation through an interactive AI Financial Advisor.

---

## 🌟 Key Features

1. **AI-Powered Expense Categorisation & Audit**
   - Parses transaction titles & notes semantically.
   - Automatically maps entries into standard categories (*Housing, Groceries, Dining, Transportation, Utilities, Subscriptions, Entertainment, Healthcare, etc.*).
   - Detects unwanted, wasteful, or recurring impulse spending (e.g. dormant gym memberships, high food delivery markups) with actionable explanations.

2. **Automated 50/30/20 Monthly Budget Optimiser**
   - Dynamically calculates envelope limits based on net monthly inflow and personal savings targets.
   - Allows users to fine-tune individual category caps with real-time recalculated surplus forecasts.

3. **Multi-Tier Wealth & Savings Goals**
   - Set and track liquid **Emergency Reserves**, **Capital Purchases**, and long-term **Investment Portfolios** (e.g. S&P 500 Index Funds).
   - Interactive deposit actions and automated AI contribution recommendations.

4. **Bills & Recurring Obligation Governance**
   - Calendar tracking for upcoming utilities, insurances, and loans.
   - One-click payment reconciliation toggle.

5. **Monthly Performance Audits & Comparative Reports**
   - Month-over-month telemetry comparison (Inflow Delta, Outflow Delta, Net Surplus).
   - Instant printable / PDF export functionality.

6. **Interactive AI Financial Advisor (Chat)**
   - 24/7 personal CFO that analyzes your live financial ledger.
   - Ask questions regarding debt payoff strategies, emergency buffer sizing, or index fund dollar-cost averaging.

7. **Public Interactive AI Demo**
   - Accessible to visitors without an account.
   - Live sandbox to test spending scenarios and observe anomaly detection.

8. **Google Sign-In & Onboarding Flow**
   - Seamless Google OAuth integration with a fallback one-click evaluator mode.
   - Onboarding wizard (*Initial Financial Setup*) for new profiles.

9. **Professional Administrator Portal**
   - Separate control center at `/admin/` with custom headers, search, filters, and full database oversight.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.12, Django 6.x
- **Database:** MySQL / MariaDB (XAMPP compatible)
- **AI Engine:** OpenAI API (with intelligent zero-downtime heuristic engine)
- **Frontend:** Vanilla HTML5, CSS3 (Custom SaaS Design System with glassmorphism and dark mode), JavaScript (ES6+), Chart.js
- **PDF Generation:** Browser Print / PDF Export Engine

---

## 🚀 How to Run the Application

The server is currently **active and running** on your machine at:
👉 **`http://127.0.0.1:8000/`**

If you restart your computer, follow these quick steps:

1. **Start MySQL (if using XAMPP):**
   - Ensure MySQL is running on port 3306.

2. **Activate the Virtual Environment & Run Server:**
   ```powershell
   cd "D:\RABIN K\SmartBudgetOptimiser"
   .\venv\Scripts\Activate.ps1
   python manage.py runserver 127.0.0.1:8000
   ```

---

## 🔑 Default Credentials & Authentication

- **Web Application Sign In (`/login/`):**
  - **Admin User:** Username `admin123@` / Password `12345` (Full Admin Privileges & Live Dashboard)
  - **Standard Demo:** Username `demouser` / Password `demo123`
  - Or click **"Create Free Account"** (`/register/`) to create a fresh user.

- **Administrator Portal (`/admin/`):**
  - **Username:** `admin123@` (or `admin`)
  - **Password:** `12345` (or `admin123`)

---

## 📂 Project Architecture

```
SmartBudgetOptimiser/
├── core/                  # Django project configuration
│   ├── settings.py        # MySQL database, templates, and static settings
│   ├── urls.py            # Global URL routing
│   └── __init__.py        # MariaDB 10.4 backward compatibility patches
├── finance/               # Core business & finance application
│   ├── models.py          # Income, Expense, Budget, Goal, Bill, Profile
│   ├── views.py           # Views & REST APIs
│   ├── urls.py            # Feature routes
│   ├── admin.py           # Custom Django Admin configuration
│   └── ai_service.py      # OpenAI & Heuristic analysis algorithms
├── static/
│   ├── css/main.css       # Premium SaaS styling & design system
│   └── js/main.js         # Interactive demo, Chatbot, Chart.js logic
├── templates/             # HTML5 templates
│   ├── base.html          # Shell layout & navbar
│   ├── home.html          # Public landing page
│   ├── about.html         # In-depth about page
│   ├── demo.html          # Public interactive AI demo
│   ├── setup.html         # Onboarding setup for new users
│   ├── dashboard.html     # Main finance control center
│   ├── expenses.html      # Expense management & AI tags
│   ├── income.html        # Revenue streams
│   ├── budget.html        # AI budget editor
│   ├── goals.html         # Goals & investment tracker
│   ├── bills.html         # Recurring obligations
│   ├── reports.html       # Monthly AI comparison & PDF
│   └── ai_assistant.html  # Interactive chatbot
└── manage.py
```
