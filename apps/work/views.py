from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from apps.users.models import MyUser
from .models import Work, WorkComment
from .forms import WorkCommentForm
from django.core.paginator import Paginator
from client_side_image_cropping import ClientsideCroppingWidget


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
        if user.is_authenticated and user.is_active:
            user.save()
        return super().dispatch(request, *args, **kwargs)


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
                messages.success(request, str("Commentaire publié."))
            form = WorkCommentForm()

        elif request.POST['action'] == 'done':
            work.state = 2
            work.save()
            # Post comment saying who completed the work
            new_comment = form.save(commit=False)
            new_comment.work = work
            new_comment.author = author
            new_comment.content = "{} {} vient de signaler qu'il a terminé ce travail.".format(
                author.surname, author.name)
            messages.success(request, str("Travail terminé. Merci !"))
            new_comment.save()

    # Paginator
    comments = work.workcomment_set.all()
    comment_count = len(comments)
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,
                  template_name,
                  {'title': 'Tâche',
                   'work': work,
                   'form': form,
                   'page_obj': page_obj,
                   'comment_count': comment_count})


class WorkCreateView(LoginRequiredMixin, CreateView):
    model = Work
    template_name = 'work/work-create.html'
    fields = ['title', 'content', 'image', 'categories', 'state', 'status', 'cost', ]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request = self.request
        form.fields['image'].widget = ClientsideCroppingWidget(
            width=1000,
            height=600,
            preview_width=120,
            preview_height=72,
        )
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class WorkUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Work
    template_name = "work/work-update.html"
    fields = ["title", "content", "image", "categories", "state", "status", "cost"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request = self.request
        form.fields['image'].widget = ClientsideCroppingWidget(
            width=1000,
            height=600,
            preview_width=120,
            preview_height=72,
        )
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, str("Le travail a bien été modifié."))
        return super().form_valid(form)

    def test_func(self):
        work = self.get_object()
        user = self.request.user
        if user == work.author or user.is_superuser or user.is_staff:
            return True
        return False


class WorkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Work
    template_name = "work/work-delete.html"
    context_object_name = "work"

    def get_success_url(self):
        messages.success(self.request, str("Le travail a bien été supprimé."))
        return "/work/"

    def test_func(self):
        work = self.get_object()
        if (
            self.request.user == work.author
            or self.request.user.is_superuser
            or self.request.user.has_perm("work.delete_work")
        ):
            return True
        return False


class WorkCommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = WorkComment
    template_name = 'work/workcomment-update.html'
    fields = ['content', 'image']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request = self.request
        form.fields['image'].widget = ClientsideCroppingWidget(
            width=1000,
            height=600,
            preview_width=120,
            preview_height=72,
        )
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, str("Le commentaire a bien été modifié."))
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

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            messages.success(self.request, str("Le commentaire a bien été supprimé."))
            return next_url  # return next url for redirection
        return '/work/'  # return some other url if next parameter not present

    def test_func(self):
        work = self.get_object()
        user = self.request.user
        if user == work.author or user.is_superuser or user.is_staff:
            return True
        return False
