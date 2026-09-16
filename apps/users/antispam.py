"""Protection of the public forms, without a third-party CAPTCHA.

New accounts already stay inactive until an administrator validates them.
What the reCAPTCHA really prevented was robots filling the database and
making the site send e-mails (a welcome message to any address, an alert to
the administrators). Three cheap checks do that without Google:

- a honeypot field, kept off-screen, that people never see and robots fill;
- a signed timestamp: a form sent back within seconds of being displayed,
  tampered with, or more than a day old is refused;
- a ceiling on registrations per hour, for whatever still gets through.

Login gets no CAPTCHA: repeated failures on one address lock it for a
quarter of an hour, on the site and on the admin.

Counters live in Django's default cache, one per Gunicorn worker, which is
enough to make password guessing hopeless.
"""
import hashlib
import time

from django import forms
from django.core import signing
from django.core.cache import cache

TOKEN_SALT = 'users.antispam.form-token'
MIN_FILL_SECONDS = 3
MAX_FORM_AGE = 24 * 60 * 60

REGISTRATIONS_PER_HOUR = 10
REGISTRATIONS_KEY = 'users.antispam.registrations'

LOGIN_ATTEMPTS = 5
LOGIN_LOCK_SECONDS = 15 * 60

HONEYPOT_FIELD = 'site_web'
TOKEN_FIELD = 'jeton'

REFUSED = "Le formulaire n'a pas pu être validé. Merci de réessayer."
TOO_FAST = "Formulaire envoyé trop vite : patientez quelques secondes, puis renvoyez-le."
EXPIRED = "La page était ouverte depuis trop longtemps : merci de renvoyer le formulaire."
LOCKED = ("Trop de tentatives de connexion pour cette adresse. "
          "Réessayez dans un quart d'heure.")


class HumanCheckMixin:
    """Honeypot and fill-time check, for a form anyone can submit."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[HONEYPOT_FIELD] = forms.CharField(
            label="Ne pas remplir ce champ", required=False,
            widget=forms.TextInput(attrs={'autocomplete': 'off', 'tabindex': '-1'}))
        self.fields[TOKEN_FIELD] = forms.CharField(required=False, widget=forms.HiddenInput)

        # The form always carries a fresh token, so a page shown again after an
        # error can be sent back; the one that came in is kept for clean().
        fresh_token = signing.dumps(time.time(), salt=TOKEN_SALT)
        self.submitted_token = ''
        if self.is_bound:
            self.submitted_token = self.data.get(TOKEN_FIELD, '')
            self.data = self.data.copy()
            self.data[TOKEN_FIELD] = fresh_token
        else:
            self.initial[TOKEN_FIELD] = fresh_token

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get(HONEYPOT_FIELD):
            raise forms.ValidationError(REFUSED, code='honeypot')
        try:
            issued = signing.loads(self.submitted_token, salt=TOKEN_SALT, max_age=MAX_FORM_AGE)
        except signing.SignatureExpired:
            raise forms.ValidationError(EXPIRED, code='expired')
        except signing.BadSignature:
            raise forms.ValidationError(REFUSED, code='bad_token')
        if time.time() - float(issued) < MIN_FILL_SECONDS:
            raise forms.ValidationError(TOO_FAST, code='too_fast')
        return cleaned_data


def registration_allowed():
    return cache.get(REGISTRATIONS_KEY, 0) < REGISTRATIONS_PER_HOUR


def count_registration():
    if cache.add(REGISTRATIONS_KEY, 1, 60 * 60):
        return
    try:
        cache.incr(REGISTRATIONS_KEY)
    except ValueError:  # expired in between
        cache.set(REGISTRATIONS_KEY, 1, 60 * 60)


def _login_key(email):
    return 'users.antispam.login.' + hashlib.sha256(email.encode()).hexdigest()


class LoginThrottleMixin:
    """Lock an address for a while after repeated failed logins."""

    def clean(self):
        email = (self.data.get('username') or '').strip().lower()
        key = _login_key(email)
        if email and cache.get(key, 0) >= LOGIN_ATTEMPTS:
            raise forms.ValidationError(LOCKED, code='locked')
        try:
            cleaned_data = super().clean()
        except forms.ValidationError:
            if email:
                cache.set(key, cache.get(key, 0) + 1, LOGIN_LOCK_SECONDS)
            raise
        cache.delete(key)
        return cleaned_data
