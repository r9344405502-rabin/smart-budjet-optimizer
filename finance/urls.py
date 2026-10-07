from django.urls import path
from . import views

urlpatterns = [
    path('set_currency/', views.set_currency, name='set_currency'),
    # Public Pages
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('demo/', views.demo_view, name='demo'),

    # Authentication & Onboarding
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('setup/', views.setup_view, name='setup'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Expenses
    path('expenses/', views.expenses_view, name='expenses'),
    path('expenses/add/', views.add_expense_view, name='add_expense'),
    path('expenses/delete/<int:id>/', views.delete_expense_view, name='delete_expense'),

    # Income
    path('income/', views.income_view, name='income'),
    path('income/add/', views.add_income_view, name='add_income'),
    path('income/delete/<int:id>/', views.delete_income_view, name='delete_income'),

    # Budgets
    path('budget/', views.budget_view, name='budget'),
    path('budget/update/', views.update_budget_view, name='update_budget'),
    path('budget/generate/', views.generate_budget_view, name='generate_budget'),

    # Goals
    path('goals/', views.goals_view, name='goals'),
    path('goals/add/', views.add_goal_view, name='add_goal'),
    path('goals/contribute/<int:id>/', views.contribute_goal_view, name='contribute_goal'),

    # Bills
    path('bills/', views.bills_view, name='bills'),
    path('bills/add/', views.add_bill_view, name='add_bill'),
    path('bills/toggle/<int:id>/', views.toggle_bill_view, name='toggle_bill'),
    path('bills/delete/<int:id>/', views.delete_bill_view, name='delete_bill'),

    # Reports
    path('reports/', views.reports_view, name='reports'),
    path('reports/generate/', views.generate_report_view, name='generate_report'),

    # AI Assistant
    path('assistant/', views.assistant_view, name='assistant'),
    path('api/ai/chat/', views.api_ai_chat, name='api_ai_chat'),
]
