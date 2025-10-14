from django import forms
from .models import Article, Comment, Subscriber


class ArticleForm(forms.ModelForm):
    """Form for logged-in users to create or edit articles."""
    class Meta:
        model = Article
        fields = ['title', 'short_description', 'full_description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter article title',
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a short summary for your article...',
            }),
            'full_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Write the full content here...',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }


class CommentForm(forms.ModelForm):
    """Form for both visitors and users to comment or reply."""
    parent = forms.ModelChoiceField(
        queryset=Comment.objects.filter(parent__isnull=True),
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Comment
        fields = ['name', 'email', 'content', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email address',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...',
            }),
        }


from django import forms
from .models import Subscriber

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email to subscribe...'
            }),
        }

