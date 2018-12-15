from django.contrib.auth.models import Group
from django.urls import reverse
from django.views.generic.base import ContextMixin

from borgia.utils import (INTERNALS_GROUP_NAME,
                          get_permission_name_group_managing,
                          group_name_display, simple_lateral_link)
from modules.models import SelfSaleModule


class LateralMenuBaseMixin(ContextMixin):
    """
    BaseMixin for LateralMenu.
    Don't use it directly, instead override it.
    """
    lm_active = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_tree'] = self.lateral_menu()
        return context
    
    def lateral_menu(self):
        """
        Override it with your custom menu.
        As a base, only add the main sections, depending on the user.
        """
        nav_tree = []

        ## TODO : Add groups of user !
        # if lateral_menu_user_groups(user) is not None:
        #     nav_tree.append(
        #         lateral_menu_user_groups(user)
        #     )
    
        return nav_tree


class LateralMenuMembersMixin(LateralMenuBaseMixin):
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

    def lateral_menu(self):
        nav_tree = super().lateral_menu()
        user = self.request.user

        nav_tree.append(
            simple_lateral_link(
                'Acceuil ' + INTERNALS_GROUP_NAME,
                'briefcase',
                'lm_workboard',
                reverse('url_members_workboard')))


        for selfsale_module in SelfSaleModule.objects.all():
            if selfsale_module.state is True:
                if user.has_perm('modules.use_selfsalemodule'):
                    shop = selfsale_module.shop
                    url = reverse('url_shop_module_sale',
                                  kwargs={'shop_pk': shop.pk, 'module_class': 'self_sales'}
                          )
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
                    'lm_self_transfert_create',
                    reverse('url_self_transfert_create')))

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

        if self.lm_active is not None:
            for link in nav_tree:
                try:
                    for sub in link['subs']:
                        if sub['id'] == self.lm_active:
                            sub['active'] = True
                            break
                except KeyError:
                    if link['id'] == self.lm_active:
                        link['active'] = True
                        break
        return nav_tree


class LateralMenuManagersMixin(LateralMenuBaseMixin):
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

    def lateral_menu(self):
        nav_tree = super().lateral_menu()
        user = self.request.user

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
                label='Exceptionnal Movements',
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
                            'pk': group.pk})
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

        if self.lm_active is not None:
            for link in nav_tree:
                try:
                    for sub in link['subs']:
                        if sub['id'] == self.lm_active:
                            sub['active'] = True
                            break
                except KeyError:
                    if link['id'] == self.lm_active:
                        link['active'] = True
                        break
        return nav_tree


class LateralMenuShopsMixin(LateralMenuBaseMixin):
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

    def lateral_menu(self):
        nav_tree = super().lateral_menu()
        user = self.request.user
        shop = self.shop

        nav_tree.append(
            simple_lateral_link(
                'Accueil Magasin ' + shop.name.title(),
                'briefcase',
                'lm_workboard',
                reverse('url_group_workboard')))

        if user.has_perm('shops.view_shop'):
            nav_tree.append(
                simple_lateral_link(
                    'Checkup',
                    'user',
                    'lm_shop_checkup',
                    reverse('url_shop_checkup'))
            )

        # OperatorSale Module
        if shop.modules_operatorsalemodule_shop.first().state is True:
            if user.has_perm('modules.use_operatorsalemodule'):
                nav_tree.append(simple_lateral_link(
                    label='Module vente',
                    fa_icon='shopping-basket',
                    id_link='lm_operatorsale_interface_module',
                    url=reverse(
                        'url_shop_module_sale',
                        kwargs={'shop_pk': shop.pk, 'module_class': 'operator_sales'})
                    )
                )

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
        if user.has_perm('stocks.view_stockentry'):
            nav_tree.append(
                simple_lateral_link(
                    'Entrées de stock',
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
                                kwargs={'shop_pk': shop.pk, 'module_class': 'self_sales'}
                                )
                ))

        if user.has_perm('modules.view_config_operatorsalemodule'):
            nav_tree.append(
                simple_lateral_link(
                    label='Configuration vente par opérateur',
                    fa_icon='coffee',
                    id_link='lm_operatorsale_module',
                    url=reverse('url_shop_module_config',
                                kwargs={'shop_pk': shop.pk, 'module_class': 'operator_sales'}
                                )
                ))

        # Groups management
        nav_management_groups = {
            'label': 'Gestion groupes magasin',
            'icon': 'users',
            'id': 'lm_group_management',
            'subs': []
        }
        groups = [Group.objects.get(name='chiefs-'+shop.name), Group.objects.get(name='associates-'+shop.name)]
        for group in groups:
            if user.has_perm(get_permission_name_group_managing(group)):
                nav_management_groups['subs'].append(
                        simple_lateral_link(
                        'Gestion ' + group_name_display(group),
                        'users',
                        'lm_group_manage_' + group.name,
                        reverse('url_group_update', kwargs={
                            'pk': group.pk})
                    ))

        nav_tree.append(nav_management_groups)



        if self.lm_active is not None:
            for link in nav_tree:
                try:
                    for sub in link['subs']:
                        if sub['id'] == self.lm_active:
                            sub['active'] = True
                            break
                except KeyError:
                    if link['id'] == self.lm_active:
                        link['active'] = True
                        break
        return nav_tree
