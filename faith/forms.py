from django import forms
from .models import FaithText

class FaithTextForm(forms.ModelForm):
    class Meta:
        model = FaithText
        fields = ['title', 'content', 'active']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 8, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }
