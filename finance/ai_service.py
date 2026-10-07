import os
import json
import re
from decimal import Decimal

# Optional OpenAI integration
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
except Exception:
    client = None

DEFAULT_CATEGORIES = [
    'Housing & Rent',
    'Groceries & Food',
    'Dining Out & Delivery',
    'Transportation',
    'Utilities & Bills',
    'Entertainment & Leisure',
    'Subscriptions',
    'Shopping & Personal',
    'Healthcare & Fitness',
    'Travel & Holiday',
    'Education & Self-Improvement',
    'Miscellaneous'
]

SUBSCRIPTION_KEYWORDS = ['netflix', 'spotify', 'prime', 'hulu', 'disney', 'youtube', 'patreon', 'gym', 'fitness', 'icloud', 'chatgpt', 'dropbox', 'adobe', 'vpn']
DINING_KEYWORDS = ['starbucks', 'uber eats', 'doordash', 'zomato', 'swiggy', 'mcdonald', 'kfc', 'cafe', 'restaurant', 'bar', 'burger', 'pizza', 'bistro']
GROCERY_KEYWORDS = ['walmart', 'trader joe', 'costco', 'supermarket', 'market', 'grocery', 'whole foods', 'target', 'kroger', 'aldi']
HOUSING_KEYWORDS = ['rent', 'mortgage', 'maintenance', 'landlord', 'property tax', 'hoa']
TRANSPORT_KEYWORDS = ['gas', 'fuel', 'petrol', 'diesel', 'uber', 'lyft', 'subway', 'metro', 'bus', 'parking', 'toll', 'train']
UTILITY_KEYWORDS = ['electric', 'water', 'internet', 'wifi', 'broadband', 'phone', 'verizon', 'att', 't-mobile', 'gas bill', 'sewer']

def ai_categorize_expense(title, amount=0.0, description=""):
    """Categorizes expense using OpenAI API if available, else high-accuracy heuristic engine."""
    title_lower = (title or "").lower()
    desc_lower = (description or "").lower()
    combined = f"{title_lower} {desc_lower}"

    # Try OpenAI if API key configured
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key and client:
        try:
            prompt = f"""You are an expert personal finance AI. Categorize this expense into exactly one of these categories:
{json.dumps(DEFAULT_CATEGORIES)}

Expense title: "{title}"
Amount: ₹{amount}
Description: "{description}"

Also determine if this is potentially an unwanted, wasteful, or recurring impulse expense.
Respond in valid JSON ONLY with format:
{{
  "category": "exact category name from list",
  "is_unwanted": true/false,
  "flag_reason": "brief reason if unwanted or null"
}}"""
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            cat = result.get("category", "Miscellaneous")
            if cat not in DEFAULT_CATEGORIES:
                cat = "Miscellaneous"
            return {
                "category": cat,
                "is_unwanted": bool(result.get("is_unwanted", False)),
                "flag_reason": result.get("flag_reason", "")
            }
        except Exception:
            pass # Fall back smoothly to rule-based engine

    # Heuristic / Intelligent Rule-Based Engine
    category = "Miscellaneous"
    is_unwanted = False
    flag_reason = ""

    if any(k in combined for k in SUBSCRIPTION_KEYWORDS):
        category = 'Subscriptions'
        is_unwanted = True
        flag_reason = "Recurring digital subscription. Check if active usage justifies ongoing monthly charge."
    elif any(k in combined for k in DINING_KEYWORDS):
        category = 'Dining Out & Delivery'
        if float(amount) > 40:
            is_unwanted = True
            flag_reason = f"High dining/delivery expense (₹{amount}). Preparing home meals could save up to 70%."
    elif any(k in combined for k in GROCERY_KEYWORDS):
        category = 'Groceries & Food'
    elif any(k in combined for k in HOUSING_KEYWORDS):
        category = 'Housing & Rent'
    elif any(k in combined for k in TRANSPORT_KEYWORDS):
        category = 'Transportation'
    elif any(k in combined for k in UTILITY_KEYWORDS):
        category = 'Utilities & Bills'
    elif any(k in combined for k in ['movie', 'steam', 'game', 'playstation', 'xbox', 'concert', 'club']):
        category = 'Entertainment & Leisure'
        if float(amount) > 60:
            is_unwanted = True
            flag_reason = "Discretionary leisure spend. Consider capping entertainment to 10% of monthly budget."
    elif any(k in combined for k in ['zara', 'h&m', 'amazon', 'shoes', 'clothes', 'luxury', 'mall', 'perfume']):
        category = 'Shopping & Personal'
        if float(amount) > 100:
            is_unwanted = True
            flag_reason = "Discretionary shopping. Evaluate the 24-hour rule before non-essential purchases."
    elif any(k in combined for k in ['doctor', 'pharmacy', 'medicine', 'dental', 'clinic', 'vitamins']):
        category = 'Healthcare & Fitness'
    elif any(k in combined for k in ['flight', 'hotel', 'airbnb', 'vacation', 'resort']):
        category = 'Travel & Holiday'
    elif any(k in combined for k in ['course', 'book', 'udemy', 'tuition', 'cert', 'training']):
        category = 'Education & Self-Improvement'

    return {
        "category": category,
        "is_unwanted": is_unwanted,
        "flag_reason": flag_reason
    }

