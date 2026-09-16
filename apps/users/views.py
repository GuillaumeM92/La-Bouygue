import unicodedata
from urllib.parse import urlencode

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from apps.users.models import MyUser
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from . import antispam
from .emails import send_quietly
from .forms import UserRegisterForm, ProfileUpdateForm, UserLoginForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid() and not antispam.registration_allowed():
            messages.error(request, str(
                "Trop d'inscriptions en peu de temps. Merci de réessayer d'ici une heure."))
        elif form.is_valid():
            antispam.count_registration()
            user = form.save()
            # Make user not active by default
            user.is_active = False
            user.save()
            user_email = form.cleaned_data['email']
            user_name = form.cleaned_data['name']
            user_surname = form.cleaned_data['surname']
            send_quietly("La Bouygue - Bienvenue",
                         ("Bonjour {} {}, merci d'avoir créé un compte sur le site de La Bouygue. "
                          "Vous pourrez vous connecter lorsqu'un administrateur aura vérifié votre "
                          "identité et activé votre compte. Vous recevrez un nouvel email vous "
                          "informant de l'activation.").format(user_surname, user_name),
                         user_email)

            # Whoever can activate accounts hears about the new one
            administrators = MyUser.objects.filter(
                Q(is_staff=True) | Q(is_superuser=True), is_active=True
            ).values_list("email", flat=True)
            for administrator in administrators:
                send_quietly("La Bouygue - Nouvel Utilisateur",
                             ("{} {} ({}) s'est créé un compte sur le site de la Bouygue. Merci "
                              "de vérifier son identité avant d'activer son compte. Lien : "
                              "https://labouygue.fr/info/admin/activate/").format(
                                 user_surname, user_name, user_email),
                             administrator)
            messages.success(request, str(
                "Votre compte a été créé avec succès ! Un email de confirmation vient de vous "
                "être envoyé. Vous pourrez vous connecter dès qu'un administrateur aura "
                "validé votre compte."))
            return redirect("users-login")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {'title': 'S\'enregistrer', "form": form})


class MyLoginView(SuccessMessageMixin, LoginView):
    form_class = UserLoginForm


@login_required
def profile(request):
    if request.method == "POST":
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        context = {'p_form': p_form, }

        if p_form.is_valid():
            p_form.save()
            messages.success(request, str("Votre compte a été modifié avec succès !"))
            return redirect("users-profile")

    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"p_form": p_form, 'title': 'Profil'}

    return render(request, "users/profile.html", context)


class UserProfileListView(LoginRequiredMixin, ListView):
    model = MyUser
    template_name = 'users/profile-view.html'
    context_object_name = 'clicked_user'

    def get_queryset(self):
        clicked_user = get_object_or_404(MyUser, id=self.kwargs.get('id'))
        return clicked_user


class UserAppListView(LoginRequiredMixin, ListView):
    """What one member published in one section."""
    template_name = 'users/user-list.html'
    context_object_name = 'app'
    paginate_by = 5
    SECTIONS = {
        'activité(s)': 'activity_set',
        'information(s)': 'infopost_set',
        'tâche(s)': 'work_set',
    }

    def get_queryset(self):
        self.clicked_user = get_object_or_404(MyUser, id=self.kwargs.get('id'))
        related = self.SECTIONS.get(self.kwargs.get('app'))
        if related is None:
            raise Http404
        return getattr(self.clicked_user, related).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clicked_user"] = self.clicked_user
        return context


class ActivateUsersListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = MyUser
    template_name = 'users/activate-users.html'
    context_object_name = 'users'
    ordering = ['-date_joined']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_users"] = MyUser.objects.filter(is_active=True).order_by("-date_joined")
        context["inactive_users"] = MyUser.objects.filter(is_active=False).order_by("-date_joined")
        return context

    def test_func(self):
        # The page lists every account, pending ones included: administrators only
        user = self.request.user
        return user.is_superuser or user.is_staff

    def post(self, request, *args, **kwargs):
        refused = request.POST.get('refuse')
        if refused:
            # Only a registration that was never used: an account that has
            # logged in before owns stays and messages, deleted with it.
            user = get_object_or_404(MyUser, id=refused if refused.isdigit() else 0,
                                     is_active=False, last_login__isnull=True)
            label = f"{user.surname} {user.name}".strip() or user.email
            user.delete()
            messages.success(self.request, f"Demande de {label} refusée : le compte a été supprimé.")
            return redirect('activate-users')
        activated = request.POST.get('action', '')
        user = get_object_or_404(MyUser, id=activated if activated.isdigit() else 0, is_active=False)
        user.is_active = True
        user.save()
        send_quietly("La Bouygue - Compte Activé",
                     ("Votre compte La Bouygue vient d'être activé. "
                      "Vous pouvez désormais vous connecter en cliquant "
                      "sur le lien suivant : https://labouygue.fr/login/"),
                     user.email)
        messages.success(self.request, str("Utilisateur activé !"))
        return redirect('activate-users')


def _folded(text):
    """Lower case, without accents: "Élodie" -> "elodie"."""
    decomposed = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


class AllUsersListView(LoginRequiredMixin, ListView):
    # Accounts waiting for activation are not members yet
    queryset = MyUser.objects.filter(is_active=True)
    template_name = 'users/all-users.html'
    context_object_name = 'users'
    ordering = ['surname']
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        words = _folded(self.request.GET.get("q", "")).split()
        if not words:
            return queryset
        # "helene dup" finds Hélène Dupont: every word, accents and case aside,
        # must be in the first or last name. A few dozen members: filtered here.
        return [member for member in queryset
                if all(word in _folded(f"{member.surname} {member.name}") for word in words)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        if context["query"]:
            context["pagination_query"] = "&" + urlencode({"q": context["query"]})
        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        user.users_viewed = MyUser.objects.filter(is_active=True).count()
        if user.is_authenticated and user.is_active:
            user.save()
        return super().dispatch(request, *args, **kwargs)
