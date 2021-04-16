import json

from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Work
from apps.users.models import MyUser
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import Work, WorkComment
from .forms import WorkCommentForm
from django.core.paginator import Paginator


class WorkListView(LoginRequiredMixin, ListView):
    model = Work
    template_name = "work/work.html"
    context_object_name = "works"
    ordering = ['-date_posted']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["handiwork"] = Work.objects.filter(categories=0).exclude(state=2)
        context["gardening"] = Work.objects.filter(categories=1).exclude(state=2)
        context["plumbing"] = Work.objects.filter(categories=2).exclude(state=2)
        context["masonry"] = Work.objects.filter(categories=3).exclude(state=2)
        context["other"] = Work.objects.filter(categories=4).exclude(state=2)
        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        user.works_viewed = len(Work.objects.all())
        user.save()
        return super().dispatch(request,*args, **kwargs)


class WorkDoneListView(LoginRequiredMixin, ListView):
    model = Work
    template_name = "work/work-done.html"
    context_object_name = "works"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["handiwork_done"] = Work.objects.filter(categories=0).filter(state=2)
        context["gardening_done"] = Work.objects.filter(categories=1).filter(state=2)
        context["plumbing_done"] = Work.objects.filter(categories=2).filter(state=2)
        context["masonry_done"] = Work.objects.filter(categories=3).filter(state=2)
        context["other_done"] = Work.objects.filter(categories=4).filter(state=2)
        return context


@login_required()
def work_detail(request, pk):
    template_name = "work/work-detail.html"
    work = get_object_or_404(Work, pk=pk)
    author = request.user
    new_comment = None
    form = WorkCommentForm()

    if request.method == 'POST':
        if request.POST['action'] == 'comment':
            form = WorkCommentForm(data=request.POST)
            if form.is_valid():
                # Create Comment object but don't save to database yet
                new_comment = form.save(commit=False)
                # Assign the current post and author to the comment
                new_comment.work = work
                new_comment.author = author
                # Save the comment to the database
                new_comment.save()

        elif request.POST['action'] == 'done':
            work.state = 2
            work.save()
            # Post comment saying who completed the work
            new_comment = form.save(commit=False)
            new_comment.work = work
            new_comment.author = author
            new_comment.content = "{} {} vient de signaler qu'il a terminé ce travail.".format(author.surname, author.name)
            messages.success(request, str("Travail terminé. Merci !"))
            new_comment.save()

    # Paginator
    comments = work.workcomment_set.all()
    comment_count = len(comments)
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, template_name, {'title': 'Tâche', 'work': work, 'form': form, 'page_obj': page_obj, 'comment_count': comment_count})


class UserWorkListView(LoginRequiredMixin, ListView):
    model = Work
    template_name = "work/user-work.html"
    context_object_name = "works"
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(MyUser, name=self.kwargs.get("name"), surname=self.kwargs.get("surname"))
        return Work.objects.filter(author=user).order_by("-date_posted")


class WorkCreateView(LoginRequiredMixin, CreateView):
    model = Work
    template_name = "work/work-create.html"
    fields = ["title", "content", "categories", "state", "status", "cost"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class WorkUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Work
    template_name = "work/work-update.html"
    fields = ["title", "content", "categories", "state", "status", "cost"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        work = self.get_object()
        if self.request.user == work.author or self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return False


class WorkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Work
    template_name = "work/work-delete.html"
    context_object_name = "work"
    success_url = "/work/"

    def test_func(self):
        work = self.get_object()
        if (
            self.request.user == work.author
            or self.request.user.is_superuser
            or self.request.user.has_perm("work.delete_work")
        ):
            # messages.success(self.request, str("La discussion a bien été supprimée."))
            return True
        return False


class WorkCommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = WorkComment
    template_name = 'work/workcomment-update.html'
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        work = self.get_object()
        if self.request.user == work.author:
            return True
        return False


class WorkCommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = WorkComment
    template_name = 'work/workcomment-delete.html'
    context_object_name = 'comment'
    success_url = '/work/'

    def test_func(self):
        work = self.get_object()
        if self.request.user == work.author or self.request.user.has_perm('work.delete_comment'):
            # messages.success(self.request, str("Le commentaire a bien été supprimé."))
            return True
        return False
