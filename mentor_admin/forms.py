from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MentorAdmin

class MentorAdminSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            MentorAdmin.objects.create(user=user)
        return user
