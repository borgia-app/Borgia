from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    surname = models.CharField(max_length=255, blank=True)
    family = models.CharField(max_length=255, blank=True)
    campus = models.CharField(max_length=4, blank=True)
    year = models.IntegerField(default=0)
    balance = models.FloatField(default=0)
