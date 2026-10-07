from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from datetime import date, datetime, timedelta
import json

from .models import Profile, Income, Expense, Budget, Goal, Bill, MonthlyReport
from .ai_service import ai_categorize_expense, ai_generate_budget_plan, ai_financial_chat

# -------------------------------------------------------------
# PUBLIC PAGES
# -------------------------------------------------------------
def home_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.is_onboarded:
            return redirect('/setup/')
    return render(request, 'home.html')

def about_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    return render(request, 'about.html')

def demo_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    return render(request, 'demo.html')

# -------------------------------------------------------------
# AUTHENTICATION (SIGN IN & REGISTER)
# -------------------------------------------------------------
def login_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    if request.method == 'POST':
        # Handle 1-click demo login button if pressed
        if 'demo_login' in request.POST:
            demo_user = User.objects.filter(username='demouser').first()
            if not demo_user:
                demo_user = User.objects.create_user(username='demouser', email='demo@smartbudget.ai', password='demo123')
                Profile.objects.get_or_create(user=demo_user, is_onboarded=True, monthly_savings_target=1000.00)
            else:
                demo_user.set_password('demo123')
                demo_user.save()
            login(request, demo_user)
            messages.success(request, "Signed in as Demo User (Alex Morgan)!")
            return redirect('/dashboard/')

        uname = request.POST.get('username', '').strip()
        pwd = request.POST.get('password', '').strip()

        if not uname or not pwd:
            messages.error(request, "Please enter your email or username and a password.")
            return render(request, 'login.html')

        # Check if user already exists by username OR email
        matching_user = User.objects.filter(username__iexact=uname).first()
        if not matching_user and '@' in uname:
            matching_user = User.objects.filter(email__iexact=uname).first()

        if matching_user:
            # Existing user -> verify password
            user = authenticate(request, username=matching_user.username, password=pwd)
            if user is not None:
                login(request, user)
                profile, _ = Profile.objects.get_or_create(user=user)
                if not profile.is_onboarded:
                    messages.info(request, "Welcome! Please configure your initial financial setup.")
                    return redirect('/setup/')
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('/dashboard/')
            else:
                messages.error(request, "Incorrect password for this account. Please verify your password.")
                return render(request, 'login.html')
        else:
            # User does NOT exist yet -> Automatically create their account with this email/password!
            if '@' in uname:
                email = uname
                base_uname = email.split('@')[0]
            else:
                email = f"{uname}@example.com"
                base_uname = uname

            candidate = base_uname
            cnt = 1
            while User.objects.filter(username__iexact=candidate).exists():
                candidate = f"{base_uname}{cnt}"
                cnt += 1

            new_user = User.objects.create_user(username=candidate, email=email, password=pwd)
            Profile.objects.create(user=new_user, is_onboarded=False)
            login(request, new_user)
            messages.success(request, f"Account created for {email}! Please complete your initial financial setup.")
            return redirect('/setup/')

    return render(request, 'login.html')

def register_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    if request.method == 'POST':
        uname = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        pwd = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')

        if pwd != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username is already taken. Please choose another.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'register.html')

        user = User.objects.create_user(username=uname, email=email, password=pwd)
        Profile.objects.create(user=user, is_onboarded=False)
        login(request, user)
        messages.success(request, "Account created! Let's set up your baseline finances.")
        return redirect('/setup/')

    return render(request, 'register.html')


def logout_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('/')

