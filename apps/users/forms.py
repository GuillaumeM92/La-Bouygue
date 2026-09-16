from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .antispam import HumanCheckMixin, LoginThrottleMixin
from .models import Profile
from client_side_image_cropping import ClientsideCroppingWidget

User = get_user_model()

INACTIVE_ACCOUNT = (
    "Désolé, votre compte est inactif pour le moment. Vous pourrez vous "
    "connecter lorsqu'un administrateur aura vérifié votre identité et "
    "activé votre compte.")


class EmailAuthenticationForm(AuthenticationForm):
    """Log in with an email address, whatever its case."""

    def clean(self):
        username = (self.cleaned_data.get('username') or '').lower()
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password)
            if self.user_cache is None:
                # Say the account awaits validation only to someone who knows
                # its password; anyone else gets the generic error.
                pending = User.objects.filter(email=username, is_active=False).first()
                if pending and pending.check_password(password):
                    raise forms.ValidationError(INACTIVE_ACCOUNT, code='inactive')
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserLoginForm(LoginThrottleMixin, EmailAuthenticationForm):
    pass


class AdminLoginForm(LoginThrottleMixin, AdminAuthenticationForm):
    pass


class UserRegisterForm(HumanCheckMixin, UserCreationForm):
    email = forms.EmailField(label="Adresse email")

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password1", "password2"]

    def clean_email(self):
        data = self.cleaned_data['email']
        return data.lower()


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
