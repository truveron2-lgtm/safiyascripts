from django import forms
from articles.models import Comment

class AdminReplyForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your reply...'}),
        label=''
    )

    class Meta:
        model = Comment
        fields = ['content']
