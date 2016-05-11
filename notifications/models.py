#-*- coding: utf-8 -*-
from django.db import models, IntegrityError
from django.db.models import Q
from django.db.models import Model
from contrib.models import TimeStampedDescription
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from django import template

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

    # displayed_date : est ce que la notification a été affichée
    displayed_date = models.DateTimeField(blank=True, null=True)

    # read_date : est ce que la notification a été lue (cad l'user a cliqué dessus)?
    read_date = models.DateTimeField(blank=True, null=True)

    # Méthodes


class NotificationClass(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    creation_datetime = models.DateTimeField(auto_now_add=True)
    last_call_datetime = models.DateTimeField(blank=True, null=True)


class NotificationTemplate(models.Model):
    notification_class = models.ForeignKey('NotificationClass')
    message_template = models.TextField(blank=True, null=True)
    target_group_template = models.ForeignKey(Group, blank=True, null=True)
    target_user_template = models.CharField(max_length=20, blank=True, null=True)

    CATEGORY_CHOICES = (
        ('ADMIN', 'admin'),
        ('FUNDS', 'funds'),
        ('FOYER', 'foyer'),
        ('AUBERGE', 'auberge'),
        ('OTHER', 'other'),
    )

    category_template = models.CharField(choices=CATEGORY_CHOICES, max_length=10, default='OTHER')

    # type : correspond aux types de messages (par défaut, ceux proposés par middleware message)

    TYPE_CHOICES = (
        ('DEBUG', 'debug'),
        ('SUCCESS', 'success'),
        ('INFO', 'info'),
        ('WARNING', 'warning'),
        ('ERROR', 'error'),
    )

    type_template = models.CharField(choices=TYPE_CHOICES, max_length=10, default='INFO')
    creation_datetime = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    last_call_datetime = models.DateTimeField(blank=True, null=True)
    is_activated = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ('notification_templates_manage', 'Gérer les template de notification'),
        )


# Méthodes


def notify(request, name, target_user_list, action_medium, target_object):
    """
    Notifie l'utilisateur cible (ou le groupe d'utilisateurs cible) d'après un template de notification qui dérive d'une
    classe de notification. Si ces éléments prérequis n'existent pas, ils sont créés et doivent être configurés via
    l'interface web (cf. documentation)
    :param request:
    :param name:
    :param target_user_list:
    :param action_medium:
    :param target_object:
    :return:
    """

    # Vérification du type list des attributs
    if not isinstance(target_user_list, list):
        raise TypeError("target_user_list must be a list")
    try:
        notification_class = NotificationClass.objects.get(name=name)
        if NotificationTemplate.objects.filter(notification_class=notification_class).exists():
            # Vérifions d'abord qu'il n'y a pas de nouveaux target_user, pour lesquels il faut créer un template
            create_notification_template(notification_class, target_user_list)
            notification_templates = order_target_user_list(NotificationTemplate.objects.filter(notification_class=notification_class))
            create_notification(request, notification_templates, action_medium, target_object)
        else:
            create_notification_template(notification_class, target_user_list)
    except ObjectDoesNotExist:
        try:
            notification_class = NotificationClass.objects.create(name=name, last_call_datetime=now())
            create_notification_template(notification_class, target_user_list)
        except IntegrityError:
            raise IntegrityError("Le nom de la classe de notifications doit être unique")


def create_notification_template(notification_class, target_user_list):
    """
    Crée des templates de notifications associés à des users cibles lorsqu'ils n'existent pas. Ces templates sont
    désactivés par défaut et doivent être activés par l'administateur une fois qu'il les a paramétrés via l'interface
    web
    :param notification_class:
    :param target_user_list:
    :return:
    """
    # Cf. users/fixtures/groups.json pour liste groupes
    for target_user in target_user_list:
        if target_user == 'User':
            if not NotificationTemplate.objects.filter(notification_class=notification_class,
                                                       target_user_template="User").exists():
                NotificationTemplate.objects.create(notification_class=notification_class,
                                                    target_user_template="User",
                                                    last_call_datetime=now())
        elif target_user == 'Recipient':
            if not NotificationTemplate.objects.filter(notification_class=notification_class,
                                                       target_user_template="Recipient").exists():
                NotificationTemplate.objects.create(notification_class=notification_class,
                                                    target_user_template="Recipient",
                                                    last_call_datetime=now())
        else:
            if not NotificationTemplate.objects.filter(notification_class=notification_class,
                                                       target_group_template=Group.objects.get(name=target_user)).exists():
                NotificationTemplate.objects.create(notification_class=notification_class,
                                                    target_group_template=Group.objects.get(name=target_user),
                                                    last_call_datetime=now())


