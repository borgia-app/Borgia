from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from modules.models import SelfSaleModule
from shops.models import Shop

INTERNALS_GROUP_NAME = 'members'
EXTERNALS_GROUP_NAME = 'externals'


def get_permission_name_group_managing(group):
    return 'users.manage_' + group.name + '_group'


def shop_from_group(group):
    if 'chiefs' in group.name or 'associates' in group.name:
        return Shop.objects.get(name=group.name.split('-')[1])
    else:
        raise ValueError('Only for shop group')


def group_name_display(group):
    """
    Return a group name which can be read be a human.

    Return the name in french, human readable. The group name must be in:
    [treasurers, presidents, vice_presidents, chiefs-<group_name>,
    associates-<group_name>]

    :param group: group, mandatory
    :type group: Group object
    :raises: ValueError if unrecognized group name
    :returns: readable group name
    :rtype: string
    """
    if group.name == 'treasurers':
        return 'Trésoriers'
    elif group.name == 'presidents':
        return 'Présidents'
    elif group.name == 'vice_presidents':
        return 'Vice-présidents'
    elif 'chiefs-' in group.name:
        return 'Chefs ' + group.name.split('-')[1]
    elif 'associates-' in group.name:
        return 'Associés ' + group.name.split('-')[1]
    elif group.name == 'externals':
        return 'Externes'
    elif group.name == INTERNALS_GROUP_NAME:
        return 'Gadz\'Arts'
    else:
        raise ValueError('Unrecognized group name')


def human_permission_name(name):
    """
    Translate the permission name in french.

    :note:: Be careful of the order in the catalog !

    :params name: permission name
    :type name: string
    :returns: translated name
    """
    translation_catalog = [
        ('Add', 'Ajouter'),
        ('add', 'Ajouter'),
        ('Change', 'Modifier'),
        ('change', 'Modifier'),
        ('Delete', 'Supprimer'),
        ('delete', 'Supprimer'),
        ('List', 'Lister'),
        ('list', 'Lister'),
        ('Manage', 'Gérer'),
        ('manage', 'Gérer'),
        ('Retrieve', 'Afficher'),
        ('retrieve', 'Afficher'),

        ('group', 'groupe'),
        ('cash', 'payement en espèces'),
        ('cheque', 'chèque'),
        ('debitbalance', 'payement par compte'),
        ('lydia', 'payement lydia'),
        ('payment', 'payement'),
        ('exceptionnal movement', 'mouvement exceptionnel'),
        ('operatorsalemodule', 'module de vente par opérateur'),
        ('selfsalemodule', 'module de vente en libre service'),
        ('sale', 'vente'),
        ('transfert', 'transfert'),
        ('recharging', 'rechargement'),
        ('event', 'évènement'),
        ('category', 'categorie de produits'),
        ('setting', 'paramètre global'),
        ('shop', 'magasin'),
        ('product', 'produits'),
        ('user', 'utilisateur'),

        ('Use', 'Utiliser'),
        ('use', 'Utiliser'),

        ('treasurers', 'trésoriers'),
        ('vice_presidents', 'vice-présidents'),
        ('presidents', 'présidents'),
        ('chiefs-', 'chefs '),
        ('associates-', 'associés '),
        ('externals', 'externes'),
        (INTERNALS_GROUP_NAME, 'Gadz\'Arts'),

        ('Supply money', 'Ajouter de l\'argent'),

        ('more', 'plus')
    ]

    for e in translation_catalog:
        name = name.replace(e[0], e[1])

    return name


def human_unused_permissions():
    unused_models = [
        'group',
        'permission',
        'contenttype',
        'session',
        'dependency'
    ]

    perms = []
    for string_model in unused_models:
        try:
            contenttype = ContentType.objects.filter(
                model=string_model).first()
        except ObjectDoesNotExist:
            pass
        if contenttype is not None:
            perms_model = Permission.objects.filter(
                content_type=contenttype.pk)
            for perm in perms_model:
                perms.append(perm.pk)

    return perms


def model_from_module_url_name(module_url_name):
    if module_url_name == 'self_sale':
        return SelfSaleModule
    else:
        raise ValueError('module_url_name does not match any defined module')


def module_url_name_from_model(model):
    if isinstance(model, SelfSaleModule):
        return 'self_sale'
    else:
        raise ValueError('model does not match any defined module')

#####################
### GROUP RELATED ###
#####################


def get_members_group(externals=False):
    """
    Get group for members, beeing internals or externals

    Return internal members by default.
    """
    if externals:
        group_name = EXTERNALS_GROUP_NAME
    else:
        group_name = INTERNALS_GROUP_NAME

    return Group.objects.get(name=group_name)


def get_managers_group_from_user(user):
    if user.groups.count() == 1:
        return None
    else:
        presidents_query = user.groups.filter(name='presidents')
        if presidents_query.count() == 1:
            return presidents_query.first()
        else:
            vice_presidents_query = user.groups.filter(name='vice_presidents')
            if vice_presidents_query.count() == 1:
                return vice_presidents_query.first()
            else:
                treasurer_query = user.groups.filter(name='treasurer')
                if treasurer_query.count() == 1:
                    return treasurer_query.first()


def is_association_manager(user):
    if get_managers_group_from_user(user) is not None:
        return True
    else:
        return False
