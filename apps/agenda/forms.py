from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from .models import Reservation


class ReservationForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    name = forms.CharField(label='Nom', max_length=200, widget=forms.TextInput(
        attrs={'placeholder': 'par exemple : Famille Merle Guillaume'}))
    start_date = forms.DateTimeField(label='Date de début', widget=AdminDateWidget())
    end_date = forms.DateTimeField(label='Date de fin', widget=AdminDateWidget())
    description = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'par exemple : 10 jours à la Bouygue en famille'}))

    class Meta:
        model = Reservation
        fields = ['id', 'name', 'start_date', 'end_date', 'description']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        try:
            if end_date < start_date:
                cleaned_data.update(
                    {'error_message': "LA DATE DE FIN DOIT ÊTRE POSTÉRIEURE À LA DATE DE DÉBUT !"})
                raise forms.ValidationError("End date should be greater than start date.")
        except TypeError:
            cleaned_data.update(
                {'error_message': "LE FORMAT DE LA DATE EST INVALIDE ! MERCI DE RÉESSAYER."})

        return cleaned_data
