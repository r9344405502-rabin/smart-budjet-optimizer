from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    google_id = models.CharField(max_length=255, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    is_onboarded = models.BooleanField(default=False)
    monthly_savings_target = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class Income(models.Model):
    CATEGORY_CHOICES = [
        ('Salary', 'Salary / Employment'),
        ('Freelance', 'Freelancing / Side Hustle'),
        ('Investment', 'Investments & Dividends'),
        ('Business', 'Business Income'),
        ('Other', 'Other Income'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    source_name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Salary')
    is_recurring = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return f"{self.source_name} - ₹{self.amount}"

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Housing & Rent', 'Housing & Rent'),
        ('Groceries & Food', 'Groceries & Food'),
        ('Dining Out & Delivery', 'Dining Out & Delivery'),
        ('Transportation', 'Transportation & Fuel'),
        ('Utilities & Bills', 'Utilities & Bills'),
        ('Entertainment & Leisure', 'Entertainment & Leisure'),
        ('Subscriptions', 'Subscriptions & Memberships'),
        ('Shopping & Personal', 'Shopping & Personal'),
        ('Healthcare & Fitness', 'Healthcare & Fitness'),
        ('Travel & Holiday', 'Travel & Holiday'),
        ('Education & Self-Improvement', 'Education & Self-Improvement'),
        ('Miscellaneous', 'Miscellaneous'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    ai_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Miscellaneous')
    is_unwanted = models.BooleanField(default=False, help_text="Flagged by AI as potentially wasteful or recurring unused")
    ai_flag_reason = models.TextField(blank=True, null=True, help_text="Reason provided by AI for unwanted expense")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.ai_category})"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    month = models.DateField(help_text="First day of the budget month")
    total_allocated = models.DecimalField(max_digits=12, decimal_places=2)
    ai_generated = models.BooleanField(default=True)
    details = models.JSONField(default=dict, help_text="Category -> Limit mapping")
    ai_insights = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'month')

    def __str__(self):
        return f"Budget {self.month.strftime('%B %Y')} - {self.user.username}"

class Goal(models.Model):
    GOAL_TYPES = [
        ('Savings', 'Emergency / Liquid Savings'),
        ('Purchase', 'Major Asset or Purchase'),
        ('Investment', 'Long-Term Investment & Wealth'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=150)
    goal_type = models.CharField(max_length=50, choices=GOAL_TYPES, default='Savings')
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deadline = models.DateField(blank=True, null=True)
    ai_suggestion = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            pct = (float(self.current_amount) / float(self.target_amount)) * 100
            return min(round(pct, 1), 100.0)
        return 0.0

    def __str__(self):
        return f"{self.name} (₹{self.current_amount} / ₹{self.target_amount})"

class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    category = models.CharField(max_length=100, default='Utilities & Services')
    is_paid = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return f"{self.name} - ₹{self.amount} (Due: {self.due_date})"

class MonthlyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    month = models.DateField()
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    savings_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    ai_summary = models.TextField()
    ai_unwanted_expenses = models.JSONField(default=list)
    ai_recommendations = models.JSONField(default=list)
    ai_investment_suggestions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    class Meta:
        unique_together = ('user', 'month')

    def __str__(self):
        return f"Report {self.month.strftime('%B %Y')} - {self.user.username}"
