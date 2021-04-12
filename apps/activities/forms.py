from django import forms
from .models import ActivityComment

class ActivityCommentForm(forms.ModelForm):
    class Meta:
        model = ActivityComment
        fields = ['content',]
