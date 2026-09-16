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
