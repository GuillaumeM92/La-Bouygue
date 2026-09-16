from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from apps.bouygue import posts
from .models import Work, WorkComment

FIELDS = ["title", "content", "image", "categories", "state", "status", "cost"]
DONE = 2
CATEGORIES = ["handiwork", "gardening", "plumbing", "masonry", "other"]


class WorkListView(posts.CountsVisit, LoginRequiredMixin, ListView):
    model = Work
    seen_field = "works_viewed"
    template_name = "work/work.html"
    context_object_name = "works"
    ordering = ["-date_posted"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for number, name in enumerate(CATEGORIES):
            context[name] = Work.objects.filter(categories=number).exclude(state=DONE)
        return context


class WorkDoneListView(LoginRequiredMixin, ListView):
    model = Work
    template_name = "work/work-done.html"
    context_object_name = "works"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for number, name in enumerate(CATEGORIES):
            context[name + "_done"] = Work.objects.filter(categories=number, state=DONE)
        return context


@login_required
def work_detail(request, pk):
    work = get_object_or_404(Work, pk=pk)
    if request.method == "POST" and request.POST.get("action") == "done":
        work.state = DONE
        work.save()
        # A comment says who completed the work
        WorkComment.objects.create(
            work=work, author=request.user,
            content="{} {} vient de signaler qu'il a terminé ce travail.".format(
                request.user.surname, request.user.name))
        messages.success(request, "Travail terminé. Merci !")
        return redirect("work-detail", pk=pk)
    context, posted = posts.comment_thread(request, work.workcomment_set.all(),
                                           posts.comment_form(WorkComment), work, work=work)
    if posted:
        return redirect("work-detail", pk=pk)
    return render(request, "work/work-detail.html", dict(context, title="Tâche", work=work))


class WorkCreateView(posts.PostCreateView):
    model = Work
    template_name = "work/work-create.html"
    fields = FIELDS


class WorkUpdateView(posts.PostUpdateView):
    model = Work
    template_name = "work/work-update.html"
    fields = FIELDS
    success_message = "Le travail a été modifié."


class WorkDeleteView(posts.PostDeleteView):
    model = Work
    template_name = "work/work-delete.html"
    context_object_name = "work"
    list_url = "/work/"
    success_message = "Le travail a été supprimé."

    def test_func(self):
        return super().test_func() or self.request.user.has_perm("work.delete_work")


class WorkCommentUpdateView(posts.CommentUpdateView):
    model = WorkComment


class WorkCommentDeleteView(posts.CommentDeleteView):
    model = WorkComment
    list_url = "/work/"
