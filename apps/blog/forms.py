from django import forms
from .models import Comment

class PostCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content',]