# -------------------------------------------------------------
# ONBOARDING / INITIAL FINANCIAL SETUP
# -------------------------------------------------------------
@login_required
def setup_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        source_name = request.POST.get('income_source', 'Primary Income')
        income_amt = Decimal(request.POST.get('monthly_income', '4500'))
        savings_target = Decimal(request.POST.get('savings_target', '900'))
        primary_goal = request.POST.get('primary_goal', 'Emergency Reserve')

        today = date.today()
        first_day = date(today.year, today.month, 1)

        # 1. Save Initial Income
        Income.objects.create(
            user=request.user,
            source_name=source_name,
            amount=income_amt,
            date=first_day,
            category='Salary',
            is_recurring=True
        )

        # 2. Update Profile
        profile.is_onboarded = True
        profile.monthly_savings_target = savings_target
        profile.save()

        # 3. Create First Goal
        Goal.objects.create(
            user=request.user,
            name=f"{primary_goal} Fund",
            goal_type='Savings',
            target_amount=savings_target * 6,
            current_amount=savings_target,
            deadline=today + timedelta(days=180),
            ai_suggestion=f"Allocate {currency_symbol}{savings_target / 4:.2f} weekly to achieve this milestone within 6 months."
        )

        # 4. Generate Initial AI Budget
        budget_plan = ai_generate_budget_plan(income_amt, savings_target=savings_target)
        Budget.objects.create(
            user=request.user,
            month=first_day,
            total_allocated=Decimal(str(budget_plan['total_budget'])),
            ai_generated=True,
            details=budget_plan['allocations'],
            ai_insights=budget_plan['insights']
        )

        messages.success(request, "Initial financial setup complete! Your AI dashboard is ready.")
        return redirect('/dashboard/')

    return render(request, 'setup.html')

# -------------------------------------------------------------
# CORE DASHBOARD
# -------------------------------------------------------------
@login_required
def dashboard_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.is_onboarded:
        return redirect('/setup/')

    today = date.today()
    first_day = date(today.year, today.month, 1)

    # Incomes & Expenses
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    total_income = sum(i.amount for i in incomes) or Decimal('0.00')
    total_expenses = sum(e.amount for e in expenses) or Decimal('0.00')
    remaining_balance = total_income - total_expenses
    savings_rate = round((remaining_balance / total_income * 100), 1) if total_income > 0 else 0.0

    # Unwanted / Wasteful Expenses
    unwanted = expenses.filter(is_unwanted=True)

    # Budget vs Actuals
    budget = Budget.objects.filter(user=request.user, month=first_day).first()
    budget_progress = []
    if budget and budget.details:
        for cat, limit in budget.details.items():
            spent = sum(e.amount for e in expenses if e.ai_category == cat)
            pct = round((float(spent) / float(limit) * 100), 1) if limit > 0 else 0
            budget_progress.append({
                'category': cat,
                'limit': limit,
                'spent': spent,
                'percent': pct
            })

    # Spending by category for Chart.js
    category_totals = {}
    for e in expenses:
        category_totals[e.ai_category] = float(category_totals.get(e.ai_category, 0) + float(e.amount))
    
    chart_labels = json.dumps(list(category_totals.keys()))
    chart_data = json.dumps(list(category_totals.values()))

    # Goals & Bills
    goals = Goal.objects.filter(user=request.user, is_completed=False)
    bills = Bill.objects.filter(user=request.user, is_paid=False).order_by('due_date')[:5]

    context = {
        'current_month_name': today.strftime('%B %Y'),
        'total_income': total_income,
        'total_expenses': total_expenses,
        'remaining_balance': remaining_balance,
        'savings_rate': savings_rate,
        'expense_count': expenses.count(),
        'unwanted_expenses': unwanted,
        'budget_progress': budget_progress[:6], # Show top 6 on dashboard
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'goals': goals,
        'upcoming_bills': bills,
    }
    return render(request, 'dashboard.html', context)

# -------------------------------------------------------------
# EXPENSE MANAGEMENT (WITH AI CATEGORIZATION)
# -------------------------------------------------------------
@login_required
def expenses_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    expenses = Expense.objects.filter(user=request.user).order_by('-date', '-created_at')
    if request.GET.get('filter') == 'unwanted':
        expenses = expenses.filter(is_unwanted=True)
    
    return render(request, 'expenses.html', {
        'expenses': expenses,
        'today': date.today()
    })

@login_required
def add_expense_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = Decimal(request.POST.get('amount', '0'))
        exp_date = request.POST.get('date', str(date.today()))
        description = request.POST.get('description', '')

        # AI Categorization & Anomaly Detection
        ai_res = ai_categorize_expense(title, float(amount), description)

        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            date=exp_date,
            ai_category=ai_res['category'],
            is_unwanted=ai_res['is_unwanted'],
            ai_flag_reason=ai_res['flag_reason'],
            description=description
        )

        msg = f"Expense recorded and categorized by AI as '{ai_res['category']}'."
        if ai_res['is_unwanted']:
            msg += f" ⚠️ AI Flag: {ai_res['flag_reason']}"
        messages.success(request, msg)

    return redirect('/expenses/')

