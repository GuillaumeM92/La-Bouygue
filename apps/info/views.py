from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from apps.users.models import MyUser
from .models import InfoPost, InfoComment
from .forms import InfoCommentForm
from django.core.paginator import Paginator
from django.core.mail import send_mail
from client_side_image_cropping import ClientsideCroppingWidget


class InfoPostListView(LoginRequiredMixin, ListView):
    model = InfoPost
    template_name = 'info/info.html'
    context_object_name = 'infoposts'
    ordering = ['-date_posted']
    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        user.informations_viewed = len(InfoPost.objects.all())
        if user.is_authenticated and user.is_active:
            user.save()
        return super().dispatch(request, *args, **kwargs)


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
            messages.success(request, str("Commentaire publié."))
        form = InfoCommentForm()
    else:
        form = InfoCommentForm()

    # Paginator
    comments = infopost.infocomment_set.all()
    comment_count = len(comments)
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, template_name, {
        'title': 'Information', 'infopost': infopost, 'form': form,
        'page_obj': page_obj, 'comment_count': comment_count})


class InfoPostCreateView(LoginRequiredMixin, CreateView):
    model = InfoPost
    template_name = 'info/infopost-create.html'
    fields = ['title', 'content', 'image']

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


class InfoPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = InfoPost
    template_name = 'info/infopost-update.html'
    fields = ['title', 'content', 'image']

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
        messages.success(self.request, str("L'information a bien été modifiée."))
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        user = self.request.user
        if user == post.author or user.is_superuser or user.is_staff:
            return True
        return False


class InfoPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = InfoPost
    template_name = 'info/infopost-delete.html'
    context_object_name = 'infopost'

    def get_success_url(self):
        messages.success(self.request, str("L'information a bien été supprimée."))
        return '/info/'

    def test_func(self):
        post = self.get_object()
        user = self.request.user
        if user == post.author or user.is_superuser or user.is_staff:
            return True
        return False


class InfoCommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = InfoComment
    template_name = 'info/infocomment-update.html'
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
        info = self.get_object()
        if self.request.user == info.author:
            return True
        return False


class InfoCommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = InfoComment
    template_name = 'info/infocomment-delete.html'
    context_object_name = 'comment'

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            messages.success(self.request, str("Le commentaire a bien été supprimé."))
            return next_url  # return next url for redirection
        return '/info/'  # return some other url if next parameter not present

    def test_func(self):
        info = self.get_object()
        user = self.request.user
        if user == info.author or user.is_superuser or user.is_staff:
            return True
        return False


class ActivateUsersListView(LoginRequiredMixin, ListView):
    model = MyUser
    template_name = 'admin/activate-users.html'
    context_object_name = 'users'
    ordering = ['-date_joined']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_users"] = MyUser.objects.filter(is_active=True).order_by("-date_joined")
        context["inactive_users"] = MyUser.objects.filter(is_active=False).order_by("-date_joined")
        return context

    def post(self, request, *args, **kwargs):
        if self.request.user.is_superuser or self.request.user.is_staff:
            if request.method == 'POST':
                user_id = request.POST['action']
                user = MyUser.objects.get(id=user_id)
                user.is_active = True
                user.save()
                user_email = user.email
                send_mail("La Bouygue - Compte Activé",
                          ("Votre compte La Bouygue vient d'être activé. "
                           "Vous pouvez désormais vous connecter en cliquant "
                           "sur le lien suivant : https://labouygue.fr/login/"),
                          None, [user_email], fail_silently=True, )
                messages.success(self.request, str("Utilisateur activé !"))
            return super().get(request, *args, **kwargs)
        else:
            return render(request, 'errors/error-403.html', status=403)


class AllUsersListView(LoginRequiredMixin, ListView):
    model = MyUser
    template_name = 'info/all-users.html'
    context_object_name = 'users'
    ordering = ['surname']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_users"] = MyUser.objects.all()
        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        user.users_viewed = len(MyUser.objects.all())
        if user.is_authenticated and user.is_active:
            user.save()
        return super().dispatch(request, *args, **kwargs)