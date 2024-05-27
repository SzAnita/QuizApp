from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core import validators
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import models

from .models import User, Quiz
from .validators import *
from django.utils.translation import gettext as _


class Signup(forms.ModelForm):
    name = forms.CharField(required=False, label='Name:')
    username = forms.CharField(required=False, label='Username', min_length=4, max_length=12)
    email = forms.EmailField(required=True, validators=[validators.EmailValidator(message='Invalid email')],
                             label='Email:')
    pwd = forms.CharField(widget=forms.PasswordInput, required=True, label='Password', min_length=6, max_length=20,
                          validators=[UpperCaseValidator, NumberValidator, SymbolValidator])
    pwd2 = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirm Password', min_length=6,
                           max_length=20)
    class Meta:

        model=User
        fields = ['name', 'username', 'email']

    def clean(self):
        self.cleaned_data = super().clean()
        pwd = self.cleaned_data.get('pwd')
        pwd2 = self.cleaned_data.get('pwd2')
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if pwd != pwd2:
            self.add_error('pwd2', ValidationError(_("Please check again the password you have given. It doesn't "
                                                     "match the first one.")))
        if User.objects.filter(email=email).exists():
            self.add_error('email', ValidationError(_('There is already an account with this email')))
        if User.objects.filter(username=username).exists():
            self.add_error('username', ValidationError(_("This username already exists")))
        try:
            validate_password(pwd)
        except ValidationError as e:
            self.add_error('pwd', e)

        return self.cleaned_data

    def save(self):
        email = self.cleaned_data.get('email')
        pwd = self.cleaned_data.get('pwd')
        name = None
        username = email

        if len(self.cleaned_data['name']) > 0:
            name = self.cleaned_data['name']
        if len(self.cleaned_data['username']) > 0:
            username = self.cleaned_data['username']
        user = User(email=email, password=pwd, name=name, username=username)
        user.set_password(pwd)
        user.save()
        authenticate(username=username, password=pwd)
        return user



class Login(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        pwd = self.cleaned_data.get('password')
        if username is not None and pwd:
            if not User.objects.filter(username=username).exists():
                self.add_error('username',
                               ValidationError(
                                   _("This username doesn't have an account. Make sure that you provide an existing "
                                     "username.")))
            else:
                self.user_cache = authenticate(
                    self.request, username=username, password=pwd
                )
                if self.user_cache is None:
                    self.add_error('password',
                                       ValidationError(_('Please make sure you enter the correct password. Note that '
                                                         'it may be case-sensitive.')))
        else:
            print('test non-field-error')
            self.add_error(NON_FIELD_ERRORS,
                           ValidationError(_("Please enter a valid %(username)s and password. Note that both fields "
                                             "may be case-sensitive.")))
        return self.cleaned_data


class CreateQuiz(forms.ModelForm):

    choices = ((0, False), (1, True))
    owner_id = forms.CharField(widget=forms.HiddenInput, label='')
    public = forms.ChoiceField(widget=forms.Select, choices=choices)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 30}), required=False)
    class Meta:
        model = Quiz
        fields = ['owner_id', 'title', 'theme', 'description', 'public']

    def clean(self):
        self.cleaned_data = super().clean()
        owner_id = self.cleaned_data.get('owner_id')
        title = self.cleaned_data.get('title')
        if Quiz.objects.filter(owner_id__username=owner_id, title=title).exists():
            self.add_error('title', ValidationError(_('You already have a quiz with this title')))
        if len(owner_id) > 0 and User.objects.filter(username=owner_id):
            self.cleaned_data['owner_id'] = User.objects.get(username=owner_id)
        return self.cleaned_data

