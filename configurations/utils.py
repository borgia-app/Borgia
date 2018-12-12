from django.conf import settings

from configurations.models import Configuration


def configurations_safe_get(name):
    """
    Get the setting object regarding the name.
    If it doesn't exists, create one with default value in settings.py.

    :warning: This function raises errors if the name doens't correspond to
    something knew in settings.py, this error should not be excepted and should
    stop Borgia. These settings are crucial and an error means that settings.py
    isn't well configured.
    """
    default = settings.CONFIGURATIONS_DEFAULT[name]
    setting, created = Configuration.objects.get_or_create(
        name=default[0],
        description=default[1],
        value_type=default[2]
    )
    if created:
        setting.value = default[3]
        setting.save()
    return setting
