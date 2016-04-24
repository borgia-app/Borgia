from django.core.exceptions import ValidationError, ObjectDoesNotExist
from users.models import User
import re


def autocomplete_username_validator(value):
    try:
        User.objects.get(username=value)
    except ObjectDoesNotExist:
        raise ValidationError('L\'utilisateur n\'existe pas')
