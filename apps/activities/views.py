from django.views.generic import ListView
from .models import Activity
from django.shortcuts import render, get_object_or_404

class ActivitiesListView(ListView):
    model = Activity
    template_name = 'activities/activities.html'
    context_object_name = 'activities'

def activity_detail(request, pk):
    template_name = 'activities/activity-detail.html'
    activity = get_object_or_404(Activity, pk=pk)

    return render(request, template_name, {'activity': activity})
