#-*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.db.models import Model
from contrib.models import TimeStampedDescription
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from users.models import User

# Table d'archivage des notifications?

# Modèle notifications (stocke les notifications générées par ailleurs)


class Notification(models.Model):
    """
    Notifications est la table qui stocke les notifications des users.
    """

    # TODO : sécu, auth
    # TODO : décider si on_delete=models.CASCADE ou non
    # TODO : mails
    # TODO : sms
    # TODO : fuseau horaire/ utc?
    # TODO : se vide automatiquement
    # TODO : notifications de masse

    # Attributs

    # Catégorie : catégorie de la notification (admin, argent, etc)

    CATEGORY_CHOICES = (
        ('ADMIN', 'admin'),
        ('FUNDS', 'funds'),
        ('FOYER', 'foyer'),
        ('AUBERGE', 'auberge'),
        ('OTHER', 'other'),
    )

    category = models.CharField(choices=CATEGORY_CHOICES, max_length=10, default='OTHER')

    # type : correspond aux types de messages (par défaut, ceux proposés par middleware message)

    TYPE_CHOICES = (
        ('DEBUG', 'debug'),
        ('SUCCESS', 'success'),
        ('INFO', 'info'),
        ('WARNING', 'warning'),
        ('ERROR', 'error'),
    )

    type = models.CharField(choices=TYPE_CHOICES, max_length=10, default='INFO')

    # actor : l'objet qui réalise l'action.
    actor_type = models.ForeignKey(ContentType, related_name='notification_actor', on_delete=models.CASCADE) # la notification est supprimée si l'actor est supprimé
    actor_id = models.PositiveIntegerField()
    actor_object = GenericForeignKey('actor_type', 'actor_id')

    # verb : phrase verbale qui décrit l'action réalisée.
    verb = models.TextField()

    # target_user : user cible de la notification, chez qui elle sera affichée
    target_user = models.ForeignKey('users.User', related_name='notification_target_user', on_delete=models.CASCADE)

    # action medium (option): objet support de l'action
    action_medium_type = models.ForeignKey(ContentType, related_name='notification_action_medium', blank=True, null=True, on_delete=models.CASCADE) # la notification est supprimée si l'action medium est supprimé
    action_medium_id = models.PositiveIntegerField(blank=True, null=True)
    action_medium_object = GenericForeignKey('action_medium_type', 'action_medium_id')

    # target (option): objet pour lequel l'action est réalisée
    target_type = models.ForeignKey(ContentType, related_name='notification_target', blank=True, null=True, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(blank=True, null=True)
    target_object = GenericForeignKey('target_type', 'target_id')

    # creation_date: date de création de la notification
    creation_datetime = models.DateTimeField(auto_now_add=True)

    # displayed : est ce que la notification a été affichée
    is_displayed = models.BooleanField(default=False)
    displayed_date = models.DateTimeField(blank=True, null=True)

    # readed : est ce que la notification a été lue (cad l'user a cliqué dessus)?
    is_readed = models.BooleanField(default=False)
    readed_date = models.DateTimeField(blank=True, null=True)

    # Méthodes

# Méthodes


def get_undisplayed_notifications_for_user(request):
    """
    Récupère les notifications non affichées et les passe au middleware message

    :param request:
    :return: un str vide pour ne pas altérer le html
    """
    try:
        notifications_for_user = Notification.objects.filter(target_user=request.user,  is_displayed=False) # Filtre la table de notification à la recherche des notifications qui concernent l'utilisateur et qui n'ont pas été affichées

        if notifications_for_user:  # Si la liste n'est pas vide...
            for e in notifications_for_user:
                if e.type == "DEBUG":
                    messages.add_message(request, messages.DEBUG, str(e.actor_object) + " " + e.verb + " " + str(e.action_medium_object) + ".")  # Passe le message au middleware message
                elif e.type == "SUCCESS":
                    messages.add_message(request, messages.SUCCESS,  str(e.actor_object) + " " + e.verb + " " + str(e.action_medium_object) + ".")
                elif e.type == "INFO":
                    messages.add_message(request, messages.INFO, str(e.actor_object) + " " + e.verb + " " + str(e.action_medium_object) + ".")
                elif e.type == "WARNING":
                    messages.add_message(request, messages.WARNING, str(e.actor_object) + " " + e.verb + " " + str(e.action_medium_object) + ".")
                elif e.type == "ERROR":
                    messages.add_message(request, messages.ERROR, str(e.actor_object) + " " + e.verb + " " + str(e.action_medium_object) + ".")

                e.is_displayed = True  # Enregistre l'affichage dans la base de donnée
                e.displayed_date = now()  # Ainsi que la date d'affichage
                e.save()

        else:
            messages.add_message(request, messages.INFO, "Il n'y a pas de nouvelles notifications pour toi " + request.user.first_name)

    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO, "Il y a un problème avec les notifications! Signale le à un admin! ")

    return ""  # Nécessaire sinon retourne un beau none dans le html

