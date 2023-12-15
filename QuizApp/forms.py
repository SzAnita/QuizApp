from django import forms
from django.core import validators
from .validators import *
from django.utils.translation import gettext as _


class Signup(forms.Form):
    name = forms.CharField(required=False, label='Name:')
    username = forms.CharField(required=False, label='Username', min_length=6, max_length=6)
    email = forms.EmailField(required=True, validators=[validators.EmailValidator(message='Invalid email')],
                             label='Email:')
    pwd = forms.CharField(widget=forms.PasswordInput, required=True, label='Password', min_length=6, max_length=20,
                          validators=[UpperCaseValidator, NumberValidator, SymbolValidator])
    pwd2 = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirm Password', min_length=6,
                           max_length=20)

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('pwd')
        pwd2 = cleaned_data.get('pwd2')
        if pwd != pwd2:
            self.add_error('pwd2', ValidationError(_("Please check again the password you have given. It doesn't "
                                                     "match the first one.")))


class Login(forms.Form):
    email = forms.EmailField(required=True, validators=[validators.EmailValidator], label='Email:')
    pwd = forms.CharField(widget=forms.PasswordInput, required=True, label='Password', min_length=6, max_length=20)