def order_target_user_list(notifications_templates):
    """
    Trie les template en fonction des groupes d'user concernés dans un ordre prédéfini afin s'assurer de ce dernier peut
    importe l'ordre de la liste que le développeur donne en argument à la fonction
    :param notifications_templates:
    :return:
    """
    # Initialisation des listes de manière à pouvoir appeler la méthode append() dessus par la suite
    sorting_list = []
    sorting_list_bis = []

    # Pour chaque template de notification associé à l'action
    for notifications_template in notifications_templates:
        # Récupération du groupe cible de la notification, ou l'user à défaut
        if notifications_template.target_group_template is None:
            name = notifications_template.target_user_template
        else:
            name = notifications_template.target_group_template.name
        # Création d'une liste intermédiare avec des couples (niveau du groupe, template associé)
        sorting_list.append((determine_group_level(name), notifications_template))
    # Tri de la liste intermédiaire sur les niveaux
    sorting_list.sort()

    # Création de la liste finale ne comprenant que les templates triés
    for e in sorting_list:
        sorting_list_bis.append(e[1])
    return sorting_list_bis


def determine_group_level(group):
    """
    Retourne le niveau prédéterminé de chaque groupe
    :param group:
    :return:
    """
    group_levels = (("User", -1),
                    ("Recipient", 0),
                    ("Présidents", 1),
                    ("Vices présidents délégués à la vie interne", 2),
                    ("Trésoriers", 3),
                    ("Chefs gestionnaires du foyer", 4),
                    ("Chefs gestionnaires de l'auberge", 5),
                    ("Gestionnaires du foyer", 6),
                    ("Gestionnaires de l'auberge", 7),
                    ("Chefs gestionnaires de la C-Vis", 8),
                    ("Gestionnaires de la C-Vis", 9),
                    ("Gadz'Arts", 10),
                    ("Membres d'honneurs", 11),
                    ("Membres spéciaux", 12),
                    )
    for group_level in group_levels:
        if group_level[0] == group:
            return group_level[1]


def create_notification(request, notification_templates, action_medium, target_object):
    """
    Crée des notifications pour un template donné, en veillant à éviter les doublons de notifications pour un
    utilisateur qui aurait plusieurs rôles au sein de l'association
    :param request:
    :param notification_templates:
    :param action_medium:
    :param target_object:
    :return:
    """
    already_notified_users = []
    for template in notification_templates:
        if template.is_activated:
            print("A")
            target_user_group = []
            if template.target_group_template is None:
                if template.target_user_template == "User":
                    if request.user.is_authenticated():
                        target_user_group = [User.objects.get(pk=request.user.pk)]
                if template.target_user_template == "Recipient":
                    if action_medium != request.user:
                        target_user_group = [User.objects.get(pk=action_medium.pk)]
            else:
                print("B")
                print(User.objects.filter(groups=template.target_group_template))
                target_user_group = [n for n in User.objects.filter(groups=template.target_group_template) if n not in already_notified_users]
                print(target_user_group)
                already_notified_users = already_notified_users + target_user_group

            if action_medium is None:
                action_medium_id = None
                action_medium_type = None
            else:
                action_medium_id = action_medium.pk
                action_medium_type = ContentType.objects.get_for_model(action_medium)

            if target_object is None:
                target_object_id = None
                target_object_type = None
            else:
                target_object_id = target_object.pk
                target_object_type = ContentType.objects.get_for_model(target_object)

            for target_user in target_user_group:
                Notification.objects.create(category=template.category_template,
                                            type=template.type_template,
                                            actor_id=request.user.pk,
                                            actor_type=ContentType.objects.get(app_label='users', model='user'),
                                            verb=template.message_template,
                                            target_user=target_user,
                                            action_medium_id=action_medium_id,
                                            action_medium_type=action_medium_type,
                                            target_id=target_object_id,
                                            target_type=target_object_type,
                                            )


def get_unread_notifications_for_user(request):
    """
    Récupère les notifications non affichées et les passe au middleware message

    :param request:
    :return: un str vide pour ne pas altérer le html
    """
    try:
        notifications_for_user = Notification.objects.filter(target_user=request.user,  read_date=None) # Filtre la table de notification à la recherche des notifications qui concernent l'utilisateur et qui n'ont pas été affichées

        if notifications_for_user:  # Si la liste n'est pas vide...
            for e in notifications_for_user:
                # https://docs.djangoproject.com/fr/1.9/ref/contrib/messages/
                # Message levels:
                # DEBUG : 10
                # INFO : 20
                # SUCCESS : 25
                # WARNING : 30
                # ERROR : 40

                if e.type == "DEBUG":
                    message_level = 10

                elif e.type == "INFO":
                    message_level = 20

                elif e.type == "SUCCESS":
                    message_level = 25

                elif e.type == "WARNING":
                    message_level = 30

                elif e.type == "ERROR":
                    message_level = 40

                else:
                    # Par défaut le message est de type INFO
                    message_level = 20

                # Ajout de la notification au middleware message
                messages.add_message(request,
                                     message_level,
                                     template.Template(
                                         "Le " + str(e.creation_datetime.day) + '/' + str(e.creation_datetime.month) +
                                         '/' + str(e.creation_datetime.year) + ' à ' + str(e.creation_datetime.hour) +
                                         ':' + str(e.creation_datetime.minute) + "\n" + e.verb).render(
                                         template.Context({'recipient': e.action_medium_object},
                                                          {'object': e.action_medium_object})),
                                     extra_tags=e.pk)

                # Prise en compte de l'affichage de la notification pour utilisation ultérieure
                if e.displayed_date is None:
                    e.displayed_date = now()
                    e.save()

    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO, "Il n'y a pas de notifications associées à cet user ")

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
