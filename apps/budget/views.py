from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def budget(request):
    return render(request, 'budget.html', {'title': 'Budget'} )
