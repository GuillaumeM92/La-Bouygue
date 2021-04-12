from django import forms
from .models import WorkComment

class WorkCommentForm(forms.ModelForm):
    class Meta:
        model = WorkComment
        fields = ['content',]
