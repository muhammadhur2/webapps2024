from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'currency',)

class CustomUserUpdateForm(UserChangeForm):
    password = None  # Hides the password field
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')
