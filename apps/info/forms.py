from django import forms
from .models import InfoComment

class InfoCommentForm(forms.ModelForm):
    class Meta:
        model = InfoComment
        fields = ['content',]
