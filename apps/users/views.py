from django.core.mail import send_mail
from apps.users.models import MyUser
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileUpdateForm, UserLoginForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView
from apps.blog.models import Post


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Make user not active by default
            user.is_active = False
            user.save()
            user_email = form.data['email']
            user_name = form.data['name']
            user_surname = form.data['surname']
            send_mail("La Bouygue - Bienvenue",
                      ("Bonjour {} {}, merci d'avoir créé un compte sur le site de La Bouygue. "
                       "Vous pourrez vous connecter lorsqu'un administrateur aura vérifié votre "
                       "identité et activé votre compte. Vous recevrez un nouvel email vous "
                       "informant de l'activation.").format(user_surname, user_name),
                      None, [user_email], fail_silently=True, )

            send_mail("La Bouygue - Nouvel Utilisateur",
                      ("{} {} s'est créé un compte sur le site de la Bouygue. Merci de vérifier "
                       "son identité avant d'activer son compte. Lien : "
                       "https://labouygue.com/info/admin/activate/").format(user_surname, user_name),
                      None, ["gemacx@gmail.com", "x.merle@orange.fr", "patrice16.merle@orange.fr", "paulhenri.merle78@gmail.com"], fail_silently=True, )
            messages.success(request, str(
                "Votre compte a été créé avec succès ! Un email de confirmation vient de vous "
                "être envoyé. Vous pourrez vous connecter dès qu'un administrateur aura "
                "validé votre compte."))
            return redirect("users-login")
        else:
            if "captcha" in form.errors:
                messages.error(request, str("N'oubliez pas de remplir le captcha."))
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {'title': 'S\'enregistrer', "form": form})


class MyLoginView(SuccessMessageMixin, LoginView):
    form_class = UserLoginForm

    def form_invalid(self, form):
        user_email = form.data['username']
        print(user_email)
        try:
            user = MyUser.objects.get(email=user_email)
            if not user.is_active:
                form._errors["__all__"] = form.error_class(
                    [(u"Désolé, votre compte est inactif pour le moment. Vous pourrez vous "
                      "connecter lorsqu'un administrateur aura vérifié votre "
                      "identité et activé votre compte.")])
        except MyUser.DoesNotExist:
            pass
        return super().form_invalid(form)


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
        clicked_user = MyUser.objects.get(id=self.kwargs.get('id'))
        return clicked_user


class UserAppListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'users/user-list.html'
    context_object_name = 'app'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = MyUser.objects.get(id=self.kwargs.get('id'))
        app = self.kwargs.get('app')

        if app == 'discussion(s)':
            context["app"] = user.post_set.all()
        elif app == 'activité(s)':
            context["app"] = user.activity_set.all()
        elif app == 'information(s)':
            context["app"] = user.infopost_set.all()
        elif app == 'tâche(s)':
            context["app"] = user.work_set.all()

        context["clicked_user"] = user
        return context

    def get_queryset(self):
        posts = MyUser.objects.get(id=self.kwargs.get('id')).post_set.all()
        return posts
