"""
Define Configurations utils.
Including the default configurations, with the syntax:
name: (String name, String description, String value_type, String value)
"""

from configurations.models import Configuration


def configurations_get(name):
    return Configuration.objects.get(name=name)
