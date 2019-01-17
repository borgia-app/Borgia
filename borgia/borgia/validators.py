from django.core.exceptions import ObjectDoesNotExist, ValidationError

from users.models import User


def autocomplete_username_validator(value):
    try:
        User.objects.get(username=value)
    except ObjectDoesNotExist:
        raise ValidationError('L\'utilisateur n\'existe pas')
