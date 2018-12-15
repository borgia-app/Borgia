from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.views.generic.base import ContextMixin

from borgia.utils import (INTERNALS_GROUP_NAME,
                          get_permission_name_group_managing,
                          group_name_display, simple_lateral_link, is_association_manager)
from modules.models import SelfSaleModule
from shops.utils import get_shops_tree


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

        is_manager = is_association_manager(self.request.user)

        shop_tree = get_shops_tree(self.request.user, is_manager)

        if is_manager or len(shop_tree) >= 1:
            management_tree = {
                'label': 'Managements',
                'icon': 'institution',
                'id': 'lm_user_groups',
                'class': 'info',
                'subs': []
            }
            management_tree['subs'].append(
                simple_lateral_link(
                    'Actions Membre',
                    'briefcase',
                    'lm_workboard',
                    reverse('url_members_workboard')
                )
            )
            if is_manager:
                management_tree['subs'].append(
                    simple_lateral_link(
                        'Association',
                        'briefcase',
                        'lm_workboard',
                        reverse('url_managers_workboard')
                    )
                )
            for nav_shop in shop_tree:
                management_tree['subs'].append(nav_shop)
            
            nav_tree.append(management_tree)

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


class MembersMixin(PermissionRequiredMixin, LateralMenuMembersMixin):
    """
    Mixin that check permission and add MEMBERS lateral menu.
    """


class ManagerMixin(PermissionRequiredMixin, LateralMenuManagersMixin):
    """
    Mixin that check permission and add MANAGERS lateral menu.
    """
