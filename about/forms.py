from django import forms
from .models import AboutPage

class AboutPageForm(forms.ModelForm):
    class Meta:
        model = AboutPage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
        }
