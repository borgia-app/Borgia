#-*- coding: utf-8 -*-
from django.db import models, IntegrityError
from django.db.models import Model, Max
from contrib.models import TimeStampedDescription
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group, Permission
from django import template
from shops.models import Shop
from lxml import etree
from annoying.fields import AutoOneToOneField

from django.utils.html import conditional_escape

from users.models import User

# Modèle notifications (stocke les notifications générées par ailleurs)


class Notification(models.Model):
    """
    Table des notifications.
    """

    # TODO : sécu, auth
    # TODO : décider si on_delete=models.CASCADE ou non
    # TODO : mails
    # TODO : sms
    # TODO : fuseau horaire/ utc?
    # TODO : se vide automatiquement
    # TODO : notifications de masse

    class Meta:
        default_permissions = (
            'list',
        )
    # Attributs

    # Catégorie : catégorie de la notification (admin, argent, etc)

    category = models.ForeignKey('shops.Shop', blank=True, null=True)

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

    # notification_template : template xml qui va permettre de générer la notification
    notification_template = models.ForeignKey('NotificationTemplate', blank=True, null=True, on_delete=models.CASCADE)

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
    creation_datetime = models.DateTimeField(auto_now_add=True, editable=False)

    # displayed_date : est ce que la notification a été affichée
    displayed_date = models.DateTimeField(blank=True, null=True, editable=False)

    # read_date : est ce que la notification a été lue (cad l'user a cliqué dessus)?
    read_date = models.DateTimeField(blank=True, null=True)

    # Méthodes


