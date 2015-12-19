from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    surname = models.CharField(max_length=255)
    family = models.CharField(max_length=255)
    campus = models.CharField(max_length=4)
    year = models.IntegerField()
