from django import forms

from .models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'input',
                'placeholder': "Enter your username"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'input',
                'placeholder': "Enter your password"
            }
        )
    )
    
    # class Meta:
    #     model = User
    #     fields = ['email']
