from django import forms
from .models import Reservation


class DateInput(forms.DateInput):
    """The browser's own date picker (the phone's wheel on a phone)."""
    input_type = "date"

    def __init__(self, attrs=None):
        super().__init__(attrs, format="%Y-%m-%d")


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["name", "start_date", "end_date", "description"]
        labels = {
            "name": "Qui vient",
            "start_date": "Arrivée",
            "end_date": "Départ",
            "description": "Précisions (facultatif)",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "par exemple : Famille Merle, Guillaume et les enfants",
                                           "maxlength": 200}),
            "start_date": DateInput(),
            "end_date": DateInput(),
            "description": forms.Textarea(attrs={"rows": 3,
                                                 "placeholder": "par exemple : 10 jours en famille, arrivée en fin de journée"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Blank dates are refused by the model; say it in words people use
        for name in ("start_date", "end_date"):
            self.fields[name].required = True
            self.fields[name].error_messages["required"] = "Choisissez une date."
            self.fields[name].error_messages["invalid"] = "Cette date n'est pas valide."

    def clean(self):
        cleaned_data = super().clean()
        start, end = cleaned_data.get("start_date"), cleaned_data.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "Le départ doit être le jour de l'arrivée ou après.")
        return cleaned_data
