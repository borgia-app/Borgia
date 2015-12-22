from django.db import models
from django.utils.translation import ugettext_lazy as _


class TimeStampedDescription(models.Model):
    """TimeStampedDescription
    Une classe de base abstraite qui fournit une gestion automatique des dates de creation
    et de derniere modification, ainsi qu'un titre, une description
    """
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    slug = models.SlugField(unique=True)
    # Le slug est un nom unique que l'on peut passer dans l'url pour appeler l'objet

    class Meta:
        get_latest_by = 'modified'
        ordering = ('-modified', '-created',)
        abstract = True
