from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Activity
from apps.users.models import MyUser
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Activity, ActivityComment
from .forms import ActivityCommentForm
from django.core.paginator import Paginator


class ActivityListView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = 'activities/activities.html'
    context_object_name = 'activities'
    ordering = ['-date_posted']
    paginate_by = 7

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        user.activities_viewed = len(Activity.objects.all())
        user.save()
        return super().dispatch(request,*args, **kwargs)


@login_required
def activity_detail(request, pk):
    template_name = 'activities/activity-detail.html'
    activity = get_object_or_404(Activity, pk=pk)
    author = request.user
    new_comment = None

    if request.method == 'POST':
        form = ActivityCommentForm(data=request.POST)
        if form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = form.save(commit=False)
            # Assign the current post and author to the comment
            new_comment.activity = activity
            new_comment.author = author
            # Save the comment to the database
            new_comment.save()
            messages.success(request, str("Commentaire publié."))
        form = ActivityCommentForm()
    else:
        form = ActivityCommentForm()

    # Paginator
    comments = activity.activitycomment_set.all()
    comment_count = len(comments)
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, template_name, {'title': 'Activité', 'activity': activity, 'form': form, 'page_obj': page_obj, 'comment_count': comment_count})


class UserActivityListView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = 'activities/user-activities.html'
    context_object_name = 'activities'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(MyUser, name=self.kwargs.get('name'), surname=self.kwargs.get('surname'))
        return Activity.objects.filter(author=user).order_by('-date_posted')

class ActivityCreateView(LoginRequiredMixin, CreateView):
    model = Activity
    template_name = 'activities/activity-create.html'
    fields = ['title', 'image', 'content', 'image2', 'content2', 'difficulty', 'duration', 'distance']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ActivityUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Activity
    template_name = 'activities/activity-update.html'
    fields = ['title', 'image', 'content', 'image2', 'content2', 'difficulty', 'duration', 'distance']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, str("L'activité a bien été modifiée."))
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

    def get_success_url(self):
        messages.success(self.request, str("L'activité a bien été supprimée."))
        return '/activities/'

    def test_func(self):
        activity = self.get_object()
        if self.request.user == activity.author or self.request.user.is_superuser or self.request.user.has_perm('activities.delete_activity'):
            return True
        return False


class ActivityCommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ActivityComment
    template_name = 'activities/activitycomment-update.html'
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, str("Le commentaire a bien été modifié."))
        return super().form_valid(form)

    def test_func(self):
        activity = self.get_object()
        if self.request.user == activity.author:
            return True
        return False


class ActivityCommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ActivityComment
    template_name = 'activities/activitycomment-delete.html'
    context_object_name = 'comment'

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            messages.success(self.request, str("Le commentaire a bien été supprimé."))
            return next_url # return next url for redirection
        return '/activities/' # return some other url if next parameter not present

    def test_func(self):
        activity = self.get_object()
        if self.request.user == activity.author or self.request.user.has_perm('activities.delete_comment'):
            return True
        return False
