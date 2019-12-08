import datetime

from django import forms
from django.core.exceptions import ObjectDoesNotExist

from borgia.validators import autocomplete_username_validator
from users.models import User, get_list_year


class EventListForm(forms.Form):
    date_begin = forms.DateField(label="Depuis", required=False, initial=datetime.date.today().replace(day=1),
                                 widget=forms.DateInput(
                                     attrs={'class': 'datepicker'})
                                 )
    date_end = forms.DateField(label="Jusqu'à", required=False, widget=forms.DateInput(
        attrs={'class': 'datepicker'}))
    done = forms.ChoiceField(label="Etat", choices=(("not_done", 'En cours'), ("done", 'Terminé'), ("both", 'Les deux')),
                             initial=("not_done", 'En cours')
                             )
    order_by = forms.ChoiceField(label="Trier par", choices=(
        ('-date', 'Date'), ('manager', 'Opérateur')))


class EventCreateForm(forms.Form):
    description = forms.CharField(label='Description')
    date = forms.DateField(label='Date de l\'événement',
                           widget=forms.DateInput(attrs={'class': 'datepicker'}))
    price = forms.DecimalField(label='Prix total (vide si pas encore connu)', decimal_places=2, max_digits=9,
                               required=False, min_value=0)
    bills = forms.CharField(
        label='Factures liées (vide si pas encore connu)', required=False)
    allow_self_registeration = forms.BooleanField(
        label='Autoriser la préinscription', initial=True, required=False)
    date_end_registration = forms.DateField(label='Date de fin de la préinscription',
                                            required=False,
                                            widget=forms.DateInput(
                                                attrs={'class': 'datepicker'})
                                            )


class EventDeleteForm(forms.Form):
    checkbox = forms.BooleanField(
        label="Je suis conscient que la suppression entraîne le non-paiement, et la perte des informations.")


class EventFinishForm(forms.Form):
    type_payment = forms.ChoiceField(label='Type de débucquage', choices=(('pay_by_total', 'Payer par division du total'),
                                                                          ('pay_by_ponderation',
                                                                           'Payer par prix par pondération'),
                                                                          ('no_payment', 'Ne pas faire payer')))
    total_price = forms.DecimalField(label='Prix total', decimal_places=2, max_digits=9,
                                     required=False, min_value=0.01)
    ponderation_price = forms.DecimalField(label='Prix par pondération', decimal_places=2, max_digits=9,
                                           required=False, min_value=0.01)
    remark = forms.CharField(
        label='Pourquoi finir l\'événement ?', required=False)

    def clean_total_price(self):
        data = self.cleaned_data['total_price']

        if self.cleaned_data['type_payment'] == 'pay_by_total':
            if data is None:
                raise forms.ValidationError('Obligatoire !')

        return data

    def clean_ponderation_price(self):
        data = self.cleaned_data['ponderation_price']

        if self.cleaned_data['type_payment'] == 'pay_by_ponderation':
            if data is None:
                raise forms.ValidationError('Obligatoire !')

        return data

    def clean_remark(self):
        data = self.cleaned_data['remark']

        if self.cleaned_data['type_payment'] == 'no_payment':
            if not data:
                raise forms.ValidationError('Obligatoire !')

        return data


class EventUpdateForm(forms.Form):
    price = forms.DecimalField(
        label='Prix total (€)', decimal_places=2, max_digits=9, min_value=0, required=False)
    bills = forms.CharField(label='Factures liées', required=False)
    manager = forms.CharField(label='Gestionnaire', required=False,
                              widget=forms.TextInput(
                                  attrs={'class': 'autocomplete_username'}),
                              validators=[autocomplete_username_validator])
    allow_self_registeration = forms.BooleanField(
        label='Autoriser la préinscription', required=False)


class EventListUsersForm(forms.Form):
    order_by = forms.ChoiceField(label='Trier par', choices=(
        ('username', 'Username'), ('last_name', 'Nom'), ('surname', 'Bucque'), ('year', 'Année')))
    state = forms.ChoiceField(label='Lister', choices=(
        ('users', 'Tous les concernés'),
        ('registrants', 'Uniquement les préinscrits'),
        ('participants', 'Uniquement les participants')))


class EventSelfRegistrationForm(forms.Form):
    weight = forms.IntegerField(label='Pondération', min_value=0)


class EventAddWeightForm(forms.Form):
    user = forms.CharField(
        label="Ajouter",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control autocomplete_username',
                                      'autocomplete': 'off',
                                      'autofocus': 'true',
                                      'placeholder': "Nom d'utilisateur"}))

    state = forms.ChoiceField(label='En tant que', choices=(
        ('registered', 'Préinscrit'), ('participant', 'Participant')))
    weight = forms.IntegerField(
        label='Pondération', min_value=0, required=True, initial=1)

    def clean_user(self):
        username = self.cleaned_data['user']

        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError("L'utilisateur n'existe pas !")

        if not user.is_active:
            raise forms.ValidationError("L'utilisateur a été desactivé !")

        return user


class EventDownloadXlsxForm(forms.Form):
    state = forms.ChoiceField(label='Sélection',
                              choices=(
                                  ('year', 'Listes de promotions'),
                                  ('registrants', 'Préinscrits'),
                                  ('participants', 'Participants')))
    years = forms.MultipleChoiceField(
        label='Année(s) à inclure', required=False)

    def __init__(self):
        super().__init__()
        YEAR_CHOICES = []
        for year in get_list_year():
            YEAR_CHOICES.append(
                (year, year)
            )
        self.fields['years'].choices = YEAR_CHOICES


class EventUploadXlsxForm(forms.Form):
    list_user = forms.FileField(label='Fichier de données')
    state = forms.ChoiceField(
        label='Liste de ',
        choices=(('registrants', 'Préinscrits'), ('participants', 'Participants')))
