from django.db import models
from django.utils.translation import ugettext_lazy as _


class TimeStampedDescription(models.Model):
    """TimeStampedDescription
    Une classe de base abstraite qui fournit une gestion automatique des dates de creation
    et de derniere modification, ainsi qu'un titre, une description
    """
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        get_latest_by = 'modified'
        ordering = ('-modified', '-created',)
        abstract = True
