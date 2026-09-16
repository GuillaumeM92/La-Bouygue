from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from apps.bouygue import posts
from .models import InfoComment, InfoPost

FIELDS = ["title", "content", "image"]


class InfoPostListView(posts.CountsVisit, LoginRequiredMixin, ListView):
    model = InfoPost
    seen_field = "informations_viewed"
    template_name = "info/info.html"
    context_object_name = "infoposts"
    ordering = ["-date_posted"]
    paginate_by = 5


@login_required
def infopost_detail(request, pk):
    infopost = get_object_or_404(InfoPost, pk=pk)
    context, posted = posts.comment_thread(request, infopost.infocomment_set.all(),
                                           posts.comment_form(InfoComment), infopost=infopost)
    if posted:
        return redirect("infopost-detail", pk=pk)
    return render(request, "info/infopost-detail.html",
                  dict(context, title="Information", infopost=infopost))


class InfoPostCreateView(posts.PostCreateView):
    """Practical information is written by administrators."""
    model = InfoPost
    template_name = "info/infopost-create.html"
    fields = FIELDS

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not posts.is_admin(request.user):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class InfoPostUpdateView(posts.PostUpdateView):
    model = InfoPost
    template_name = "info/infopost-update.html"
    fields = FIELDS
    success_message = "L'information a été modifiée."


class InfoPostDeleteView(posts.PostDeleteView):
    model = InfoPost
    template_name = "info/infopost-delete.html"
    context_object_name = "infopost"
    list_url = "/info/"
    success_message = "L'information a été supprimée."


class InfoCommentUpdateView(posts.CommentUpdateView):
    model = InfoComment


class InfoCommentDeleteView(posts.CommentDeleteView):
    model = InfoComment
    list_url = "/info/"
