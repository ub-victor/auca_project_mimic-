from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class SignupForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    student_id = forms.CharField(max_length=30, required=False)

    class Meta:
        model  = CustomUser
        fields = ['first_name', 'email', 'student_id', 'password1', 'password2']

    def save(self, commit=True):
        user          = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email    = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'phone', 'profile_picture']
