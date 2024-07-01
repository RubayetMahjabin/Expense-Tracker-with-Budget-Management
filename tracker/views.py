# tracker/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Category, Budget
from .forms import ExpenseForm, BudgetForm
from django.db.models import Sum
from django.contrib import messages
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def log_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense logged successfully.')
            return redirect('log_expense')
    else:
        form = ExpenseForm()
    return render(request, 'tracker/log_expense.html', {'form': form})

@login_required
def list_expenses(request):
    expenses = Expense.objects.filter(user=request.user)
    categories = Category.objects.all()

    if request.method == 'POST':
        category_name = request.POST.get('category')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if category_name:
            expenses = expenses.filter(category__name=category_name)
        
        if start_date and end_date:
            expenses = expenses.filter(date__range=[start_date, end_date])

    for category in categories:
        try:
            budget = Budget.objects.get(category=category, user=request.user).amount
            total_expenses = Expense.objects.filter(category=category, user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
            if total_expenses > budget:
                messages.warning(request, f'You have exceeded your budget for {category.name}.')
        except Budget.DoesNotExist:
            pass

    context = {
        'expenses': expenses,
        'categories': categories,
    }

    return render(request, 'tracker/list_expenses.html', context)

@login_required
def set_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget set successfully.')
            return redirect('set_budget')
    else:
        form = BudgetForm()
    
    return render(request, 'tracker/set_budget.html', {'form': form})

@login_required
def summary_report(request):
    categories = Category.objects.all()
    report = []

    for category in categories:
        try:
            budget = Budget.objects.get(category=category, user=request.user).amount
            total_expenses = Expense.objects.filter(category=category, user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
            remaining_budget = budget - total_expenses
            report.append({
                'category': category.name,
                'budget': budget,
                'total_expenses': total_expenses,
                'remaining_budget': remaining_budget
            })
        except Budget.DoesNotExist:
            report.append({
                'category': category.name,
                'budget': 0,
                'total_expenses': 0,
                'remaining_budget': 0
            })

    fig, ax = plt.subplots()
    categories_names = [entry['category'] for entry in report]
    total_expenses = [entry['total_expenses'] for entry in report]
    budget = [entry['budget'] for entry in report]
    remaining_budget = [entry['remaining_budget'] for entry in report]

    ax.bar(categories_names, budget, label='Budget')
    ax.bar(categories_names, total_expenses, label='Total Expenses')
    ax.plot(categories_names, remaining_budget, label='Remaining Budget', marker='o')

    ax.set_xlabel('Categories')
    ax.set_ylabel('Amount')
    ax.set_title('Summary Report')
    ax.legend()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    context = {
        'report': report,
        'plot_data': plot_data
    }

    return render(request, 'tracker/summary_report.html', context)
