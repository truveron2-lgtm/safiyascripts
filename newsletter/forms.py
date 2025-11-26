from django import forms
from .models import Newsletter, NewsletterSection

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['title', 'volume', 'main_content']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter newsletter title...',
                'class': 'form-control'
            }),
            'volume': forms.NumberInput(attrs={
                'min': 1,
                'placeholder': 'Enter volume number...',
                'class': 'form-control'
            }),
            'main_content': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': 'Type text or paste HTML here...',
                'style': 'font-family: Arial, sans-serif;',
                'class': 'form-control'
            }),
        }

class NewsletterSectionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSection
        fields = ['heading', 'content', 'image', 'link', 'order']
        widgets = {
            'heading': forms.TextInput(attrs={
                'placeholder': 'Optional: Section heading',
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Type text or paste HTML here...',
                'class': 'form-control'
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={
                'placeholder': 'Optional link (https://example.com)',
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control'
            }),
        }
