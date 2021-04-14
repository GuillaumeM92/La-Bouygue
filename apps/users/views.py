from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileUpdateForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from apps.users.models import MyUser
from django.core.exceptions import ValidationError


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Make user not active by default
            user.is_active = False
            user.save()
            messages.success(request, str("Votre compte a été créé avec succès ! Vous pourrez vous connecter dès qu'un administrateur aura validé votre compte."))
            return redirect("users-login")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {'title': 'S\'enregistrer', "form": form})


class MyLoginView(SuccessMessageMixin, LoginView):

    def form_invalid(self, form):
        user_email = form.data['username']
        try:
            user = MyUser.objects.get(email=user_email)
            if not user.is_active:
                form._errors["__all__"] = form.error_class([u"Désolé, votre compte est inactif. Vous pourrez vous connecter lorsque l'administrateur aura vérifié votre identité et activé votre compte."])
        except MyUser.DoesNotExist:
            pass
        print(form.data)
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