class NotificationClass(models.Model):
    """
    Table des classes de notifications. Une classe correspond à une action (exemple: création user) et fait référence à
    un ou plusieurs templates créés pour des publics différents.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    creation_datetime = models.DateTimeField(auto_now_add=True)
    last_call_datetime = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class NotificationTemplate(models.Model):
    """
    Table des templates de notification. Un template se présente sous la forme de texte xml éditable par l'utilisateur,
    à l'aide de balises dédiées.
    """
    notification_class = models.ForeignKey('NotificationClass',
                                           on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)

    class Meta:
        default_permissions = (
            'list',
            'add',
            'change',
            'delete',
        )

    TARGET_USERS_CHOICES = (
        ('ACTOR', 'actor'),
        ('RECIPIENT', 'recipient'),
        ('TARGET_GROUPS', 'one or many target groups'),
    )

    target_users = models.CharField(choices=TARGET_USERS_CHOICES, max_length=20, default='ACTOR')

    target_groups = models.ManyToManyField('NotificationGroup', blank=True)

    category = models.ForeignKey('shops.Shop', blank=True, null=True)

    # type : correspond aux types de messages (par défaut, ceux proposés par middleware message)

    TYPE_CHOICES = (
        ('DEBUG', 'debug'),
        ('SUCCESS', 'success'),
        ('INFO', 'info'),
        ('WARNING', 'warning'),
        ('ERROR', 'error'),
    )

    type = models.CharField(choices=TYPE_CHOICES, max_length=10, default='INFO')

    creation_datetime = models.DateTimeField(auto_now_add=True, editable=False)
    update_date = models.DateTimeField(auto_now=True, editable=False)
    last_call_datetime = models.DateTimeField(blank=True, null=True, editable=False)
    is_activated = models.BooleanField(default=False)


class NotificationGroup(models.Model):
    """

    """
    class Meta:
        default_permissions = (
            'list',
            'add',
            'change',
        )
    def __str__(self):
        return self.notificationgroup.name
    notificationgroup = AutoOneToOneField('auth.Group', unique=True)
    weight = models.IntegerField(default=0)

# Méthodes


def notify(request, notification_class_name, recipient=False, action_medium=False, target_object=False):
    """
    Notifie l'utilisateur cible (ou le groupe d'utilisateurs cible) d'après un template de notification qui dérive d'une
    classe de notification. Si ces éléments prérequis n'existent pas, ils sont créés et doivent être configurés via
    l'interface web (cf. documentation)
    :param request:
    :param notification_class_name:
    :param recipient:
    :param action_medium:
    :param target_object:
    :return:
    """

    try:
        notification_class = NotificationClass.objects.get_or_create(name=notification_class_name,
                                                                     defaults={'last_call_datetime': now()})
        notified_users = []

        if not notification_class[1]:
            # Warning: notification_class is a tuple returned by get_or_create with the queryset as the first value
            try:
                for group in NotificationGroup.objects.\
                        filter(notificationtemplate__notification_class=notification_class[0],
                               notificationtemplate__is_activated=True,
                               notificationtemplate__target_users='TARGET_GROUPS').\
                        exclude(notificationgroup__name='specials').\
                        order_by('-weight'):

                    for user in User.objects.filter(groups=group.notificationgroup, is_active=True):
                        if user not in notified_users:
                            create_notification(
                                request,
                                user,
                                NotificationTemplate.objects.get(notification_class=notification_class[0],
                                                                 target_groups=group,
                                                                 target_users='TARGET_GROUPS',
                                                                 is_activated=True),
                                action_medium,
                                target_object)
                            notified_users.append(user)

            except ObjectDoesNotExist:
                pass

            try:
                create_notification(
                    request,
                    request.user,
                    NotificationTemplate.objects.get(notification_class=notification_class[0],
                                                     target_users='ACTOR',
                                                     is_activated=True),
                    action_medium,
                    target_object)
            except ObjectDoesNotExist:
                pass

            if recipient:
                try:
                    create_notification(
                        request,
                        recipient,
                        NotificationTemplate.objects.get(notification_class=notification_class[0],
                                                         target_users='RECIPIENT',
                                                         is_activated=True),
                        action_medium,
                        target_object)
                except ObjectDoesNotExist:
                    pass

    except IntegrityError:
        raise IntegrityError("Le nom de la classe de notifications doit être unique")


def create_notification(request, user, notification_template, action_medium=False, target_object=False):
    """
    Crée des notifications pour un notification_template donné, en veillant à éviter les doublons de notifications pour un
    utilisateur qui aurait plusieurs rôles au sein de l'association
    :param request:
    :param user:
    :param notification_template:
    :param action_medium:
    :param target_object:
    :return:
    """

    if not action_medium:
        action_medium_id = None
        action_medium_type = None
    else:
        action_medium_id = action_medium.pk
        action_medium_type = ContentType.objects.get_for_model(action_medium)

    if not target_object:
        target_object_id = None
        target_object_type = None
    else:
        target_object_id = target_object.pk
        target_object_type = ContentType.objects.get_for_model(target_object)

    Notification.objects.create(category=notification_template.category,
                                type=notification_template.type,
                                actor_id=request.user.pk,
                                actor_type=ContentType.objects.get(app_label='users', model='user'),
                                notification_template=notification_template,
                                target_user=user,
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
        notifications_for_user = Notification.objects.filter(target_user=request.user,
                                                             read_date=None) # Filtre la table de notification à la recherche des notifications qui concernent l'utilisateur et qui n'ont pas été affichées

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
                                         ':' + str(e.creation_datetime.minute) + "\n" +
                                         template_rendering_engine(NotificationTemplate.objects.get(
                                             pk=e.notification_template.pk).message)).render(template.Context({'recipient': e.action_medium_object,
                                                                          'object': e.action_medium_object,
                                                                          'actor': e.actor_object})),
                                     extra_tags=e.pk)

                # Prise en compte de l'affichage de la notification pour utilisation ultérieure
                if e.displayed_date is None:
                    e.displayed_date = now()
                    e.save()

    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO, "Il n'y a pas de notifications associées à cet user ")

    return ""  # Nécessaire sinon retourne un beau none dans le html


def determine_notification_category(product):

    if product.product_base.shop.name == 'Foyer':
        category = 'FOYER'
    elif product.product_base.shop.name == 'Auberge':
        category = 'AUBERGE'
    else:
        category = 'OTHER'

    return category


def xml_parser(node, parsed_xml=""):
    """
    Lit un noeud xml généré par minidom et remplace les balises reconnues par des balises html. Le reste du texte est
    échappé par sécurité.
    :param node:
    :param parsed_xml:
    :return:
    """

    # Si parsed_xml est vide, il n'existe pas de texte à insérer et il faut récupérer la valeur de la balise
    if not parsed_xml:
        if node.text is None:
            text = ""
        else:
            text = conditional_escape(node.text)
        if node.tail is None:
            tail = ""
        else:
            tail = conditional_escape(node.tail)
    else:
        text = parsed_xml
        tail = ""

    # Reconnaissance des balises et remplacement
    try:
        tag_dictionary = get_allowed_tags()
        html_result = tag_dictionary[node.tag][0] + text + tag_dictionary[node.tag][1] + tail
    except KeyError:
        html_result = conditional_escape(etree.tostring(node))

    return html_result


def recursive_parser(tree):
    """
    Fonction récursive qui permet de lire l'ensemble de l'arbre xml généré par lxml
    :param tree: Arbre xml
    :return:
    """
    parsed_xml = ""

    # tree.iter() construit un itérateur qui renvoit une liste des noeuds de l'arbre (les plus profonds en premier)
    for node in tree.iter():
        parsed_xml += xml_parser(node)

    return xml_parser(tree, parsed_xml)


def template_xml_tree_builder(xml_body):
    """
    Construit l'arbre xml associé au template d'une notificatipn grâce à lxml
    :param xml_body:
    :return:
    """
    # Ajout d'une une balise d'encadrement bcode qui générera une div bcode dans le html pour un éventuel traitement
    xml_header = "<bcode>"
    xml_footer = "</bcode>"
    xml_template = xml_header + xml_body + xml_footer

    return etree.fromstring(xml_template, parser=etree.XMLParser(recover=True))


def template_rendering_engine(xml_body):
    """
    Génère le code html associé à un template xml
    :param xml_body:
    :return:
    """
    xml_tree = template_xml_tree_builder(xml_body)

    return recursive_parser(xml_tree)


def get_allowed_tags():
    """

    :return:
    """
    tag_dictionary = {'bold': ('<strong>', '</strong>'),
                      'actor': ('<a href="{% url "url_user_retrieve" pk=actor.pk group_name=group_name %}">'
                                '{{actor}}</a>', ''),
                      '#text': ('', ''),
                      'bcode': ('<div class="bcode">', '</div>')}

    return tag_dictionary
