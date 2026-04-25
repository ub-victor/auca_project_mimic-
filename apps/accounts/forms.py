from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class SignupForm(UserCreationForm):
    student_id = forms.CharField(max_length=30, required=True, label="Student ID")
    first_name = forms.CharField(max_length=150, required=True, label="First Name")
    email      = forms.EmailField(required=True, label="Email")

    class Meta:
        model  = CustomUser
        fields = ['student_id', 'first_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username   = self.cleaned_data['email']
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.student_id = self.cleaned_data['student_id']
        user.role       = 'student'
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already in use.")
        return email
