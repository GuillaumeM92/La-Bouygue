from . import views
from django.urls import path
from .views import BudgetCreateView


urlpatterns = [
    path('budget/', views.budget, name='budget'),
    path('budget-data/', views.budget_data, name='budget-data'),
    path('budget/new/', BudgetCreateView.as_view(), name='budget-create'),
]
