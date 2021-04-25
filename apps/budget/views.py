from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView
from django.http import JsonResponse
from .models import Budget


@login_required
def budget(request):
    current_budget = Budget.objects.order_by('-date_posted').first()
    previous_budget = Budget.objects.order_by('-date_posted').all()[1]
    difference = current_budget.total - previous_budget.total
    return render(request, 'budget/budget.html', {'title': 'Budget', 'current_budget': current_budget, 'difference': difference})


@login_required
def budget_data(request):
    # wrap in list(), because QuerySet is not JSON serializable
    data = list(Budget.objects.all().values())
    return JsonResponse(data, safe=False)


class BudgetCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Budget
    template_name = 'budget/budget-create.html'
    fields = ['total', 'description']
    success_url = '/budget/'

    def test_func(self):
        user = self.request.user
        if user.is_superuser or user.user.is_staff:
            return True
        return False
