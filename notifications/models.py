from annoying.fields import AutoOneToOneField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models.signals import m2m_changed, pre_save
from django.db.utils import IntegrityError
from django.dispatch.dispatcher import receiver
from django.utils.html import conditional_escape
from django.utils.timezone import now
from lxml import etree


# TODO: make it work with users.models
# Classes
class Notification(models.Model):
    """"
    A notification represents an user side log, saved for informative purposes.
    Notifications are saved when the "notify" method is called and only if the app is well configured.
    :param notification_class : a notification class represents the action for which the "notify" method is called
    :param shop_category : when a notification is related with a shop, null otherwise
    :param target_category : defines for which user category the notification stands for. Can't be null.
    :param group_category : if target_category is set to "TARGET_GROUPS", specifies which group
    :param type : string must be in TYPE_CHOICES
    :param actor_type : GenericForeignKey. The actor is the user or the entity which performs the action
    :param actor_id : GenericForeignKey
    :param actor_object : GenericForeignKey
    :param target_user : is the target of the notification, i.e. its recipient
    :param action_medium_type : GenericForeignKey. It's the medium through which the action is performed, e.g. a shop.
    :param action_medium_id : GenericForeignKey
    :param action_medium_object : GenericForeignKey
    :param target_type : GenericForeignKey. It's the object on which the action is performed, e.g. a product.
    :param target_id : GenericForeignKey
    :param target_object : GenericForeignKey
    :param creation_datetime : the notification creation date
    :param displayed_datetime : null if the notification was never displayed
    :param read_datetime : null if the notification is unread
    """

    # TODO : décider si on_delete=models.CASCADE ou non
    # TODO : mails
    # TODO : sms
    # TODO : fuseau horaire/ utc?

    class Meta:
        """
        Defines auto-generated permissions. Allow an user to add, edit or delete a notification does not make sense,
        then the only permission is to list notifications.
        """
        default_permissions = (
            'list',
        )

    notification_class = models.ForeignKey(
        'NotificationClass', blank=True, null=True, on_delete=models.CASCADE)

    shop_category = models.ForeignKey(
        'shops.Shop', blank=True, null=True, on_delete=models.CASCADE)

    target_category = models.CharField(max_length=20, default='ACTOR')

    group_category = models.ForeignKey(
        'NotificationGroup', blank=True, null=True, on_delete=models.CASCADE)

    TYPE_CHOICES = (
        ('DEBUG', 'debug'),
        ('SUCCESS', 'success'),
        ('INFO', 'info'),
        ('WARNING', 'warning'),
        ('ERROR', 'error'),
    )

    type = models.CharField(choices=TYPE_CHOICES,
                            max_length=10, default='INFO')

    actor_type = models.ForeignKey(
        ContentType, related_name='notification_actor', on_delete=models.CASCADE)
    # CASCADE : the notification is deleted if the related actor object is deleted
    actor_id = models.PositiveIntegerField()
    actor_object = GenericForeignKey('actor_type', 'actor_id')

    target_user = models.ForeignKey(
        'users.User', related_name='notification_target_user', on_delete=models.CASCADE)

    action_medium_type = models.ForeignKey(ContentType,
                                           related_name='notification_action_medium',
                                           blank=True,
                                           null=True,
                                           on_delete=models.CASCADE)
    action_medium_id = models.PositiveIntegerField(blank=True, null=True)
    action_medium_object = GenericForeignKey(
        'action_medium_type', 'action_medium_id')

    target_type = models.ForeignKey(ContentType,
                                    related_name='notification_target',
                                    blank=True,
                                    null=True,
                                    on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(blank=True, null=True)
    target_object = GenericForeignKey('target_type', 'target_id')

    creation_datetime = models.DateTimeField(auto_now_add=True, editable=False)

    displayed_datetime = models.DateTimeField(
        blank=True, null=True, editable=False)

    read_datetime = models.DateTimeField(blank=True, null=True)


class NotificationClass(models.Model):
    """
    A notification class represents the action for which the "notify" method is called, e.g. "user_creation"
    :param name : A string used to call it with the "notify" method
    :param description : A string to give some context about the action
    :param creation_datetime : the class notification creation date
    :param last_call_datetime : used to see when the notify method was last called with this notification class
    """
    name = models.CharField(max_length=255, unique=True)

    verbose_name = models.CharField(max_length=255, blank=True, null=True)

    description = models.TextField()

    creation_datetime = models.DateTimeField(auto_now_add=True, editable=False)

    last_call_datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        default_permissions = (
            'list',
            'change',
        )

    def __str__(self):
        """
        When the notification class object is called, e.g. in a template, display self.name instead of "a
        NotificationClass object"
        :return: notification class name
        """
        return self.name


class NotificationTemplate(models.Model):
    """
    A notification template represents the information used to generate the html template related to a notification.
    Basically, a template is a xml string.
    :param notification_class : a template is related to one performed action through a notification class
    :param xml_template : represents the template, with xml tags.
    :param target_users : defines for which target user (actor, recipient, a group : the string must be in
    string must be in TARGET_USERS_CHOICES) the notification template stands for. Can't be null.
    :param target_groups : if target_users is set to "TARGET_GROUPS", specifies which group
    :param shop_category : when a notification template is related with a shop, null otherwise
    :param type : string must be in TYPE_CHOICES
    :param creation_datetime : the notification template creation date
    :param update_datetime : the notification template update date
    :param last_call_datetime : used to see when this template was last used
    :param is_activated : True if the notification template is activated (and used)
    """
    notification_class = models.ForeignKey('NotificationClass',
                                           verbose_name='Action déclenchant la notification',
                                           on_delete=models.CASCADE)

    xml_template = models.TextField(blank=True,
                                    null=True,
                                    verbose_name='Template XML',
                                    default='Une notification.')

    class Meta:
        default_permissions = (
            'list',
            'add',
            'change',
            'deactivate',
        )

    TARGET_USERS_CHOICES = (
        ('ACTOR', 'Acteur de l\'action'),
        ('RECIPIENT', 'Utilisateur cible de l\'action'),
        ('TARGET_GROUPS', 'Un ou plusieurs groupes d\'utilisateurs'),
    )

    target_users = models.CharField(choices=TARGET_USERS_CHOICES,
                                    verbose_name='Utilisateur destinataire de la notification',
                                    max_length=20,
                                    default='ACTOR')

    target_groups = models.ManyToManyField('NotificationGroup',
                                           verbose_name='Groupe d\'utilisateurs destinataire de la notification',
                                           blank=True)

    shop_category = models.ForeignKey('shops.Shop',
                                      verbose_name='Magasin concerné par la notification',
                                      blank=True,
                                      null=True,
                                      on_delete=models.CASCADE)

    # type : correspond aux types de messages (par défaut, ceux proposés par middleware template)

    TYPE_CHOICES = (
        ('DEBUG', 'debug'),
        ('SUCCESS', 'success'),
        ('INFO', 'info'),
        ('WARNING', 'warning'),
        ('ERROR', 'error'),
    )

    type = models.CharField(choices=TYPE_CHOICES,
                            verbose_name='Type',
                            max_length=10,
                            default='INFO')

    creation_datetime = models.DateTimeField(auto_now_add=True, editable=False)
    update_datetime = models.DateTimeField(auto_now=True, editable=False)
    last_call_datetime = models.DateTimeField(
        blank=True, null=True, editable=False)

    is_activated = models.BooleanField(default=False,
                                       verbose_name='Template activé')


@receiver(m2m_changed, sender=NotificationTemplate.target_groups.through)
def target_groups_changed(instance, **kwargs):
    """
    Use a Django signal (https://docs.djangoproject.com/en/1.10/topics/signals/) to check the uniqueness of
    notification_class and target_group together when the ManyToMany field is changed. Unique_together is unusable
    with a ManyToMany field.
    Note : sender should be the through table (automatically created by Django).
    :param instance: the object saved in db, here it's a NotificationTemplate instance
    :return: raise a ValidationError if the uniqueness is not respected.
    """
    if instance.target_users == 'TARGET_GROUPS':  # The uniqueness together is only checked for groups
        for group in instance.target_groups.all():
            if NotificationTemplate.objects.filter(notification_class=instance.notification_class,
                                                   target_users='TARGET_GROUPS',
                                                   target_groups=group).\
                    exclude(pk=instance.pk).exists():
                raise ValidationError("L'un des groupes est déjà utilisé pour la même classe de notification",
                                      code='Invalid')


@receiver(pre_save, sender=NotificationTemplate)
def target_users_pre_save(instance, **kwargs):
    """
    Use a Django signal (https://docs.djangoproject.com/en/1.10/topics/signals/) to check the uniqueness of
    notification_class and target_users together (i.e., we want only one template for a given class and with "actor" as
    a target). Unique_together can not be used because there could be many 'TARGET_GROUPS'.
    :param instance: the object saved in db, here it's a NotificationTemplate instance
    :return: raise a ValidationError if the uniqueness is not respected.
    """
    if instance.target_users == "ACTOR":
        if NotificationTemplate.objects.filter(notification_class=instance.notification_class,
                                               target_users="ACTOR").exclude(pk=instance.pk).exists():
            raise ValidationError("Il existe déjà un template 'Actor' pour la même classe de notification",
                                  code='Invalid')
    elif instance.target_users == "RECIPIENT":
        if NotificationTemplate.objects.filter(notification_class=instance.notification_class,
                                               target_users="RECIPIENT").exclude(pk=instance.pk).exists():
            raise ValidationError("Il existe déjà un template 'Recipient' pour la même classe de notification",
                                  code='Invalid')


class NotificationGroup(models.Model):
    """
    Basically, it's a auth.Group table replication, used to give them a weight (note the AutoOneToOneField from Django
    annoying to ensure the replication). The auth.Group is not directly overwrite to avoid interferences.
    :param notificationgroup : a group from auth.Group through a AutoOneToOneField. Unique.
    :param weight : the weight is used to determine priority group when a user belongs to several groups, in order to
    avoid notification spam.
    """
    class Meta:
        default_permissions = (
            'list',
            'add',
            'change'
        )

    notificationgroup = AutoOneToOneField(
        'auth.Group', unique=True, on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)

    def __str__(self):
        """
        When the notification group object is called, e.g. in a template, display self.name instead of "a
        NotificationClass object"
        :return: the group name saved in auth.Group
        """
        return self.notificationgroup.name

# Methods


def notify(notification_class_name, actor, recipient=False, action_medium=False, target_object=False):
    """
    Notify the target user (or the target group) given by templates related to the class name (2nd argument).
    If the class does not exist, it is created. Templates must be configured manually through the web interface.
    Cf. dev documentation.
    :param actor: the user who performed the action
    :param notification_class_name: the name of the notification class related to the action
    :param recipient: the user who receive the action. Optional.
    :param action_medium: the medium through which the action is performed, e.g. a shop. Optional.
    :param target_object: the object on which the action is performed, e.g. a product. Optional.
    :return: True if a notification did occur, False if not.
    :rtype: bool
    """
    try:
        # Fist we check if the notification class exists. If not, we create it.
        notification_class = NotificationClass.objects.get_or_create(name=notification_class_name,
                                                                     defaults={'last_call_datetime': now()})
        notified_users = []  # Used to notify users only one time

        if not notification_class[1]:
            # Warning: notification_class is a tuple returned by get_or_create with the queryset as the first value
            try:
                for group in NotificationGroup.objects.\
                        filter(notificationtemplate__notification_class=notification_class[0],
                               notificationtemplate__is_activated=True,
                               notificationtemplate__target_users='TARGET_GROUPS').\
                        exclude(notificationgroup__name='externals').\
                        order_by('-weight'):  # Heavier group, like "President", are more important

                    for user in User.objects.filter(groups=group.notificationgroup, is_active=True):
                        if user not in notified_users:
                            create_notification(
                                notification_template=NotificationTemplate.objects.get(
                                    notification_class=notification_class[0],
                                    target_groups=group,
                                    target_users='TARGET_GROUPS',
                                    is_activated=True),
                                actor=actor,
                                target_user=user,
                                group=group,
                                action_medium=action_medium,
                                target_object=target_object)

                            # The notified user is added to the list, he will not be notified again if he belongs to a
                            # lighter group (heavier groups are notified first).
                            notified_users.append(user)

                            # An user was notified
                            notified = True

            except ObjectDoesNotExist:
                # It means there is not matching template for TARGET_GROUPS
                notified = False

            try:
                create_notification(
                    notification_template=NotificationTemplate.objects.get(notification_class=notification_class[0],
                                                                           target_users='ACTOR',
                                                                           is_activated=True),
                    actor=actor,
                    target_user=actor,
                    group=None,
                    action_medium=action_medium,
                    target_object=target_object)

                # An user was notified
                notified = True

            except ObjectDoesNotExist:
                # It means there is not matching template for ACTOR
                notified = False

            try:
                create_notification(
                    notification_template=NotificationTemplate.objects.get(notification_class=notification_class[0],
                                                                           target_users='RECIPIENT',
                                                                           is_activated=True),
                    actor=actor,
                    target_user=recipient,
                    group=None,
                    action_medium=action_medium,
                    target_object=target_object)

                # An user was notified
                notified = True

            except ObjectDoesNotExist:
                # It means there is not matching template for RECIPIENT
                notified = False

            return notified

    except IntegrityError:
        raise IntegrityError(
            "Le nom de la classe de notifications doit être unique")


def create_notification(notification_template, actor, target_user, group=None, action_medium=False, target_object=False):
    """
    Create a notification in the db. It handles GenericForeignKey fields.
    :param notification_template: the notification template. A notification template object.
    :param actor: the notification actor. A user object.
    :param target_user: the user to who the notification is sent. A user object.
    :param group: If given, it's the group to which the notification is sent. Used to determine the group category.
    Optional.
    :param action_medium: the action medium related to the notification. Optional. May be any object.
    :param target_object: the target_object related to the notification. Optional. May be any object.
    :return:
    """
    # First, we handle GenericForeignKey fields
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

    # Then, the notification is created
    Notification.objects.create(shop_category=notification_template.shop_category,
                                group_category=group,
                                target_category=notification_template.target_users,
                                type=notification_template.type,
                                actor_id=actor.pk,
                                actor_type=ContentType.objects.get(
                                    app_label='users', model='user'),
                                notification_class=notification_template.notification_class,
                                target_user=target_user,
                                action_medium_id=action_medium_id,
                                action_medium_type=action_medium_type,
                                target_id=target_object_id,
                                target_type=target_object_type,
                                )


def xml_parser(node, parsed_xml=""):
    """
    Analyze a xml node and replace allowed tags by html tags. Any other text will be escaped.
    :param node: a xml node from a xml tree generated by lxml.
    :param parsed_xml: For a recursive use, when there is a string yet parsed to insert between tags.
    :return : html_result, a html string
    :rtype : str
    """

    # If parsed_xml is empty, we get the tag text and tail (see lxml documentation for more information)
    if not parsed_xml:
        # text is the text between the right and left tag
        if node.text is None:
            text = ""
        else:
            text = conditional_escape(node.text)
        # tail is the text after the tag , e.g. "<bold>Hello</bold> Michel" (" Michel" is the tail)
        if node.tail is None:
            tail = ""
        else:
            tail = conditional_escape(node.tail)
    else:
        text = parsed_xml
        tail = ""

    # Tag recognition and substitution
    try:
        # Allowed tag are saved in a dictionary outside of the function for external use
        tag_dictionary = get_allowed_tags()
        html_result = tag_dictionary[node.tag][0] + \
            text + tag_dictionary[node.tag][1] + tail
    except KeyError:
        # If the tag does not exist in the dictionary, a xml string is generated from the node
        html_result = conditional_escape(etree.tostring(node))

    return html_result


def recursive_parser(tree):
    """
    A recursive function which analyze and parse a xml tree
    :param tree: a xml tree generated by lxml (it's an object)
    :return: a html string
    :rtype: str
    """
    parsed_xml = ""

    # tree.iter() build an iterator which lists the tree nodes (deepest first)
    for node in tree.iter():
        parsed_xml += xml_parser(node)

    return xml_parser(tree, parsed_xml)


def template_xml_tree_builder(xml_body):
    """
    Generate a xml tree related to a xml_body, thanks to lxml
    :param xml_body: a string with xml tags
    :return: the xml tree
    """
    # Frame the body string with a header and a footer tag for potential later processing
    xml_header = "<bcode>"
    xml_footer = "</bcode>"
    xml_template = xml_header + xml_body + xml_footer

    return etree.fromstring(xml_template, parser=etree.XMLParser(recover=True))


def template_rendering_engine(template):
    """
    Generate the html related to a xml template.
    :param template: str. Represents a xml template.
    :return: an html string, escaped except for allowed tags.
    :rtype : str
    """
    xml_tree = template_xml_tree_builder(template)

    return recursive_parser(xml_tree)


def get_allowed_tags():
    """
    A get function to give access to tag_dictionary.
    :return: tag_dictionary which saves allowed tags.
    :rtype : dict
    """
    tag_dictionary = {'bold': ('<strong>', '</strong>'),
                      'actor': ('<span class="notification-actor" data-link="{% url "url_user_retrieve" pk=actor.pk %}">'
                                '{{actor}}</span>', ''),
                      'target_object': ('{{target_object}}', ''),
                      'transfer.amount': ('{{target_object.amount}}', ''),
                      'transfer.justification': ('{{target_object.justification}}', ''),
                      '#text': ('', ''),
                      'bcode': ('<span class="bcode">', '</span>')}

    return tag_dictionary
