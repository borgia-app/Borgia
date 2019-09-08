from django.contrib.auth.models import Group
from django.urls import reverse

from borgia.utils import (get_permission_name_group_managing,
                          group_name_display, simple_lateral_link)
from shops.models import Shop

DEFAULT_PERMISSIONS_CHIEFS = ['add_user', 'view_user',
                              'change_shop', 'view_shop',
                              'add_product', 'change_product', 'delete_product', 'view_product',
                              'change_price_product',
                              'view_sale', 'use_operatorsalemodule',
                              'change_config_operatorsalemodule', 'view_config_operatorsalemodule',
                              'change_config_selfsalemodule', 'view_config_selfsalemodule',
                              'add_stockentry', 'view_stockentry',
                              'add_inventory', 'view_inventory']
DEFAULT_PERMISSIONS_ASSOCIATES = ['add_user', 'view_user',
                                  'view_shop',
                                  'add_product', 'change_product', 'view_product',
                                  'view_sale', 'use_operatorsalemodule',
                                  'view_config_operatorsalemodule', 'view_config_selfsalemodule',
                                  'add_stockentry', 'view_stockentry',
                                  'add_inventory', 'view_inventory']


def is_shop_manager(shop, user):
    """
    Return True if the user is a chief or associate.
    """
    if user in shop.get_managers():
        return True
    else:
        return False


def get_shops_managed(user):
    """
    Return the list of shop managed by the user.
    """
    shop_list = []
    for shop in Shop.objects.all():
        if is_shop_manager(shop, user):
            shop_list.append(shop)

    return shop_list


def get_shops_tree(user, is_association_manager):
    shop_tree = []
    if is_association_manager:
        shop_managed = Shop.objects.all()
    else:
        shop_managed = get_shops_managed(user)
        if not shop_managed:
            return []

    for shop in shop_managed:
        shop_tree.append(
            simple_lateral_link(
                'Management ' + shop.name.capitalize(),
                'briefcase',
                'lm_workboard',
                reverse('url_shop_workboard',
                        kwargs={'shop_pk': shop.pk})
            )
        )
    return shop_tree


def shops_lateral_menu(nav_tree, user, shop):
    """
    Lateral Menu for shops managers.

    Add :
    - Home page shops
    - Checkup
    - OperatorSale module
    - Sales
    - Products
    - StockEntries
    - Inventories
    - OperatorSale Configuration
    - SelfSale Configuration
    - Shop groups management
    """
    nav_tree.append(
        simple_lateral_link(
            'Accueil Magasin ' + shop.name.title(),
            'briefcase',
            'lm_workboard',
            reverse('url_shop_workboard',
                    kwargs={'shop_pk': shop.pk})
        ))

    if user.has_perm('shops.view_shop'):
        nav_tree.append(
            simple_lateral_link(
                'Checkup',
                'user',
                'lm_shop_checkup',
                reverse('url_shop_checkup',
                        kwargs={'shop_pk': shop.pk})
            ))

    # OperatorSale Module
    if shop.modules_operatorsalemodule_shop.first() is not None:
        if shop.modules_operatorsalemodule_shop.first().state is True:
            if user.has_perm('modules.use_operatorsalemodule'):
                nav_tree.append(simple_lateral_link(
                    label='Module vente',
                    fa_icon='shopping-basket',
                    id_link='lm_operatorsale_interface_module',
                    url=reverse(
                        'url_shop_module_sale',
                        kwargs={'shop_pk': shop.pk, 'module_class': 'operator_sales'})
                ))

    # Sales
    if user.has_perm('finances.view_sale'):
        nav_tree.append(
            simple_lateral_link(
                'Ventes',
                'shopping-cart',
                'lm_sale_list',
                reverse(
                    'url_sale_list',
                    kwargs={'shop_pk': shop.pk})
            )
        )

    # Products
    if user.has_perm('shops.view_product'):
        nav_tree.append(
            simple_lateral_link(
                label='Produits',
                fa_icon='cube',
                id_link='lm_product_list',
                url=reverse(
                    'url_product_list',
                    kwargs={'shop_pk': shop.pk})
            )
        )

    # StockEntries
    if user.has_perm('stocks.view_stockentry'):
        nav_tree.append(
            simple_lateral_link(
                'Entrées de stock',
                'list',
                'lm_stockentry_list',
                reverse(
                    'url_stockentry_list',
                    kwargs={'shop_pk': shop.pk})
            )
        )

    # Inventories
    if user.has_perm('stocks.view_inventory'):
        nav_tree.append(
            simple_lateral_link(
                'Inventaires',
                'list',
                'lm_inventory_list',
                reverse(
                    'url_inventory_list',
                    kwargs={'shop_pk': shop.pk})
            )
        )

    if user.has_perm('modules.view_config_selfsalemodule'):
        nav_tree.append(
            simple_lateral_link(
                label='Configuration vente libre service',
                fa_icon='shopping-basket',
                id_link='lm_selfsale_module',
                url=reverse('url_shop_module_config',
                            kwargs={'shop_pk': shop.pk,
                                    'module_class': 'self_sales'}
                            )
            ))

    if user.has_perm('modules.view_config_operatorsalemodule'):
        nav_tree.append(
            simple_lateral_link(
                label='Configuration vente par opérateur',
                fa_icon='coffee',
                id_link='lm_operatorsale_module',
                url=reverse('url_shop_module_config',
                            kwargs={'shop_pk': shop.pk,
                                    'module_class': 'operator_sales'}
                            )
            ))

    # Groups management
    subs = []
    groups = [Group.objects.get(name='chiefs-'+shop.name),
              Group.objects.get(name='associates-'+shop.name)]
    for group in groups:
        if user.has_perm(get_permission_name_group_managing(group)):
            subs.append(
                simple_lateral_link(
                    'Gestion ' + group_name_display(group),
                    'users',
                    'lm_group_manage_' + group.name,
                    reverse('url_group_update', kwargs={
                        'group_pk': group.pk})
                ))
    if len(subs) > 1:
        nav_tree.append({
            'label': 'Gestion groupes magasin',
            'icon': 'users',
            'id': 'lm_group_management',
            'subs': subs
        })
    elif len(subs) == 1:
        nav_tree.append(subs[0])

    return nav_tree
