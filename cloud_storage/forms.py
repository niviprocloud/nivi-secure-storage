from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import EncryptedFile

class FileUploadForm(forms.Form):
    """Form for uploading files to be encrypted and stored"""
    file = forms.FileField(
        label='Select a file',
        help_text='Max file size: 100 MB',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (limit to 100 MB)
            if file.size > 100 * 1024 * 1024:  # 100 MB in bytes
                raise forms.ValidationError("File size must be under 100 MB.")
        return file

class UserRegistrationForm(UserCreationForm):
    """Form for user registration (not used directly since we're using Google OAuth)"""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Only Gmail accounts are allowed.")
        return email