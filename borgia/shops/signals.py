from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from shops.models import Shop
from shops.utils import (DEFAULT_PERMISSIONS_ASSOCIATES,
                         DEFAULT_PERMISSIONS_CHIEFS)


@receiver(post_save, sender=Shop)
def create_shop_groups(instance, created, **kwargs):
    """
    Create shop groups (chiefs and associates) on shop creation.
    Also add permissions to manage these groups
    """
    if created:
        content_type = ContentType.objects.get(app_label='users', model='user')
        manage_chiefs = Permission.objects.create(
            name='Can manage chiefs of ' + instance.name + ' shop',
            codename='manage_chiefs-' + instance.name + '_group',
            content_type=content_type
        )
        manage_associates = Permission.objects.create(
            name='Can manage associates of ' + instance.name + ' shop',
            codename='manage_associates-' + instance.name + '_group',
            content_type=content_type
        )

        chiefs = Group.objects.create(
            name='chiefs-' + instance.name
        )
        for codename in DEFAULT_PERMISSIONS_CHIEFS:
            chiefs.permissions.add(
                Permission.objects.get(codename=codename)
            )

        chiefs.permissions.add(manage_associates)
        chiefs.save()

        associates = Group.objects.create(
            name='associates-' + instance.name
        )
        for codename in DEFAULT_PERMISSIONS_ASSOCIATES:
            associates.permissions.add(
                Permission.objects.get(codename=codename)
            )

        associates.save()

        try:
            vice_presidents = Group.objects.get(name='vice_presidents')
        except ObjectDoesNotExist:
            pass
        else:
            vice_presidents.permissions.add(manage_chiefs)
            vice_presidents.save()
