from django import forms
from .models import Comment
from client_side_image_cropping import ClientsideCroppingWidget

class PostCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'image']
        widgets = {
            'image': ClientsideCroppingWidget(
                width=800,
                height=600,
                preview_width=80,
                preview_height=80,
            )
        }