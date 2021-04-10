from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileUpdateForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, str("Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter."))
            return redirect("users-login")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


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

    context = {"p_form": p_form}

    return render(request, "users/profile.html", context)
