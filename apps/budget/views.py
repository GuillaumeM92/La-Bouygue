from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, UpdateView
from django.http import JsonResponse
from .models import Budget, Funding


@login_required
def budget(request):
    current_budget = Budget.objects.order_by('-date_posted').first()
    previous_budget = Budget.objects.order_by('-date_posted').all()
    if len(previous_budget) > 1:
        previous_budget = previous_budget[1]
        difference = current_budget.total - previous_budget.total
    else:
        difference = None
    funding = Funding.objects.order_by('-date_posted').first()
    if funding:
        funding_percent = int((funding.progress / funding.goal) * 100)
    else:
        funding_percent = None
    return render(request, 'budget/budget.html', {'title': 'Budget', 'current_budget': current_budget, 'difference': difference, 'funding': funding, 'funding_percent': funding_percent})


@login_required
def budget_data(request):
    # wrap in list(), because QuerySet is not JSON serializable
    data = list(Budget.objects.all().values())
    for item in data:
        item['date_posted'] = "{}/{}".format(
            f"{item['date_posted'].month:02d}", item['date_posted'].year)
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


class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'budget/budget-detail.html'
    context_object_name = 'budget_detail'
    ordering = ['-date_posted']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["budget_entries"] = Budget.objects.all()
        return context


class FundingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Funding
    template_name = 'budget/funding-create.html'
    fields = ['progress', 'goal']
    success_url = '/budget/'

    def test_func(self):
        user = self.request.user
        if user.is_superuser or user.user.is_staff:
            return True
        return False
