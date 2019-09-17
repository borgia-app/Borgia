from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from modules.models import SelfSaleModule
from shops.models import Shop


INTERNALS_GROUP_NAME = 'members'
EXTERNALS_GROUP_NAME = 'externals'
PRESIDENTS_GROUP_NAME = 'presidents'
VICE_PRESIDENTS_GROUP_NAME = 'vice_presidents'
TREASURERS_GROUP_NAME = 'treasurers'
ACCEPTED_MENU_TYPES = ['members', 'managers', 'shops']


def simple_lateral_link(label, fa_icon, id_link, url):
    return {
        'label': label,
        'icon': fa_icon,
        'id': id_link,
        'url': url
    }

def members_lateral_menu(nav_tree, user):
    """
    Lateral Menu for members.

    Add :
    - Home page members
    - List of self sale modules
    - Lydia credit
    - Transferts
    - History of transactions
    - Shared events
    """
    nav_tree.append(
        simple_lateral_link(
            'Accueil ' + INTERNALS_GROUP_NAME,
            'briefcase',
            'lm_workboard',
            reverse('url_members_workboard')))


    for selfsale_module in SelfSaleModule.objects.all():
        if selfsale_module.state is True:
            if user.has_perm('modules.use_selfsalemodule'):
                shop = selfsale_module.shop
                url = reverse('url_shop_module_sale',
                              kwargs={'shop_pk': shop.pk, 'module_class': 'self_sales'})
                nav_tree.append(
                    simple_lateral_link(
                        'Vente directe ' + shop.name.title(),
                        'shopping-basket',
                        # Not currently used in modules.view
                        'lm_selfsale_interface_module_' + shop.name,
                        url
                    )
                )

    nav_tree.append(
        simple_lateral_link(
            'Rechargement de compte',
            'credit-card',
            'lm_self_lydia_create',
            reverse('url_self_lydia_create'))
    )

    if user.has_perm('finances.add_transfert'):
        nav_tree.append(
            simple_lateral_link(
                'Transfert',
                'exchange',
                'lm_transfert_create',
                reverse('url_transfert_create')))

    nav_tree.append(
        simple_lateral_link(
            'Historique des transactions',
            'history',
            'lm_self_transaction_list',
            reverse('url_self_transaction_list')))

    if user.has_perm('events.view_event'):
        nav_tree.append(
            simple_lateral_link(
                'Évènements',
                'calendar',
                'lm_event_list',
                reverse('url_event_list')))

    return nav_tree


def managers_lateral_menu(nav_tree, user):
    """
    Lateral Menu for association managers.

    Add :
    - Home page managers
    - Users
    - Shops
    - Events
    - Transferts
    - Rechargings
    - ExceptionnalMovements
    - Groups Management
    - Configuration
    """
    nav_tree.append(
        simple_lateral_link(
            'Accueil Managers',
            'briefcase',
            'lm_workboard',
            reverse('url_managers_workboard')))

    if user.has_perm('users.view_user'):
        nav_tree.append(
            simple_lateral_link(
                'Utilisateurs',
                'user',
                'lm_user_list',
                reverse('url_user_list'))
        )

    if user.has_perm('shops.view_shop'):
        nav_tree.append(
            simple_lateral_link(
                'Magasins',
                'shopping-basket',
                'lm_shop_list',
                reverse('url_shop_list'))
        )

    if user.has_perm('events.view_event'):
        nav_tree.append(
            simple_lateral_link(
                'Evenements',
                'calendar',
                'lm_event_list',
                reverse('url_event_list'))
        )

    # Rechargings
    if user.has_perm('finances.view_recharging'):
        nav_tree.append(simple_lateral_link(
            label='Rechargements',
            fa_icon='money',
            id_link='lm_recharging_list',
            url=reverse('url_recharging_list')
        ))

    # Transferts
    if user.has_perm('finances.view_transfert'):
        nav_tree.append(simple_lateral_link(
            label='Transferts',
            fa_icon='exchange',
            id_link='lm_transfert_list',
            url=reverse('url_transfert_list')
        ))

    # ExceptionnalMovements
    if user.has_perm('finances.view_exceptionnalmovement'):
        nav_tree.append(simple_lateral_link(
            label='Mouvements exceptionnels',
            fa_icon='exclamation-triangle',
            id_link='lm_exceptionnalmovement_list',
            url=reverse('url_exceptionnalmovement_list')
        ))

    # Groups management
    nav_management_groups = {
        'label': 'Gestion des groupes',
        'icon': 'users',
        'id': 'lm_group_management',
        'subs': []
    }
    for group in Group.objects.all():
        if user.has_perm(get_permission_name_group_managing(group)):
            nav_management_groups['subs'].append(
                simple_lateral_link(
                    'Gestion ' + group_name_display(group),
                    'users',
                    'lm_group_manage_' + group.name,
                    reverse('url_group_update', kwargs={
                        'group_pk': group.pk})
                ))
    if len(nav_management_groups['subs']) > 1:
        nav_tree.append(nav_management_groups)
    elif len(nav_management_groups['subs']) == 1:
        nav_tree.append(nav_management_groups['subs'][0])

    # Global config
    if user.has_perm('configurations.change_configuration'):
        nav_tree.append(simple_lateral_link(
            label='Configuration',
            fa_icon='cogs',
            id_link='lm_index_config',
            url=reverse('url_index_config')
        ))

    return nav_tree


def permission_to_manage_group(group):
    """
    DEPRECATED. Use get_permission_name_group_managing instead
    Get Permission to manage group.
    """
    perm = Permission.objects.get(codename=('manage_'+group.name+'_group'))
    perm_name = 'users.' + perm.codename
    return perm, perm_name


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
    if group.name == TREASURERS_GROUP_NAME:
        return 'Trésoriers'
    elif group.name == PRESIDENTS_GROUP_NAME:
        return 'Présidents'
    elif group.name == VICE_PRESIDENTS_GROUP_NAME:
        return 'Vice-présidents'
    elif 'chiefs-' in group.name:
        return 'Chefs ' + group.name.split('-')[1]
    elif 'associates-' in group.name:
        return 'Associés ' + group.name.split('-')[1]
    elif group.name == EXTERNALS_GROUP_NAME:
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
        (EXTERNALS_GROUP_NAME, 'externes'),
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
            perm_query = Permission.objects.filter(
                content_type=contenttype.pk)
            for perm in perm_query:
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


def get_members_group(is_externals=False):
    """
    Get group for members, beeing internals or externals

    Return internal members group by default.
    """
    if is_externals:
        group_name = EXTERNALS_GROUP_NAME
    else:
        group_name = INTERNALS_GROUP_NAME

    return Group.objects.get(name=group_name)


def get_managers_group_from_user(user):
    if user.groups.count() == 1:
        return None
    else:
        presidents_query = user.groups.filter(name=PRESIDENTS_GROUP_NAME)
        if presidents_query.count() == 1:
            return presidents_query.first()
        else:
            vice_presidents_query = user.groups.filter(name=VICE_PRESIDENTS_GROUP_NAME)
            if vice_presidents_query.count() == 1:
                return vice_presidents_query.first()
            else:
                treasurer_query = user.groups.filter(name=TREASURERS_GROUP_NAME)
                if treasurer_query.count() == 1:
                    return treasurer_query.first()
                else:
                    return None


def is_association_manager(user):
    if get_managers_group_from_user(user) is not None:
        return True
    else:
        return False
