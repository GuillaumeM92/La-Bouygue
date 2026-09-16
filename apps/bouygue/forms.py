from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Announcement

DURATIONS = [
    ("7", "1 semaine"),
    ("30", "1 mois"),
    ("90", "3 mois"),
    ("180", "6 mois"),
    ("365", "1 an"),
]


class AnnouncementForm(forms.ModelForm):
    duration = forms.ChoiceField(label="Visible pendant", choices=DURATIONS, initial="90")

    class Meta:
        model = Announcement
        fields = ["title", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def save(self, author):
        announcement = super().save(commit=False)
        announcement.author = author
        announcement.expires_at = timezone.now() + timedelta(days=int(self.cleaned_data["duration"]))
        announcement.save()
        # Whoever writes it has read it
        announcement.read_by.add(author)
        return announcement