# Centralisation des méthodes de notification

# Application Shops


def determine_notification_category(product):

    if product.product_base.shop.name == 'Foyer':
        category = 'FOYER'
    elif product.product_base.shop.name == 'Auberge':
        category = 'AUBERGE'
    else:
        category = 'OTHER'

    return category

# CRUD shop


    """
    def shop_creation_notify_success_to_user(request, shop):
    """"""
    Crée une notification de succès à destination de l'user qui a créé le shop

    :param request:
    :param shop:
    :return: nothing
    """"""
    Notification.objects.create(type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a créé le shop",
                                target_user=request.user,
                                action_medium_id=shop.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='shop')
                                )


def shop_updating_notify_success_to_user(request, shop):
    """"""
    Crée une notification de succès à destination de l'user qui a modifié le shop

    :param request:
    :param shop:
    :return: nothing
    """"""
    Notification.objects.create(type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a modifié le shop",
                                target_user=request.user,
                                action_medium_id=shop.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='shop')
                                )


def shop_deletion_notify_success_to_user(request, shop, shop_name):
    """"""
    Crée une notification de succès à destination de l'user qui a supprimé le shop

    :param request:
    :param shop:
    :param shop_name:
    :return:
    """"""
    Notification.objects.create(type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a supprimé le shop" + str(shop_name),
                                target_user=request.user,
                                action_medium_id=shop.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='shop')
                                )
"""
# CRUD SingleProduct


def single_product_creation_notify_success_to_user_and_admins(request, single_product):
    """
    Crée une notification de succès à destination de l'user qui a créé le produit unitaire

    :param request:
    :param single_product:
    :return: nothing
    """

    Notification.objects.create(category=determine_notification_category(single_product),
                                type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a créé le produit unitaire",
                                target_user=request.user,
                                action_medium_id=single_product.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='singleproduct')
                                )

    for user in User.objects.filter(groups__in={1, 2}):

        Notification.objects.create(category='ADMIN',
                                    type="SUCCESS",
                                    actor_id=request.user.pk,
                                    actor_type=ContentType.objects.get(app_label='users', model='user'),
                                    verb="a créé le produit unitaire",
                                    target_user=user,
                                    action_medium_id=single_product.pk,
                                    action_medium_type=ContentType.objects.get(app_label='shops', model='singleproduct')
                                    )

"""def single_product_updating_notify_success_to_user(request, single_product):
    """"""
    Crée une notification de succès à destination de l'user qui a modifié le produit unitaire

    :param request:
    :param single_product
    :return: nothing
    """"""
    Notification.objects.create(type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a modifié le produit unitaire",
                                target_user=request.user,
                                action_medium_id=single_product.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='singleproduct')
                                )


def single_product_deletion_notify_success_to_user(request, single_product, single_product_name):
    """"""
    Crée une notification de succès à destination de l'user qui a supprimé le produit unitaire

    :param request:
    :param single_product
    :param single_product_name
    :return: nothing
    """"""
    Notification.objects.create(type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a supprimé le produit unitaire " + str(single_product_name),
                                target_user=request.user,
                                action_medium_id=single_product.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='singleproduct')
                                )
"""
# CRUD Container


def container_creation_notify_success_to_user_and_admins(request, container):
    """
    Crée une notification de succès à destination de l'user qui a créé le container

    :param request:
    :param container
    :return: nothing
    """

    Notification.objects.create(category=determine_notification_category(container),  # Permet de déterminer si notification foyer, auberge, ... CF. fonction
                                type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a créé le container",
                                target_user=request.user,
                                action_medium_id=container.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='container')
                                )

    for user in User.objects.filter(groups__in={1, 2}):

        Notification.objects.create(category='ADMIN',
                                    type="SUCCESS",
                                    actor_id=request.user.pk,
                                    actor_type=ContentType.objects.get(app_label='users', model='user'),
                                    verb="a créé le container",
                                    target_user=user,
                                    action_medium_id=container.pk,
                                    action_medium_type=ContentType.objects.get(app_label='shops', model='container')
                                    )


"""def container_updating_notify_success_to_user(request, container):
    """"""
    Crée une notification de succès à destination de l'user qui a modifié le container

    :param request:
    :param container
    :return: nothing
    """"""
    Notification.objects.create(type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a modifié le container",
                                target_user=request.user,
                                action_medium_id=container.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='container')
                                )


def container_deletion_notify_success_to_user(request, container, container_name):
    """"""
    Crée une notification de succès à destination de l'user qui a supprimé le container

    :param request:
    :param container
    :param container_name
    :return: nothing
    """"""
    Notification.objects.create(type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a supprimé le container " + str(container_name),
                                target_user=request.user,
                                action_medium_id=container.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='singleproduct')
                                )
    """

# CRUD Product Unit


