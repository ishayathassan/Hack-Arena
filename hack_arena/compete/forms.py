from django import forms

class ContestLoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Contest Password")