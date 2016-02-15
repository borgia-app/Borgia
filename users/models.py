#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

from finances.models import Sale


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
    balance = models.FloatField(default=0)
    year = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
    campus = models.CharField(choices=CAMPUS_CHOICES, max_length=2, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)

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
        return Sale.objects.filter(sender=self)