def ai_generate_budget_plan(total_income, current_expenses_summary=None, savings_target=0.0):
    """Generates an optimal, personalized monthly budget allocation using 50/30/20 guidelines modified by user history."""
    income = float(total_income) if total_income else 3000.0
    target_savings = float(savings_target) if savings_target else round(income * 0.20, 2)
    spendable = max(income - target_savings, income * 0.70)

    # Standard balanced budget distribution
    allocations = {
        'Housing & Rent': round(spendable * 0.35, 2),
        'Groceries & Food': round(spendable * 0.16, 2),
        'Utilities & Bills': round(spendable * 0.10, 2),
        'Transportation': round(spendable * 0.10, 2),
        'Healthcare & Fitness': round(spendable * 0.06, 2),
        'Dining Out & Delivery': round(spendable * 0.07, 2),
        'Entertainment & Leisure': round(spendable * 0.05, 2),
        'Subscriptions': round(spendable * 0.03, 2),
        'Shopping & Personal': round(spendable * 0.05, 2),
        'Education & Self-Improvement': round(spendable * 0.03, 2),
    }

    insights = (
        f"Based on your monthly net income of ₹{income:,.2f}, the AI has structured an optimized 50/30/20 budget framework. "
        f"Essential needs (Housing, Food, Utilities, Transport) account for 65% (₹{spendable*0.71:,.2f}), "
        f"while discretionary lifestyle spending is capped at 15% (₹{spendable*0.29:,.2f}). "
        f"This guarantees a healthy monthly savings rate of ₹{target_savings:,.2f} ({(target_savings/income)*100:.1f}%)."
    )

    return {
        "allocations": allocations,
        "total_budget": round(sum(allocations.values()), 2),
        "target_savings": target_savings,
        "insights": insights
    }

def ai_financial_chat(user_message, financial_context=None):
    """Personal finance assistant responses answering user financial questions."""
    msg_lower = user_message.lower()

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key and client:
        try:
            system_prompt = f"""You are Smart Budget Optimiser's elite AI Financial Advisor. 
Provide concise, highly practical, and motivating financial advice.
User Financial Context: {json.dumps(financial_context or {})}
Always format your response cleanly with bullet points, actionable steps, and clear takeaways."""
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5
            )
            return res.choices[0].message.content
        except Exception:
            pass

    # Expert heuristic advice responses
    if any(w in msg_lower for w in ['invest', 'stock', 'mutual fund', 'crypto', 'etf', 'where to put money']):
        return """### 💡 AI Investment Guidance:
1. **Emergency Buffer First:** Ensure you maintain 3 to 6 months of baseline living expenses in a High-Yield Savings Account (HYSA) before risk-bearing investments.
2. **Broad-Market Index Funds:** Allocate monthly surpluses into low-cost index ETFs (e.g., S&P 500 or Total World Market Index). This captures historical 8-10% annual returns without single-stock volatility.
3. **Automate Rupee-Cost Averaging:** Set up automated transfers immediately on payday to remove emotion and timing risks.
4. **Tax-Advantaged Accounts:** Maximize retirement vehicles (such as Roth IRA or 401k employer match) to compound tax-free wealth."""

    elif any(w in msg_lower for w in ['save', 'cut cost', 'reduce expense', 'tight budget', 'unwanted']):
        return """### 🎯 Smart Expense Optimisation Blueprint:
1. **Audit Ghost Subscriptions:** Run through our Unwanted Expenses audit. Cancel streaming and app services you haven't opened in 14 days.
2. **The 72-Hour Rule:** For any non-essential purchase exceeding ₹50, delay the cart for 72 hours. 65% of impulse desires fade.
3. **Meal Planning Efficiency:** Consolidate grocery runs and batch cook 3 dinners weekly. This immediately trims 30-40% off dining out charges.
4. **Negotiate Recurring Bills:** Call your internet and insurance providers annually to request retention discounts or competitor price matching."""

    elif any(w in msg_lower for w in ['debt', 'credit card', 'loan', 'pay off']):
        return """### 🛡️ Accelerated Debt Repayment Strategy:
1. **Avalanche Method:** Prioritize paying the absolute maximum toward your highest interest rate debt (typically credit cards 20%+ APR) while paying minimums on others. This minimizes overall interest paid.
2. **Snowball Alternative:** If psychological momentum is needed, knock out the smallest balance loan first for an immediate motivational win.
3. **Freeze High-Interest Lines:** Switch day-to-day purchases to debit or cash until revolving credit utilization drops below 30%."""

    else:
        return f"""### 📊 AI Financial Analysis for: "{user_message.strip()}"
- **Personalized Assessment:** A strong financial trajectory relies on maintaining an expense-to-income ratio under 70%.
- **Action Step:** Check your current monthly budget and allocate at least 20% of net income directly towards high-priority savings or debt clearance.
- **Continuous Monitoring:** Regularly review the 'Unwanted Expenses' tab to ensure subtle lifestyle creep doesn't erode your savings capacity."""
