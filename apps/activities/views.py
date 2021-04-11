from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Activity
from apps.users.models import MyUser
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class ActivityListView(ListView):
    model = Activity
    template_name = 'activities/activities.html'
    context_object_name = 'activities'

def activity_detail(request, pk):
    template_name = 'activities/activity-detail.html'
    activity = get_object_or_404(Activity, pk=pk)

    return render(request, template_name, {'activity': activity})

class UserActivityListView(ListView):
    model = Activity
    template_name = 'activities/user-activities.html'
    context_object_name = 'activities'
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(MyUser, name=self.kwargs.get('name'), surname=self.kwargs.get('surname'))
        return Activity.objects.filter(author=user).order_by('-date_posted')

class ActivityCreateView(LoginRequiredMixin, CreateView):
    model = Activity
    template_name = 'activities/activity-create.html'
    fields = ['title', 'content', 'difficulty', 'duration', 'distance', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ActivityUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Activity
    template_name = 'activities/activity-update.html'
    fields = ['title', 'content', 'difficulty', 'duration', 'distance', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        activity = self.get_object()
        if self.request.user == activity.author or self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return False

class ActivityDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Activity
    template_name = 'activities/activity-delete.html'
    context_object_name = 'activity'
    success_url = '/activities/'

    def test_func(self):
        activity = self.get_object()
        if self.request.user == activity.author or self.request.user.is_superuser or self.request.user.has_perm('activities.delete_activity'):
            # messages.success(self.request, str("La discussion a bien été supprimée."))
            return True
        return False
