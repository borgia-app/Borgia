#-*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from datetime import datetime

from finances.models import Sale, BankAccount


class User(AbstractUser):

    # Listes de validations
    CAMPUS_CHOICES = (
        ('ME', 'Me'),
        ('KA', 'Ka'),
        ('CH', 'Ch'),
        ('AI', 'Ai'),
        ('BO', 'Bo'),
        ('LI', 'Li'),
        ('CL', 'Cl'),
        ('KIN', 'Kin')
    )
    YEAR_CHOICES = []
    for i in range(1900, datetime.now().year):
        YEAR_CHOICES.append((i, i))

    # Attributs
    # ID, last_name, first_name, email sont dans AbstractUser
    surname = models.CharField(max_length=255, blank=True, null=True)
    family = models.CharField(max_length=255, blank=True, null=True)
    balance = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    year = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
    campus = models.CharField(choices=CAMPUS_CHOICES, max_length=2, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    token_id = models.CharField(max_length=6, blank=True, null=True)

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
        return Sale.objects.filter(Q(sender=self) | Q(recipient=self))

    def list_bank_account(self):
        return BankAccount.objects.filter(owner=self)

    class Meta:
        permissions = (
            ('presidents_group_manage', 'Gérer le groupe des présidents'),
            ('tresoriers_group_manage', 'Gérer le groupe des trésoriers'),
            ('chefs_gestionnaires_du_foyer_group_manage', 'Gérer le groupe des chefs gestionnaires du foyer'),
            ('gestionnaires_du_foyer_group_manage', 'Gérer le groupe des gestionnaires du foyer'),
            ('chefs_gestionnaires_de_l_auberge_group_manage', 'Gérer le groupe des chefs gestionnaires de l\'auberge'),
            ('gestionnaires_de_l_auberge_group_manage', 'Gérer le groupe des gestionnaires de l\'auberge'),
            ('gadz_arts_group_manage', 'Gérer le groupe des Gadz\'Arts'),
            ('membres_d_honneurs_group_manage', 'Gérer le groupe des membres d\'honneurs'),
            ('membres_speciaux_group_manage', 'Gérer le groupe des membres spéciaux'),
            ('vices_presidents_delegues_a_la_vie_interne_group_manage',
             'Gérer le groupe des vices présidents délégués à la vie interne'),
            ('reach_workboard_treasury', 'Accéder au workboard de la trésorie'),
            ('reach_workboard_presidents', 'Accéder au workboard des présidents'),
            ('reach_workboard_vices_presidents_vie_interne', 'Accéder au workboard des vices présidents délégués à la vie interne'),

            ('list_user', 'Lister les users'),
            ('retrieve_user', 'Afficher les users'),

            ('supply_account', 'Ajouter de l\'argent à un compte'),

            ('link_token_user', 'Lier un jeton à un user'),

            ('add_product', 'Ajouter des produits'),
        )


def list_year():
    list_year = []
    for u in User.objects.all().exclude(groups=9):
        if u.year not in list_year:
            if u.year is not None:
                list_year.append(u.year)
    return sorted(list_year, reverse=True)
