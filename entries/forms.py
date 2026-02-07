from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Entry

class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Used for 'Reply-To' notifications.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['title', 'content', 'mood', 'spotify_track_id']
        widgets = {
            'mood': forms.HiddenInput(),
            'spotify_track_id': forms.HiddenInput(),
        }