@login_required
def delete_expense_view(request, id):
    currency_symbol = request.session.get('currency_symbol', '₹')
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    messages.info(request, "Expense record removed.")
    return redirect(request.META.get('HTTP_REFERER', '/expenses/'))

# -------------------------------------------------------------
# INCOME MANAGEMENT
# -------------------------------------------------------------
@login_required
def income_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    total_income = sum(i.amount for i in incomes) or Decimal('0.00')
    return render(request, 'income.html', {
        'incomes': incomes,
        'total_income': total_income,
        'today': date.today()
    })

@login_required
def add_income_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    if request.method == 'POST':
        source_name = request.POST.get('source_name')
        amount = Decimal(request.POST.get('amount', '0'))
        category = request.POST.get('category', 'Salary')
        inc_date = request.POST.get('date', str(date.today()))
        is_recurring = 'is_recurring' in request.POST

        Income.objects.create(
            user=request.user,
            source_name=source_name,
            amount=amount,
            date=inc_date,
            category=category,
            is_recurring=is_recurring
        )
        messages.success(request, f"Income stream '{source_name}' logged.")

    return redirect('/income/')

@login_required
def delete_income_view(request, id):
    currency_symbol = request.session.get('currency_symbol', '₹')
    income = get_object_or_404(Income, id=id, user=request.user)
    income.delete()
    messages.info(request, "Income stream removed.")
    return redirect('/income/')

# -------------------------------------------------------------
# AI BUDGET MANAGEMENT & EDITING
# -------------------------------------------------------------
@login_required
def budget_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    today = date.today()
    first_day = date(today.year, today.month, 1)

    budget = Budget.objects.filter(user=request.user, month=first_day).first()
    if not budget:
        # Auto-create if none exists
        incomes = Income.objects.filter(user=request.user)
        total_income = sum(i.amount for i in incomes) or Decimal('4000.00')
        plan = ai_generate_budget_plan(total_income)
        budget = Budget.objects.create(
            user=request.user,
            month=first_day,
            total_allocated=Decimal(str(plan['total_budget'])),
            ai_generated=True,
            details=plan['allocations'],
            ai_insights=plan['insights']
        )

    expenses = Expense.objects.filter(user=request.user)
    budget_items = []
    if budget.details:
        for cat, limit in budget.details.items():
            spent = sum(e.amount for e in expenses if e.ai_category == cat)
            pct = round((float(spent) / float(limit) * 100), 1) if limit > 0 else 0
            budget_items.append({
                'category': cat,
                'limit': limit,
                'spent': spent,
                'percent': pct
            })

    return render(request, 'budget.html', {
        'budget': budget,
        'budget_items': budget_items,
        'current_month_name': today.strftime('%B %Y')
    })

@login_required
def update_budget_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    if request.method == 'POST':
        today = date.today()
        first_day = date(today.year, today.month, 1)
        budget = get_object_or_404(Budget, user=request.user, month=first_day)

        new_details = {}
        total = Decimal('0.00')
        for key, val in request.POST.items():
            if key.startswith('cat_'):
                category = key[4:]
                try:
                    limit = float(val)
                    new_details[category] = limit
                    total += Decimal(str(limit))
                except ValueError:
                    pass

        budget.details = new_details
        budget.total_allocated = total
        budget.ai_generated = False
        budget.save()
        messages.success(request, "Budget limits successfully updated.")

    return redirect('/budget/')

@login_required
def generate_budget_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    today = date.today()
    first_day = date(today.year, today.month, 1)
    incomes = Income.objects.filter(user=request.user)
    total_income = sum(i.amount for i in incomes) or Decimal('4500.00')

    plan = ai_generate_budget_plan(total_income)
    budget, _ = Budget.objects.get_or_create(user=request.user, month=first_day)
    budget.total_allocated = Decimal(str(plan['total_budget']))
    budget.details = plan['allocations']
    budget.ai_insights = plan['insights']
    budget.ai_generated = True
    budget.save()

    messages.success(request, "Fresh AI budget model generated based on your income profile.")
    return redirect('/budget/')

