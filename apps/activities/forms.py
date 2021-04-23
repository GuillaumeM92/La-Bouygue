from django import forms
from .models import Activity, ActivityComment
from client_side_image_cropping import ClientsideCroppingWidget

class ActivityCommentForm(forms.ModelForm):
    class Meta:
        model = ActivityComment
        fields = ['content', 'image']
        widgets = {
            'image': ClientsideCroppingWidget(
                width=400,
                height=600,
                preview_width=100,
                preview_height=150,
            )
        }

class ActivityCreateForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['title', 'image', 'content', 'image2', 'content2', 'difficulty', 'duration', 'distance']
        widgets = {
            'image': ClientsideCroppingWidget(
                width=400,
                height=600,
                preview_width=100,
                preview_height=150,
            )
        }