def product_unit_creation_notify_success_to_user_and_admins(request, product_unit):
    """

    :param request:
    :param product_unit:
    :return: nothing
    """

    Notification.objects.create(category='OTHER',
                                type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a créé l'unité de produit",
                                target_user=request.user,
                                action_medium_id=product_unit.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='productunit')
                                )

    for user in User.objects.filter(groups__in={1, 2}):

        Notification.objects.create(category='ADMIN',
                                    type="SUCCESS",
                                    actor_id=request.user.pk,
                                    actor_type=ContentType.objects.get(app_label='users', model='user'),
                                    verb="a créé l'unité de produit",
                                    target_user=user,
                                    action_medium_id=product_unit.pk,
                                    action_medium_type=ContentType.objects.get(app_label='shops', model='productunit')
                                    )


def product_unit_updating_notify_success_to_user_and_admins(request, product_unit):
    """

    :param request:
    :param product_unit:
    :return: nothing
    """

    Notification.objects.create(category='OTHER',
                                type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a mis à jour l'unité de produit",
                                target_user=request.user,
                                action_medium_id=product_unit.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='productunit')
                                )

    for user in User.objects.filter(groups__in={1, 2}):

        Notification.objects.create(category='ADMIN',
                                    type="SUCCESS",
                                    actor_id=request.user.pk,
                                    actor_type=ContentType.objects.get(app_label='users', model='user'),
                                    verb="a mis à jour l'unité de produit",
                                    target_user=user,
                                    action_medium_id=product_unit.pk,
                                    action_medium_type=ContentType.objects.get(app_label='shops', model='productunit')
                                    )


def product_unit_deletion_notify_success_to_user_and_admins(request, product_unit):
    """

    :param request:
    :param product_unit:
    :return: nothing
    """

    Notification.objects.create(category='OTHER',
                                type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a supprimé l'unité de produit " + product_unit.name,
                                target_user=request.user,
                                action_medium_id=product_unit.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='productunit')
                                )

    for user in User.objects.filter(groups__in={1, 2}):

        Notification.objects.create(category='ADMIN',
                                    type="SUCCESS",
                                    actor_id=request.user.pk,
                                    actor_type=ContentType.objects.get(app_label='users', model='user'),
                                    verb="a supprimé l'unité de produit " + product_unit.name,
                                    target_user=user,
                                    action_medium_id=product_unit.pk,
                                    action_medium_type=ContentType.objects.get(app_label='shops', model='productunit')
                                    )


# CRUD Product Base


def product_base_creation_notify_success_to_user_and_admins(request, product_base):
    """

    :param request:
    :param product_base:
    :return: nothing
    """

    Notification.objects.create(category='OTHER',
                                type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a créé la base produit",
                                target_user=request.user,
                                action_medium_id=product_base.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='productbase')
                                )

    for user in User.objects.filter(groups__in={1, 2}):

        Notification.objects.create(category='ADMIN',
                                    type="SUCCESS",
                                    actor_id=request.user.pk,
                                    actor_type=ContentType.objects.get(app_label='users', model='user'),
                                    verb="a créé la base produit",
                                    target_user=user,
                                    action_medium_id=product_base.pk,
                                    action_medium_type=ContentType.objects.get(app_label='shops', model='productbase')
                                    )


def product_base_updating_notify_success_to_user_and_admins(request, product_base):
    """

    :param request:
    :param product_base:
    :return: nothing
    """

    Notification.objects.create(category='OTHER',
                                type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a mis à jour la base produit",
                                target_user=request.user,
                                action_medium_id=product_base.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='productbase')
                                )

    for user in User.objects.filter(groups__in={1, 2}):

        Notification.objects.create(category='ADMIN',
                                    type="SUCCESS",
                                    actor_id=request.user.pk,
                                    actor_type=ContentType.objects.get(app_label='users', model='user'),
                                    verb="a mis à jour la base produit",
                                    target_user=user,
                                    action_medium_id=product_base.pk,
                                    action_medium_type=ContentType.objects.get(app_label='shops', model='productbase')
                                    )


def product_base_deletion_notify_success_to_user_and_admins(request, product_base):
    """

    :param request:
    :param product_base:
    :return: nothing
    """

    Notification.objects.create(category='OTHER',
                                type="SUCCESS",
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                verb="a supprimé la base produit " + product_base.name,
                                target_user=request.user,
                                action_medium_id=product_base.pk,
                                action_medium_type=ContentType.objects.get(app_label='shops', model='productbase')
                                )

    for user in User.objects.filter(groups__in={1, 2}):

        Notification.objects.create(category='ADMIN',
                                    type="SUCCESS",
                                    actor_id=request.user.pk,
                                    actor_type=ContentType.objects.get(app_label='users', model='user'),
                                    verb="a supprimé la base produit " + product_base.name,
                                    target_user=user,
                                    action_medium_id=product_base.pk,
                                    action_medium_type=ContentType.objects.get(app_label='shops', model='productbase')
                                    )
