from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


# ============================
#   CREATE USER FORM
# ============================
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)

    is_active = forms.BooleanField(required=False, initial=True)
    is_staff = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email',
            'password1', 'password2',
            'role',
            'is_active', 'is_staff', 'is_superuser'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data['email']
        user.is_active = self.cleaned_data['is_active']
        user.is_staff = self.cleaned_data['is_staff']
        user.is_superuser = self.cleaned_data['is_superuser']

        if commit:
            user.save()

        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = self.cleaned_data['role']
        profile.save()

        return user


# ============================
#   EDIT USER FORM
# ============================
class UserEditForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Leave blank to keep the current password."
    )

    is_active = forms.BooleanField(required=False)
    is_staff = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email',
            'first_name', 'last_name',
            'password',
            'is_active', 'is_staff', 'is_superuser'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user


# ============================
#   PROFILE UPDATE FORM
# ============================
class ProfileUpdateForm(forms.ModelForm):
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)

    class Meta:
        model = Profile
        fields = ['role', 'bio', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
