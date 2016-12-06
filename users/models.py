#-*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import re
from django.core.validators import RegexValidator

from finances.models import Sale, BankAccount, SharedEvent


class User(AbstractUser):

    # Listes de validations
    CAMPUS_CHOICES = (
        ('ME', 'Me'),
        ('AN', 'An'),
        ('CH', 'Ch'),
        ('AI', 'Ai'),
        ('BO', 'Bo'),
        ('LI', 'Li'),
        ('CL', 'Cl'),
        ('KA', 'Ka'),
        ('KIN', 'Kin')
    )
    YEAR_CHOICES = []
    for i in range(1953, datetime.now().year + 1):
        YEAR_CHOICES.append((i, i))

    # Attributs
    # ID, last_name, first_name, email sont dans AbstractUser
    surname = models.CharField('Bucque', max_length=255, blank=True, null=True)
    family = models.CharField('Fam\'ss', max_length=255, blank=True, null=True)
    balance = models.DecimalField('Solde', default=0, max_digits=9, decimal_places=2)
    year = models.IntegerField('Prom\'ss', choices=YEAR_CHOICES, blank=True, null=True)
    campus = models.CharField('Tabagn\'ss', choices=CAMPUS_CHOICES, max_length=2, blank=True, null=True)
    phone = models.CharField('Numéro de téléphone', max_length=255, blank=True, null=True,
                             validators=[RegexValidator('^0[0-9]{9}$',
                                                                     'Le numéro de téléphone doit être du type 0123456789')])
    token_id = models.CharField('Numéro de jeton lié', max_length=6, blank=True, null=True,
                                validators=[RegexValidator('^[0-9A-Z]{6}$',
                                                           'Mauvaise forme de numéro de jeton, il ne doit contenir que six chiffres et/ou lettres majuscules')])
    avatar = models.ImageField('Avatar', upload_to='img/avatars/', default=None, blank=True, null=True)

    def __str__(self):
        return self.first_name+' '+self.last_name

    def year_pg(self):  # 2014 -> 214
        if self.year is not None:
            return int(str(self.year)[:1] + str(self.year)[-2:])

    def credit(self, x):
        if x > 0:
            self.balance += x
        self.save()

    def debit(self, x):
        if x > 0:
            self.balance -= x
        self.save()

    def list_sale(self):

        # sender -> vente solo (Foyer, ...), rechargement solo (Lydia), transfert, se en manager,
        #           vente normales (C-Vis, ...), mouvement exceptionnel
        # recipient -> transfert, mouvement exceptionnel

        # Liste des ventes sender, recipient ou participant
        list_sale = Sale.objects.filter(Q(sender=self) | Q(recipient=self))\
                    | Sale.objects.filter(sharedevent__participants=self)

        # Exclusion des sender car manager (et pas participant) du se
        for s in list_sale:
            # S'il n'y a pas d'évent lié, pas la peine de traiter
            try:
                se = SharedEvent.objects.get(sale=s)
                # Si l'user n'est pas participant de l'event, alors il a agit en tant que manager
                if self not in se.participants.all():
                    list_sale = list_sale.exclude(pk=s.pk)
            except ObjectDoesNotExist:
                pass

        return list_sale.order_by('-date').distinct()

    def list_bank_account(self):
        return BankAccount.objects.filter(owner=self)

    class Meta:
        permissions = (
            # Presidents
            ('presidents_group_manage', 'Gérer le groupe des présidents'),
            ('reach_workboard_presidents', 'Accéder au workboard des présidents'),
            ('reach_workboard_vices_presidents_vie_interne', 'Accéder au workboard des vices présidents délégués à la vie interne'),


            # Tresorie
            ('tresoriers_group_manage', 'Gérer le groupe des trésoriers'),
            ('reach_workboard_treasury', 'Accéder au workboard de la trésorie'),

            # Foyer
            ('chefs_gestionnaires_du_foyer_group_manage', 'Gérer le groupe des chefs gestionnaires du foyer'),
            ('gestionnaires_du_foyer_group_manage', 'Gérer le groupe des gestionnaires du foyer'),
            ('reach_workboard_foyer', 'Aller sur le workboard du foyer'),

            # Auberge
            ('chefs_gestionnaires_de_l_auberge_group_manage', 'Gérer le groupe des chefs gestionnaires de l\'auberge'),
            ('gestionnaires_de_l_auberge_group_manage', 'Gérer le groupe des gestionnaires de l\'auberge'),
            ('reach_workboard_auberge', 'Aller sur le workboard de l\'auberge'),

            #CVis
            ('chefs_gestionnaires_de_la_cvis_group_manage', 'Gérer le groupe des chefs gestionnaires de la cvis'),
            ('gestionnaires_de_la_cvis_group_manage', 'Gérer le groupe des gestionnaires de la cvis'),
            ('reach_workboard_cvis', 'Aller sur le workboard de la cvis'),

            #Bkars
            ('chefs_gestionnaires_de_la_bkars_group_manage', 'Gérer le groupe des chefs gestionnaires de la bkars'),
            ('gestionnaires_de_la_bkars_group_manage', 'Gérer le groupe des gestionnaires de la bkars'),
            ('reach_workboard_bkars', 'Aller sur le workboard de la bkars'),


            #Autre
            ('gadz_arts_group_manage', 'Gérer le groupe des Gadz\'Arts'),
            ('membres_d_honneurs_group_manage', 'Gérer le groupe des membres d\'honneurs'),
            ('membres_speciaux_group_manage', 'Gérer le groupe des membres spéciaux'),
            ('vices_presidents_delegues_a_la_vie_interne_group_manage',
             'Gérer le groupe des vices présidents délégués à la vie interne'),


            ('list_user', 'Lister les users'),
            ('retrieve_user', 'Afficher les users'),

            ('supply_account', 'Ajouter de l\'argent à un compte'),
            ('exceptionnal_movement', 'Créer un mouvement exceptionnel'),

            ('link_token_user', 'Lier un jeton à un user'),

        )


def list_year():
    list_year = []
    for u in User.objects.all().exclude(groups=9):
        if u.year not in list_year:
            if u.year is not None:
                list_year.append(u.year)
    return sorted(list_year, reverse=True)


def user_from_token_tap(initial_token_tap):
    """
    Renvoi l'user correspondant à un code de jeton lu avec le système d'électrovanne
    Remarque : A utiliser à travers un try pour gérer ObjectDoesNotExist
    Exemples :
    25166484851706966556857503 -> 3FEB7D
    25166484852565553687068573 -> 4875DF
    """
    token_end = ''
    for dual in re.findall(r"[0-9]{2}", initial_token_tap[1:len(initial_token_tap) - 5]):
        token_end += chr(int(dual))
    token_end = token_end[4:]
    return User.objects.get(token_id=token_end)
