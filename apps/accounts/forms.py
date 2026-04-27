from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class LoginForm(forms.Form):
    email    = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your Email', 'class': 'carre'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Type your Password', 'class': 'carre'}))


class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'First name'}))
    last_name  = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Last name'}))
    email      = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input', 'placeholder': 'your.email@auca.ac.rw'}))
    student_id = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Student Registration No (optional)'}))

    class Meta:
        model  = CustomUser
        fields = ['first_name', 'last_name', 'email', 'student_id', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        user            = super().save(commit=False)
        user.username   = self.cleaned_data['email']
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.student_id = self.cleaned_data.get('student_id', '')
        user.role       = 'student'
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-input'}),
            'email':      forms.EmailInput(attrs={'class': 'form-input'}),
            'bio':        forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'phone':      forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
