from django import forms
from django.forms.widgets import PasswordInput
from borgia.validators import *

from users.models import User, list_year


class UserCreationCustomForm(forms.Form):
    first_name = forms.CharField(label='Prenom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    email = forms.EmailField(label='Email')
    surname = forms.CharField(label='Buque', max_length=255, required=False)
    family = forms.CharField(label='Fam\'ss', max_length=255, required=False)
    campus = forms.ChoiceField(label='Tabagn\'s', choices=User.CAMPUS_CHOICES, required=False)
    year = forms.ChoiceField(label='Prom\'ss', choices=User.YEAR_CHOICES[::-1], required=False)
    username = forms.CharField(label='Username', max_length=255)
    honnor_member = forms.BooleanField(label='Membre d\'honneur', required=False)
    password = forms.CharField(label='Mot de passe', widget=PasswordInput)
    password_bis = forms.CharField(label='Mot de passe (confirmation)', widget=PasswordInput)

    def clean(self):
        cleaned_data = super(UserCreationCustomForm, self).clean()
        try:

            if cleaned_data['password'] != cleaned_data['password_bis']:
                raise forms.ValidationError('Les deux mots de passe ne correspondent pas')

        except KeyError:
            pass
        return super(UserCreationCustomForm, self).clean()

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


class SelfUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'phone', 'avatar','theme']

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user')
        super(SelfUserUpdateForm, self).__init__(**kwargs)

    def clean_email(self):
        data = self.cleaned_data['email']
        if data == '':
            raise ValidationError('Ce champ ne peut pas être vide')
        if User.objects.filter(email=data).exclude(pk=self.user.pk).exists():
            raise ValidationError('Un autre utilisateur existe avec cet email')
        return data


class UserUpdateAdminForm(forms.Form):
    first_name = forms.CharField(label='Prenom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    email = forms.EmailField(label='Email')
    surname = forms.CharField(label='Buque', max_length=255, required=False)
    family = forms.CharField(label='Fam\'ss', max_length=255, required=False)
    campus = forms.ChoiceField(label='Tabagn\'s', choices=User.CAMPUS_CHOICES, required=False)
    year = forms.ChoiceField(label='Prom\'ss', choices=User.YEAR_CHOICES, required=False)

    def __init__(self, **kwargs):
        self.user_modified = kwargs.pop('user_modified')
        super(UserUpdateAdminForm, self).__init__(**kwargs)

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
        if User.objects.filter(email=data).exclude(pk=self.user_modified.pk).exists():
            raise ValidationError('Un autre utilisateur existe avec cet email')
        return data


class ManageGroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        possible_members = kwargs.pop('possible_members')
        possible_permissions = kwargs.pop('possible_permissions')
        super(ManageGroupForm, self).__init__(*args, **kwargs)
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


class LinkTokenUserForm(forms.Form):
    username = forms.CharField(
        label='User à lier',
        widget=forms.TextInput(attrs={'class': 'autocomplete_username'}))
    token_id = forms.CharField(label='Numéro unique du jeton')

    def clean(self):

        cleaned_data = super(LinkTokenUserForm, self).clean()

        # Validation de l'username
        username = cleaned_data['username']
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Cette personne n\'existe pas')

        return super(LinkTokenUserForm, self).clean()


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
                                                        ('negative_balance', 'Uniquement ceux à solde négative'),
                                                        ('threshold', 'Uniquement ceux en-dessous du seuil de commande'),
                                                        ('unactive', 'Uniquement ceux désactivés')),
                                            required=False)

    def __init__(self, **kwargs):
        super(UserSearchForm, self).__init__(**kwargs)

        YEAR_CHOICES = [('all', 'Toutes')]
        for year in list_year():
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
    list_user = forms.FileField(label='Fichier Excel')
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
