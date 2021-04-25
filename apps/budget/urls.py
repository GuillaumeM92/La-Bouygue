from . import views
from django.urls import path
from .views import BudgetCreateView, BudgetListView, FundingCreateView


urlpatterns = [
    path('budget/', views.budget, name='budget'),
    path('budget/detail/', BudgetListView.as_view(), name='budget-detail'),
    path('budget/data/', views.budget_data, name='budget-data'),
    path('budget/new/', BudgetCreateView.as_view(), name='budget-create'),
    path('budget/funding/', FundingCreateView.as_view(), name='funding-create'),
]
