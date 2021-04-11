from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Work
from apps.users.models import MyUser
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class WorkListView(ListView):
    model = Work
    template_name = "work/work.html"
    context_object_name = "works"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["handiwork"] = Work.objects.filter(categories=0)
        context["gardening"] = Work.objects.filter(categories=1)
        context["plumbing"] = Work.objects.filter(categories=2)
        context["masonry"] = Work.objects.filter(categories=3)
        context["other"] = Work.objects.filter(categories=4)
        return context

def work_detail(request, pk):
    template_name = "work/work-detail.html"
    work = get_object_or_404(Work, pk=pk)

    return render(request, template_name, {"work": work})


class UserWorkListView(ListView):
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
