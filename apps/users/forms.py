import os
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile
from captcha.fields import ReCaptchaField
from client_side_image_cropping import ClientsideCroppingWidget

User = get_user_model()


class UserLoginForm(AuthenticationForm):
    if os.getenv("ENV") == "prod":
        captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ["user", "password1", "password2", "captcha"]

    def clean(self):
        username = self.cleaned_data.get('username').lower()
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Adresse email")
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password1", "password2", "captcha"]

    def clean_email(self):
        data = self.cleaned_data['email']
        return data.lower()


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["email"]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image", "address", "phone"]
        widgets = {
            'image': ClientsideCroppingWidget(
                width=600,
                height=600,
                preview_width=90,
                preview_height=90,
            ),
            'address': forms.TextInput(
                attrs={
                    'placeholder': 'Renseignez votre adresse postale pour la partager avec les autres utilisateurs.'
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'placeholder': 'Renseignez votre N° de téléphone pour le partager avec les autres utilisateurs.'
                }
            )
        }
