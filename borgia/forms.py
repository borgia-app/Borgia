from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate

from users.models import User


class UserSearchForm(forms.Form):
    search = forms.CharField(
        label='Recherche',
        max_length=255
    )


class LoginForm(forms.Form):
    username = forms.CharField(
		label="Nom d'utilisateur",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control autocomplete_username',
                                      'autocomplete': 'off',
									  'autofocus': 'true',
									  'placeholder': "Nom d'utilisateur"})
    )
    password = forms.CharField(
        label='Mot de passe',
        max_length=255,
        widget=forms.PasswordInput(attrs={'class': 'form-control',
										  'placeholder': "Mot de passe"})
    )

    def __init__(self, **kwargs):
        self.module = kwargs.pop('module')
        super(LoginForm, self).__init__(**kwargs)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()

        # User credential check
        try:
            u = User.objects.get(username=cleaned_data['username'])
        except ObjectDoesNotExist:
            raise forms.ValidationError("L'utilisateur n'existe pas")
        if not u.is_active:
            raise forms.ValidationError("L'utilisateur a été desactivé")

        user = authenticate(
            username=cleaned_data['username'],
            password=cleaned_data['password']
        )
        if user is None:
            raise forms.ValidationError('Mot de passe incorrect')

        # If module, check if active
        if self.module:
            if not self.module.state:
                raise forms.ValidationError("""Ce module de vente n'est pas
                                            actuellement actif.""")
