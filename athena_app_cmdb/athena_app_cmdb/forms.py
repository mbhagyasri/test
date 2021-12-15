"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from athena_app_cmdb import models


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254, label=_("USERNAME"),
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'USERNAME'}))
    password = forms.CharField(label=_("PASSWORD"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder': 'PASSWORD'}))


class RegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=254, required=True, label=_("*First Name"),
                                 widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': '*First Name'}))

    last_name = forms.CharField(max_length=254, required=True, label=_("*Last Name"),
                                widget=forms.TextInput({
                                     'class': 'form-control',
                                     'placeholder': '*Last Name'}))
    email = forms.CharField(max_length=254, label=_("*Email Address"),
                                widget=forms.TextInput({
                                     'class': 'form-control',
                                     'placeholder': '*Email Address'}))
    username = forms.CharField(max_length=254, label=_("*Username"),
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': '*Username'}))
    password = forms.CharField(label=_("*Password"),
                               widget=forms.PasswordInput({

                                   'class': 'form-control',
                                   'title': "Must contain at least one number and one uppercase and lowercase letter, "
                                            "a symbol, no spaces and at least 15 or more characters",
                                   'placeholder': '*Password'}))
    confirm_password = forms.CharField(label=_("*Confirm Password"),
                                       widget=forms.PasswordInput({'class': 'form-control',
                                                                   'placeholder': '*Confirm Password'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'username')