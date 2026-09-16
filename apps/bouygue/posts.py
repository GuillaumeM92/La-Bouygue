"""What Infos pratiques, Balades and Travaux share: a post with photos, and comments.

Each section keeps its own models, URLs and page templates; the views below
hold the behaviour they have in common (who may change what, the cropping
widget, the comment thread, the messages).
"""
from client_side_image_cropping import ClientsideCroppingWidget
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.forms import modelform_factory
from django.views.generic import CreateView, DeleteView, UpdateView

from .utils import safe_next

COMMENTS_PER_PAGE = 5


def cropping_widget():
    """Photos are cropped in the browser to 1000×600 before they are sent."""
    return ClientsideCroppingWidget(width=1000, height=600, preview_width=120, preview_height=72)


def comment_form(model):
    return modelform_factory(model, fields=["content", "image"], widgets={"image": cropping_widget()})


def is_admin(user):
    return user.is_superuser or user.is_staff


class AuthorOrAdminRequired(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user == self.get_object().author or is_admin(user)


class AuthorRequired(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user == self.get_object().author


class CountsVisit:
    """Remembers how many items the member has seen, for the home page badges."""
    seen_field = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user.is_active:
            setattr(user, self.seen_field, self.model.objects.count())
            user.save()
        return super().dispatch(request, *args, **kwargs)


class CroppedImages:
    image_fields = ("image",)
    image_labels = {}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for name in self.image_fields:
            form.fields[name].widget = cropping_widget()
            if name in self.image_labels:
                form.fields[name].label = self.image_labels[name]
        return form


class PostCreateView(LoginRequiredMixin, CroppedImages, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(AuthorOrAdminRequired, CroppedImages, UpdateView):
    success_message = "La publication a été modifiée."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class PostDeleteView(AuthorOrAdminRequired, DeleteView):
    list_url = "/"
    success_message = "La publication a été supprimée."

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return self.list_url


class CommentUpdateView(AuthorRequired, CroppedImages, UpdateView):
    template_name = "posts/comment-update.html"
    fields = ["content", "image"]

    def form_valid(self, form):
        messages.success(self.request, "Le commentaire a été modifié.")
        return super().form_valid(form)


class CommentDeleteView(AuthorOrAdminRequired, DeleteView):
    template_name = "posts/comment-delete.html"
    context_object_name = "comment"
    list_url = "/"

    def get_success_url(self):
        messages.success(self.request, "Le commentaire a été supprimé.")
        return safe_next(self.request, self.list_url)


def comment_thread(request, comments, form_class, **attach):
    """The comment form and one page of comments; posts a comment when one is sent.

    Returns (context, posted): after a posted comment the view redirects, so a
    reload does not send it twice.
    """
    form = form_class()
    posted = False
    if request.method == "POST":
        bound = form_class(data=request.POST)
        if bound.is_valid():
            comment = bound.save(commit=False)
            comment.author = request.user
            for name, value in attach.items():
                setattr(comment, name, value)
            comment.save()
            messages.success(request, "Commentaire publié.")
            posted = True
        else:
            form = bound
    page_obj = Paginator(comments, COMMENTS_PER_PAGE).get_page(request.GET.get("page"))
    return {"form": form, "page_obj": page_obj, "comment_count": comments.count()}, posted
