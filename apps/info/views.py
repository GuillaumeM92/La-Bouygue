from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.models import Permission
from apps.users.models import MyUser
from .models import InfoPost, InfoComment
from .forms import InfoCommentForm
from django.core.paginator import Paginator


class InfoPostListView(LoginRequiredMixin, ListView):
    model = InfoPost
    template_name = 'info/info.html'
    context_object_name = 'infoposts'
    ordering = ['-date_posted']
    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        user.informations_viewed = len(InfoPost.objects.all())
        user.save()
        return super().dispatch(request,*args, **kwargs)


class UserInfoPostListView(LoginRequiredMixin, ListView):
    model = InfoPost
    template_name = 'info/user-infoposts.html'
    context_object_name = 'infoposts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(MyUser, name=self.kwargs.get('name'), surname=self.kwargs.get('surname'))
        return InfoPost.objects.filter(author=user).order_by('-date_posted')


@login_required()
def infopost_detail(request, pk):
    template_name = 'info/infopost-detail.html'
    infopost = get_object_or_404(InfoPost, pk=pk)
    author = request.user
    new_comment = None

    if request.method == 'POST':
        form = InfoCommentForm(data=request.POST)
        if form.is_valid():

            # Create Comment object but don't save to database yet
            new_comment = form.save(commit=False)
            # Assign the current post and author to the comment
            new_comment.infopost = infopost
            new_comment.author = author
            # Save the comment to the database
            new_comment.save()
    else:
        form = InfoCommentForm()

    # Paginator
    comments = infopost.infocomment_set.all()
    comment_count = len(comments)
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, template_name, {'title': 'Information', 'infopost': infopost, 'form': form, 'page_obj': page_obj, 'comment_count': comment_count})


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


class InfoCommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = InfoComment
    template_name = 'info/infocomment-update.html'
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        info = self.get_object()
        if self.request.user == info.author:
            return True
        return False


class InfoCommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = InfoComment
    template_name = 'info/infocomment-delete.html'
    context_object_name = 'comment'
    success_url = '/info/'

    def test_func(self):
        info = self.get_object()
        if self.request.user == info.author or self.request.user.has_perm('info.delete_comment'):
            # messages.success(self.request, str("Le commentaire a bien été supprimé."))
            return True
        return False
