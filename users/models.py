from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    surname = models.CharField(max_length=255, blank=True)
    family = models.CharField(max_length=255, blank=True)
    campus = models.CharField(max_length=4, blank=True)
    year = models.IntegerField(default=0)
    balance = models.FloatField(default=0)

    def __str__(self):
        return self.surname+' '+self.campus+str(self.year_pg())+' ('+self.first_name+' '+self.last_name+')'

    def year_pg(self):  # 2014 -> 214
        return int(str(self.year)[:1] + str(self.year)[-2:])