# -------------------------------------------------------------
# FINANCIAL GOALS
# -------------------------------------------------------------
@login_required
def goals_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    goals = Goal.objects.filter(user=request.user).order_by('is_completed', '-created_at')
    return render(request, 'goals.html', {'goals': goals})

@login_required
def add_goal_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    if request.method == 'POST':
        name = request.POST.get('name')
        goal_type = request.POST.get('goal_type', 'Savings')
        target_amt = Decimal(request.POST.get('target_amount', '0'))
        current_amt = Decimal(request.POST.get('current_amount', '0'))
        deadline = request.POST.get('deadline') or None

        ai_tip = f"Automate recurring weekly transfers of {currency_symbol}{(target_amt - current_amt)/12:.2f} to hit this target comfortably."

        Goal.objects.create(
            user=request.user,
            name=name,
            goal_type=goal_type,
            target_amount=target_amt,
            current_amount=current_amt,
            deadline=deadline,
            ai_suggestion=ai_tip
        )
        messages.success(request, f"Financial goal '{name}' established.")

    return redirect('/goals/')

@login_required
def contribute_goal_view(request, id):
    currency_symbol = request.session.get('currency_symbol', '₹')
    goal = get_object_or_404(Goal, id=id, user=request.user)
    if request.method == 'POST':
        contribution = Decimal(request.POST.get('contribution', '0'))
        goal.current_amount += contribution
        if goal.current_amount >= goal.target_amount:
            goal.is_completed = True
            messages.success(request, f"🎉 Congratulations! Goal '{goal.name}' reached 100% completion!")
        else:
            messages.success(request, f"Added {currency_symbol}{contribution:.2f} toward '{goal.name}'.")
        goal.save()

    return redirect('/goals/')

# -------------------------------------------------------------
# BILLS & RECURRING PAYMENTS
# -------------------------------------------------------------
@login_required
def bills_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    bills = Bill.objects.filter(user=request.user).order_by('is_paid', 'due_date')
    return render(request, 'bills.html', {'bills': bills})

@login_required
def add_bill_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = Decimal(request.POST.get('amount', '0'))
        due_date = request.POST.get('due_date')
        category = request.POST.get('category', 'Utilities')
        is_recurring = 'is_recurring' in request.POST

        Bill.objects.create(
            user=request.user,
            name=name,
            amount=amount,
            due_date=due_date,
            category=category,
            is_recurring=is_recurring
        )
        messages.success(request, f"Bill obligation '{name}' registered.")

    return redirect('/bills/')

@login_required
def toggle_bill_view(request, id):
    currency_symbol = request.session.get('currency_symbol', '₹')
    bill = get_object_or_404(Bill, id=id, user=request.user)
    bill.is_paid = not bill.is_paid
    bill.save()
    status = "Paid ✓" if bill.is_paid else "Pending ⏳"
    messages.info(request, f"Bill '{bill.name}' marked as {status}.")
    return redirect(request.META.get('HTTP_REFERER', '/bills/'))

@login_required
def delete_bill_view(request, id):
    currency_symbol = request.session.get('currency_symbol', '₹')
    bill = get_object_or_404(Bill, id=id, user=request.user)
    bill.delete()
    messages.info(request, "Bill removed.")
    return redirect('/bills/')

