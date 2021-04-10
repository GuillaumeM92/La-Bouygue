from django.shortcuts import render

def budget(request):
    return render(request, 'budget.html')
