from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.views.generic.base import ContextMixin

from events.models import Event
from modules.models import OperatorSaleModule, SelfSaleModule
from shops.models import Product, Shop
from users.models import User

INTERNALS_GROUP_NAME = 'members'
EXTERNALS_GROUP_NAME = 'externals'


def simple_lateral_link(label, fa_icon, id_link, url):
    return {
        'label': label,
        'icon': fa_icon,
        'id': id_link,
        'url': url
    }


def lateral_menu(user, group, active=None):
    """
    Build the object tree used to generate the lateral menu in the template
    lateral_menu.html.

    This function checks several permissions of the group treasurer and add
    links in the tree if allowed.
    """
    # TODO: try for reverse urls

    models_checked = [
        (User, 'Utilisateurs', 'user'),
        (Shop, 'Magasins', 'shopping-basket'),
        (Event, 'Evènements', 'calendar'),
    ]

    nav_tree = []

    # Groups of the user
    if lateral_menu_user_groups(user) is not None:
        nav_tree.append(
            lateral_menu_user_groups(user)
        )

    # Workboard
    nav_tree.append(
        simple_lateral_link(
            'Accueil ' + group_name_display(group),
            'briefcase',
            'lm_workboard',
            reverse('url_managers_workboard', kwargs={'group_name': group.name})))

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
                        'group_name': group.name,
                        'pk': group.pk})
                ))
    if len(nav_management_groups['subs']) > 1:
        nav_tree.append(nav_management_groups)
    elif len(nav_management_groups['subs']) == 1:
        nav_tree.append(nav_management_groups['subs'][0])

    # Functions

    # Manage products
    try:
        if Permission.objects.get(codename='view_product') in group.permissions.all():
            nav_tree.append(
                simple_lateral_link(
                    label='Produits',
                    fa_icon='cube',
                    id_link='lm_product_list',
                    url=reverse(
                        'url_product_list',
                        kwargs={'group_name': group.name})
                )
            )
    except ObjectDoesNotExist:
        pass

    # Manage stocks
    if lateral_menu_stock(group) is not None:
        nav_tree.append(
            lateral_menu_stock(group)
        )

    # List sales
    nav_sale_lists = {
        'label': 'Finances',
        'icon': 'database',
        'id': 'lm_sale_lists',
        'subs': []
    }

    try:
        if (Permission.objects.get(codename='view_sale')
                in group.permissions.all()):
            nav_sale_lists['subs'].append(simple_lateral_link(
                label='Ventes',
                fa_icon='shopping-cart',
                id_link='lm_sale_list',
                url=reverse(
                    'url_sale_list',
                    kwargs={'shop_pk': 0}
                )
            ))
    except ObjectDoesNotExist:
        pass

    # module of shop
    try:
        # TODO: check perm
        shop = shop_from_group(group)
        if shop is not None:
            nav_tree.append(simple_lateral_link(
                label='Module vente libre service',
                fa_icon='shopping-basket',
                id_link='lm_selfsale_module',
                url=reverse('url_shop_module_config',
                            kwargs={'shop_pk': shop.pk, 'module_class': 'self_sales'}
                            )
            ))
        # TODO: check perm
            nav_tree.append(simple_lateral_link(
                label='Module vente par opérateur',
                fa_icon='coffee',
                id_link='lm_operatorsale_module',
                url=reverse('url_shop_module_config',
                            kwargs={'shop_pk': shop.pk, 'module_class': 'self_sales'}
                            )
            ))
    except ValueError:
        pass

    # Shop sale for Gadz'Arts
    if group.name == INTERNALS_GROUP_NAME:
        for shop in Shop.objects.all():
            if lateral_menu_shop_sale(group, shop) is not None:
                nav_tree.append(lateral_menu_shop_sale(group, shop))

    # Shop sale for shop
    try:
        shop = shop_from_group(group)
        module_sale, created = OperatorSaleModule.objects.get_or_create(
            shop=shop)
        if module_sale.state is True:
            nav_tree.append(simple_lateral_link(
                label='Module vente',
                fa_icon='shopping-basket',
                id_link='lm_operatorsale_interface_module',
                url=reverse(
                    'url_shop_module_sale',
                    kwargs={'shop_pk': shop.pk, 'module_class': 'operator_sales'})
            ))
    except ValueError:
        pass

    # Shop checkup
    try:
        shop = shop_from_group(group)
        nav_tree.append(simple_lateral_link(
            label='Bilan de santé',
            fa_icon='hospital-o',
            id_link='lm_shop_checkup',
            url=reverse(
                'url_shop_checkup',
                kwargs={'pk': shop.pk})
        ))

    except ValueError:
        pass

    if active is not None:
        for link in nav_tree:
            try:
                if len(link['subs']) == 0:
                    if link['id'] == active:
                        link['active'] = True
                else:
                    for sub in link['subs']:
                        if sub['id'] == active:
                            sub['active'] = True
                            break
            except KeyError:
                if link['id'] == active:
                    link['active'] = True
                    break

    return nav_tree

