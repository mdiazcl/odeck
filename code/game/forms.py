from django.forms import ModelForm, Form
from django import forms

class FormLogin(Form):
    user = forms.CharField(max_length=32)
    password = forms.CharField(max_length=32, widget=forms.PasswordInput) 

class FormNewGame(Form):
    name = forms.CharField(max_length = 12)

class FormJoinGame(Form):
    gid = forms.IntegerField()
    password = forms.IntegerField()