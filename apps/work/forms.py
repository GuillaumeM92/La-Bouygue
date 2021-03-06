from django import forms
from .models import WorkComment
from client_side_image_cropping import ClientsideCroppingWidget


class WorkCommentForm(forms.ModelForm):
    class Meta:
        model = WorkComment
        fields = ['content', 'image']
        widgets = {
            'image': ClientsideCroppingWidget(
                width=1000,
                height=600,
                preview_width=120,
                preview_height=72,
            )
        }