# -------------------------------------------------------------
# MONTHLY AI REPORTS & PDF COMPARISON
# -------------------------------------------------------------
@login_required
def reports_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    today = date.today()
    first_day = date(today.year, today.month, 1)

    report = MonthlyReport.objects.filter(user=request.user, month=first_day).first()
    if not report:
        return redirect('/reports/generate/')

    # Comparative figures vs prior month
    prev_month = (first_day - timedelta(days=1)).replace(day=1)
    prev_report = MonthlyReport.objects.filter(user=request.user, month=prev_month).first()

    income_delta = Decimal('0.00')
    income_pct = 0.0
    expense_delta = Decimal('0.00')
    if prev_report and prev_report.total_income > 0:
        income_delta = report.total_income - prev_report.total_income
        income_pct = round(float(income_delta / prev_report.total_income) * 100, 1)
        expense_delta = report.total_expenses - prev_report.total_expenses

    return render(request, 'reports.html', {
        'report': report,
        'current_month_name': today.strftime('%B %Y'),
        'income_delta': income_delta,
        'income_pct': income_pct,
        'expense_delta': expense_delta
    })

@login_required
def generate_report_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    today = date.today()
    first_day = date(today.year, today.month, 1)

    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    total_income = sum(i.amount for i in incomes) or Decimal('0.00')
    total_expenses = sum(e.amount for e in expenses) or Decimal('0.00')
    net_savings = total_income - total_expenses
    savings_rate = round((net_savings / total_income * 100), 2) if total_income > 0 else Decimal('0.00')

    unwanted = list(expenses.filter(is_unwanted=True).values_list('title', flat=True))

    summary = (
        f"In {today.strftime('%B %Y')}, you captured {currency_symbol}{total_income:,.2f} in total revenues against {currency_symbol}{total_expenses:,.2f} in total outlays, "
        f"generating a net capital surplus of {currency_symbol}{net_savings:,.2f} (Savings Rate: {savings_rate}%). "
        f"Overall fiscal health is rated STRONG. {len(unwanted)} unwanted recurring transactions were audited."
    )

    recs = [
        f"Direct at least {currency_symbol}{net_savings * Decimal('0.60'):,.2f} into automated broad-market index investments.",
        "Maintain current grocery-to-dining out ratio to prevent food inflation.",
        f"Review and cancel flagged subscriptions to reclaim up to {currency_symbol}100/mo.f"
    ]

    report, _ = MonthlyReport.objects.update_or_create(
        user=request.user,
        month=first_day,
        defaults={
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': net_savings,
            'savings_rate': savings_rate,
            'ai_summary': summary,
            'ai_unwanted_expenses': unwanted,
            'ai_recommendations': recs,
            'ai_investment_suggestions': "Allocate 70% of current surplus to index equity ETFs and 30% to high-yield cash reserves."
        }
    )

    messages.success(request, "Monthly AI performance audit compiled.")
    return redirect('/reports/')

# -------------------------------------------------------------
# AI FINANCIAL ASSISTANT (CHATBOT API)
# -------------------------------------------------------------
@login_required
def assistant_view(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    return render(request, 'ai_assistant.html')

@csrf_exempt
@login_required
def api_ai_chat(request):
    currency_symbol = request.session.get('currency_symbol', '₹')
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            msg = data.get('message', '')
            if not msg:
                return JsonResponse({'reply': 'Please provide a valid question.'}, status=400)

            # Pass user context for personalized answers
            incomes = Income.objects.filter(user=request.user)
            expenses = Expense.objects.filter(user=request.user)
            context = {
                'monthly_income': float(sum(i.amount for i in incomes)),
                'monthly_expenses': float(sum(e.amount for e in expenses)),
                'active_goals': list(Goal.objects.filter(user=request.user).values_list('name', flat=True))
            }

            reply = ai_financial_chat(msg, context)
            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'reply': f"Error: {str(e)}"}, status=500)

    return JsonResponse({'reply': 'Invalid request method.'}, status=405)

from django.shortcuts import redirect
def set_currency(request):
    if request.method == 'POST':
        country = request.POST.get('country')
        currency_map = {
            'USA': ('$', 'dollars'),
            'India': ('₹', 'rupees'),
            'UK': ('£', 'pounds'),
            'Europe': ('€', 'euros'),
            'Japan': ('¥', 'yen'),
            'Australia': ('A$', 'dollars')
        }
        symbol, name = currency_map.get(country, ('₹', 'rupees'))
        request.session['currency_symbol'] = symbol
        request.session['currency_name'] = name
        request.session['country'] = country
    return redirect(request.META.get('HTTP_REFERER', '/'))