def lateral_menu_stock(group):
    """
    """
    product_tree = {
        'label': 'Stocks',
        'icon': 'stack-overflow',
        'id': 'lm_stock',
        'subs': []
    }

    add_permission_stockentry = Permission.objects.get(
        codename='add_stockentry')
    list_permission_stockentry = Permission.objects.get(
        codename='view_stockentry')
    add_permission_inventory = Permission.objects.get(
        codename='add_inventory')
    list_permission_inventory = Permission.objects.get(
        codename='view_inventory')

    if add_permission_stockentry in group.permissions.all():
        product_tree['subs'].append({
            'label': 'Nouvelle entrée de stock',
            'icon': 'plus',
            'id': 'lm_stockentry_create',
            'url': reverse(
                'url_stockentry_create',
                kwargs={'shop_pk': 0})
        })

    if list_permission_stockentry in group.permissions.all():
        product_tree['subs'].append({
            'label': 'Liste des entrées de stock',
            'icon': 'list',
            'id': 'lm_stockentry_list',
            'url': reverse(
                'url_stockentry_list',
                kwargs={'shop_pk': 0})
        })

    if add_permission_inventory in group.permissions.all():
        product_tree['subs'].append({
            'label': 'Nouvel inventaire',
            'icon': 'plus',
            'id': 'lm_inventory_create',
            'url': reverse(
                'url_inventory_create',
                kwargs={'shop_pk': 0})
        })

    if list_permission_inventory in group.permissions.all():
        product_tree['subs'].append({
            'label': 'Liste des inventaires',
            'icon': 'list',
            'id': 'lm_inventory_list',
            'url': reverse(
                'url_inventory_list',
                kwargs={'shop_pk': 0})
        })

    if len(product_tree['subs']) > 0:
        return product_tree
    else:
        return None


def lateral_menu_user_groups(user):
    """
    """
    # TODO
    # if len(user.groups.all()) > 1:
    #     user_groups_tree = {
    #         'label': 'Groupes',
    #         'icon': 'institution',
    #         'id': 'lm_user_groups',
    #         'class': 'info',
    #         'subs': []
    #     }
    #     for group in user.groups.all():
    #         user_groups_tree['subs'].append({
    #             'label': group_name_display(group),
    #             'icon': 'institution',
    #             'id': 'lm_user_groups_' + group.name,
    #             'url': reverse(
    #                 'url_group_workboard',
    #                 kwargs={'group_name': group.name})
    #         })
    #     return user_groups_tree
    # else:
    return None


def lateral_menu_shop_sale(group, shop):
    """
    """
    shop_tree = {
        'label': shop.name.title(),
        'icon': 'cube',
        'id': 'lm_shop_' + shop.name,
        'subs': []
    }

    try:
        if (Permission.objects.get(codename='use_selfsalemodule')
                in group.permissions.all()):
            module_sale = SelfSaleModule.objects.get(shop=shop)
            if module_sale.state is True:
                shop_tree['subs'].append(simple_lateral_link(
                    label='Vente libre service',
                    fa_icon='shopping-basket',
                    id_link='lm_selfsale_module_'+shop.name,
                    url=reverse(
                        'url_shop_module_sale',
                        kwargs={'shop_pk': shop.pk, 'module_class': 'operator_sales'})
                ))
    except ObjectDoesNotExist:
        pass

    if len(shop_tree['subs']) > 0:
        return shop_tree
    else:
        return None


class GroupLateralMenuMixin(ContextMixin):
    lm_active = None

    def __init__(self):
        self.request = None
        self.kwargs = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['nav_tree'] = lateral_menu(
                self.request.user,
                Group.objects.get(name=self.kwargs['group_name']),
                self.lm_active)
            context['group_name'] = self.kwargs['group_name']
            context['group_name_display'] = group_name_display(
                Group.objects.get(name=self.kwargs['group_name'])
            )
        except KeyError:
            pass
        except ObjectDoesNotExist:
            pass
        return context


def permission_to_manage_group(group):
    """
    DEPRECATED.
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
