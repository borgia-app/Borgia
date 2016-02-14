#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

from finances.models import Purchase, Transaction


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
    surname = models.CharField(max_length=255, blank=True, Null=True)
    family = models.CharField(max_length=255, blank=True, Null=True)
    balance = models.FloatField(default=0)
    year = models.IntegerField(choices=YEAR_CHOICES, blank=True)
    campus = models.CharField(choices=CAMPUS_CHOICES, max_length=2, blank=True, Null=True)
    phone = models.CharField(max_length=255, blank=True, Null=True)

    # TODO: task T55
    def __str__(self):
        return self.surname+' '+self.family+self.campus+str(self.year_pg())+' ('+self.first_name+' '+self.last_name+')'

    def year_pg(self):  # 2014 -> 214
        return int(str(self.year)[:1] + str(self.year)[-2:])

    def credit(self, x):
        old_balance = self.balance
        if x > 0:
            self.balance += x
        self.save()
        return round(self.balance - old_balance,4)

    def debit(self, x):
        old_balance = self.balance
        if x > 0:
            self.balance -= x
        self.save()
        return round(old_balance - self.balance, 4)

    def list_purchase(self):
        return Purchase.objects.filter(client=self)

    def list_transaction(self):
        return Transaction.objects.filter(client=self)
