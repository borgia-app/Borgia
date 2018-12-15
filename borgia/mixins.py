from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.views.generic.base import ContextMixin

from borgia.utils import INTERNALS_GROUP_NAME, simple_lateral_link
from modules.models import OperatorSaleModule, SelfSaleModule


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
                'Accueil ' + INTERNALS_GROUP_NAME,
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
