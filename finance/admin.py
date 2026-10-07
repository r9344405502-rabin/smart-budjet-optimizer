from django.contrib import admin
from .models import Profile, Income, Expense, Budget, Goal, Bill, MonthlyReport

admin.site.site_header = "Smart Budget Optimiser Administration"
admin.site.site_title = "Smart Budget Optimiser Admin Portal"
admin.site.index_title = "Financial Database & Operations Control"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'google_id', 'monthly_savings_target', 'is_onboarded', 'created_at')
    list_filter = ('is_onboarded', 'created_at')
    search_fields = ('user__username', 'user__email', 'google_id')

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('source_name', 'user', 'amount', 'category', 'is_recurring', 'date')
    list_filter = ('category', 'is_recurring', 'date')
    search_fields = ('source_name', 'user__username')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'amount', 'ai_category', 'is_unwanted', 'date')
    list_filter = ('ai_category', 'is_unwanted', 'date')
    search_fields = ('title', 'user__username', 'description')
    list_editable = ('is_unwanted',)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'total_allocated', 'ai_generated', 'updated_at')
    list_filter = ('ai_generated', 'month')
    search_fields = ('user__username',)

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'goal_type', 'target_amount', 'current_amount', 'deadline', 'is_completed')
    list_filter = ('goal_type', 'is_completed')
    search_fields = ('name', 'user__username')
    list_editable = ('is_completed',)

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'amount', 'due_date', 'category', 'is_paid')
    list_filter = ('is_paid', 'is_recurring', 'category')
    search_fields = ('name', 'user__username')
    list_editable = ('is_paid',)

@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'total_income', 'total_expenses', 'net_savings', 'savings_rate', 'created_at')
    list_filter = ('month',)
    search_fields = ('user__username',)
