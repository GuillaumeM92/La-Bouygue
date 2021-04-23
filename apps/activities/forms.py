from django import forms
from .models import ActivityComment
from client_side_image_cropping import ClientsideCroppingWidget

class ActivityCommentForm(forms.ModelForm):
    class Meta:
        model = ActivityComment
        fields = ['content', 'image']
        widgets = {
            'image': ClientsideCroppingWidget(
                width=1000,
                height=600,
                preview_width=120,
                preview_height=72,
            )
        }