from django import forms
from .models import WorkComment
from apps.client_side_image_cropping.widgets import ClientsideCroppingWidget

class WorkCommentForm(forms.ModelForm):
    class Meta:
        model = WorkComment
        fields = ['content', 'image']
        widgets = {
            'image': ClientsideCroppingWidget(
                width=600,
                height=600,
                preview_width=50,
                preview_height=50,
            )
        }
