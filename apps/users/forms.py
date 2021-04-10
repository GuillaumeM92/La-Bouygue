from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Adresse email")

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["email"]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image"]
