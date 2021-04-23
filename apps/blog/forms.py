from django import forms
from .models import Comment
from apps.client_side_image_cropping.widgets import ClientsideCroppingWidget

class PostCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'image']
        widgets = {
            'image': ClientsideCroppingWidget(
                width=1000,
                height=600,
                preview_width=120,
                preview_height=72,
            )
        }