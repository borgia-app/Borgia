from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import PasswordInput

from users.models import User, get_list_year


class UserCreationCustomForm(forms.Form):
    first_name = forms.CharField(label='Prenom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    email = forms.EmailField(label='Email')
    surname = forms.CharField(label='Buque', max_length=255, required=False)
    family = forms.CharField(label='Fam\'ss', max_length=255, required=False)
    campus = forms.ChoiceField(
        label='Tabagn\'s', choices=User.CAMPUS_CHOICES, required=False)
    year = forms.ChoiceField(
        label='Prom\'ss', choices=User.YEAR_CHOICES[::-1], required=True)
    username = forms.CharField(label='Username', max_length=255)
    is_external_member = forms.BooleanField(
        label='Externe à l\'association', required=False)
    password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).exists():
            raise ValidationError('Un autre user existe avec cet username')
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise ValidationError('Cet email est déjà utilisé')
        return data


class UserUpdateForm(forms.Form):
    first_name = forms.CharField(label='Prenom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    email = forms.EmailField(label='Email')
    surname = forms.CharField(label='Buque', max_length=255, required=False)
    family = forms.CharField(label='Fam\'ss', max_length=255, required=False)
    campus = forms.ChoiceField(
        label='Tabagn\'s', choices=User.CAMPUS_CHOICES, required=False)
    year = forms.ChoiceField(
        label='Prom\'ss', choices=User.YEAR_CHOICES, required=False)

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user')
        self.is_manager = kwargs.pop('is_manager')
        self.is_self_update = kwargs.pop('is_self_update')
        super().__init__(**kwargs)
        if self.is_manager:
            self.fields['username'] = forms.CharField(
                label='Username', max_length=255)
        if self.is_self_update:
            self.fields['avatar'] = forms.ImageField(
                label='Avatar', required=False)
            self.fields['theme'] = forms.ChoiceField(
                label='Theme', choices=User.THEME_CHOICES, required=False)

    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        if data == '':
            raise ValidationError('Ce champ ne peut pas être vide')
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name']
        if data == '':
            raise ValidationError('Ce champ ne peut pas être vide')
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        if data == '':
            raise ValidationError('Ce champ ne peut pas être vide')
        elif data != self.user.email:
            if User.objects.filter(email=data).exists():
                raise ValidationError(
                    'Un autre utilisateur existe avec cet email')
        return data

    def clean_username(self):
        data = self.cleaned_data['username']
        if data != self.user.username:
            if User.objects.filter(username=data).exists():
                raise ValidationError('Un autre user existe avec cet username')
        return data


class GroupUpdateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        possible_members = kwargs.pop('possible_members')
        possible_permissions = kwargs.pop('possible_permissions')
        super().__init__(*args, **kwargs)
        self.fields['members'] = forms.ModelMultipleChoiceField(
            queryset=possible_members,
            widget=forms.SelectMultiple(
                attrs={'class': 'selectpicker', 'data-live-search': 'True'}),
            required=False)
        self.fields['permissions'] = forms.ModelMultipleChoiceField(
            queryset=possible_permissions,
            widget=forms.SelectMultiple(
                attrs={'class': 'selectpicker', 'data-live-search': 'True'}),
            required=False)


class UserSearchForm(forms.Form):
    search = forms.CharField(
        label="Utilisateur(s)",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'autocomplete': 'off',
                                      'autofocus': 'true',
                                      'placeholder': "Nom / Prénom / Surnom"}))
    year = forms.ChoiceField(label='Année', required=False)
    state = forms.ChoiceField(label='Etat', choices=(('all', 'Tous les actifs'),
                                                     ('internals',
                                                      'Uniquement les membres internes actifs'),
                                                     ('negative_balance',
                                                      'Uniquement ceux à solde négative'),
                                                     ('threshold', 'Uniquement ceux en-dessous du seuil de commande'),
                                                     ('unactive', 'Uniquement ceux désactivés')),
                              required=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        YEAR_CHOICES = [('all', 'Toutes')]
        for year in get_list_year():
            YEAR_CHOICES.append(
                (year, year)
            )
        self.fields['year'].choices = YEAR_CHOICES


class UserQuickSearchForm(forms.Form):
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control autocomplete_username',
                                      'autocomplete': 'off',
                                      'autofocus': 'true',
                                      'placeholder': "Nom d'utilisateur"}))


class UserUploadXlsxForm(forms.Form):
    list_user = forms.FileField(label='Fichier Excel',
                                widget=forms.ClearableFileInput(attrs={'class': 'btn btn-default btn-file'}))

    user_fields = (
        ("first_name", "Prénom"),
        ("last_name", "Nom"),
        ("email", "Email"),
        ("surname", "Bucque"),
        ("family", "Fam's"),
        ("campus", "Tabagn's"),
        ("year", "Prom's (Année)"),
        ("balance", "Solde")
    )
    xlsx_columns = forms.MultipleChoiceField(label='Colonnes à traiter:',
                                             widget=forms.SelectMultiple(
                                                 attrs={'class': 'selectpicker', 'data-live-search': 'True',
                                                        'title': 'Sélectionner les colonnes à traiter',
                                                        'data-actions-box': 'True'}),
                                             choices=user_fields)


class UserDownloadXlsxForm(forms.Form):
    user_fields = (
        ("first_name", "Prénom"),
        ("last_name", "Nom"),
        ("email", "Email"),
        ("surname", "Bucque"),
        ("family", "Fam's"),
        ("campus", "Tabagn's"),
        ("year", "Prom's (Année)"),
        ("balance", "Solde")
    )
    xlsx_columns = forms.MultipleChoiceField(label='Colonnes à traiter:',
                                             widget=forms.SelectMultiple(
                                                 attrs={'class': 'selectpicker', 'data-live-search': 'True',
                                                        'title': 'Sélectionner les colonnes à traiter',
                                                        'data-actions-box': 'True'}),
                                             choices=user_fields)
