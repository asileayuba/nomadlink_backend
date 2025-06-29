from django import forms
from django.contrib.auth.forms import AuthenticationForm

class WalletOrEmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Wallet/Email Address",
        widget=forms.TextInput(attrs={"autofocus": True})
    )
