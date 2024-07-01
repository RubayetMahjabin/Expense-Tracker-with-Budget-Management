from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('log-expense/', views.log_expense, name='log_expense'),
    path('list-expenses/', views.list_expenses, name='list_expenses'),
    path('set-budget/', views.set_budget, name='set_budget'),
    path('summary-report/', views.summary_report, name='summary_report'),
]
