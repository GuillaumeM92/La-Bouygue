from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileUpdateForm, UserLoginForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from apps.users.models import MyUser
from django.core.mail import send_mail


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
                      "Bonjour {} {}, merci d'avoir créé un compte sur le site de La Bouygue. Vous pourrez vous connecter lorsqu'un administrateur aura vérifié votre identité et activé votre compte. Vous recevrez un nouvel email vous informant de l'activation.".format(user_surname, user_name),
                      None, [user_email], fail_silently=True, )

            send_mail("La Bouygue - Nouvel Utilisateur",
                      "{} {} s'est créé un compte sur le site de la Bouygue. Merci de vérifier son identité avant d'activer son compte. Lien : https://labouygue.com/admin/activate/".format(user_surname, user_name),
                      None, ["gemacx@gmail.com"], fail_silently=True, )
            messages.success(request, str("Votre compte a été créé avec succès ! Un email de confirmation vient de vous être envoyé. Vous pourrez vous connecter dès qu'un administrateur aura validé votre compte."))
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
                form._errors["__all__"] = form.error_class([u"Désolé, votre compte est inactif pour le moment. Vous pourrez vous connecter lorsqu'un administrateur aura vérifié votre identité et activé votre compte."])
        except MyUser.DoesNotExist:
            pass
        return super().form_invalid(form)


@login_required
def profile(request):
    if request.method == "POST":
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        context = {'p_form': p_form,}

        if p_form.is_valid():
            p_form.save()
            messages.success(request, str("Votre compte a été modifié avec succès !"))
            return redirect("users-profile")

    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"p_form": p_form, 'title': 'Profil'}

    return render(request, "users/profile.html", context)
