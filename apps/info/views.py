from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.models import Permission
from apps.users.models import MyUser
from .models import InfoPost


class InfoPostListView(ListView):
    model = InfoPost
    template_name = 'info/info.html'
    context_object_name = 'infoposts'
    ordering = ['-date_posted']
    paginate_by = 4

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        user.informations_read = len(InfoPost.objects.all())
        user.save()
        return super().dispatch(request,*args, **kwargs)

class UserInfoPostListView(ListView):
    model = InfoPost
    template_name = 'info/user-infoposts.html'
    context_object_name = 'infoposts'
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(MyUser, name=self.kwargs.get('name'), surname=self.kwargs.get('surname'))
        return InfoPost.objects.filter(author=user).order_by('-date_posted')


def infopost_detail(request, pk):
    template_name = 'info/infopost-detail.html'
    infopost = get_object_or_404(InfoPost, pk=pk)

    return render(request, template_name, {'infopost': infopost})

class InfoPostCreateView(LoginRequiredMixin, CreateView):
    model = InfoPost
    template_name = 'info/infopost-create.html'
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class InfoPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = InfoPost
    template_name = 'info/infopost-update.html'
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return False

class InfoPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = InfoPost
    template_name = 'info/infopost-delete.html'
    context_object_name = 'infopost'
    success_url = '/info/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser or self.request.user.has_perm('info.delete_infopost'):
            # messages.success(self.request, str("La discussion a bien été supprimée."))
            return True
        return False
