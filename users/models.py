from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime


class User(AbstractUser):
    surname = models.CharField(max_length=255, default='noname')
    family = models.CharField(max_length=255, default=0)
    CAMPUS_CHOICES = (
        ('ME', 'Me'),
        ('KA', 'Ka'),
        ('CH', 'Ch'),
        ('AI', 'Ai'),
        ('BO', 'Bo'),
        ('LI', 'Li'),
        ('CL', 'Cl')
    )
    campus = models.CharField(choices=CAMPUS_CHOICES, default='ME', max_length=2)
    YEAR_CHOICES = []
    for i in range(1900, datetime.now().year):
        YEAR_CHOICES.append((i, i))
    year = models.IntegerField(choices=YEAR_CHOICES, default='2014')
    balance = models.FloatField(default=0)

    def __str__(self):
        return self.surname+' '+self.campus+str(self.year_pg())+' ('+self.first_name+' '+self.last_name+')'

    def year_pg(self):  # 2014 -> 214
        return int(str(self.year)[:1] + str(self.year)[-2:])

    def credit(self, x):
        old_balance = self.balance
        if x > 0:
            self.balance += x
        return self.balance - old_balance

    def debit(self, x):
        old_balance = self.balance
        if x > 0:
            self.balance -= x
        return old_balance - self.balance
