from django import forms
from .models import Activity, ActivityComment
from client_side_image_cropping import ClientsideCroppingWidget

class ActivityCommentForm(forms.ModelForm):
    class Meta:
        model = ActivityComment
        fields = ['content',]

class ActyivityCreateForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['title', 'image', 'content', 'image2', 'content2', 'difficulty', 'duration', 'distance']
        widgets = {
            'image': ClientsideCroppingWidget(
                width=1024,
                height=768,
                preview_width=150,
                preview_height=112,
            )
        }