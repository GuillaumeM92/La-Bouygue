from django import forms
from .models import InfoComment
from client_side_image_cropping import ClientsideCroppingWidget


class InfoCommentForm(forms.ModelForm):
    class Meta:
        model = InfoComment
        fields = ['content', 'image']
        widgets = {
            'image': ClientsideCroppingWidget(
                width=1000,
                height=600,
                preview_width=120,
                preview_height=72,
            )
        }
