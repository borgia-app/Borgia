from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.views.generic.base import ContextMixin

from borgia.utils import (ACCEPTED_MENU_TYPES, is_association_manager,
                          managers_lateral_menu, members_lateral_menu,
                          simple_lateral_link)
from shops.utils import get_shops_tree, shops_lateral_menu


class LateralMenuMixin(ContextMixin):
    """
    LateralMenu Mixin.
    """
    lm_active = None
    menu_type = None

    def get_menu_type(self):
        """
        Override this method to override the menu_type attribute.
        menu_type should be in accepted_types
        """
        if self.menu_type is None:
            raise ImproperlyConfigured(
                '{0} is missing the menu_type attribute. Define {0}.menu_type with either '
                'members, managers or shops.'.format(self.__class__.__name__)
            )
        else:
            return self.menu_type

    def verify_menu_type(self, menu_type):
        if menu_type not in ACCEPTED_MENU_TYPES:
            raise ImproperlyConfigured(
                '{0}.menu_type is not in accepted types. Define {0}.menu_type with either '
                'members, managers or shops.'.format(self.__class__.__name__)
            )

    def get_specific_menu(self, nav_tree):
        """
        Get specific menu
        """
        menu_type = self.get_menu_type()
        self.verify_menu_type(menu_type)

        if menu_type == 'members':
            return members_lateral_menu(nav_tree, self.request.user)
        elif menu_type == 'managers':
            return managers_lateral_menu(nav_tree, self.request.user)
        elif menu_type == 'shops':
            if self.shop is None:
                raise ImproperlyConfigured(
                    '{0}.menu_type shops should only be used when self.shop is defined. '
                    'Define {0}.menu_type with either members or managers, '
                    'or define self.shop.'.format(self.__class__.__name__)
                )
            else:
                return shops_lateral_menu(nav_tree, self.request.user, self.shop)


    def get_menu(self):
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
            # if is_manager:
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

        nav_tree = self.get_specific_menu(nav_tree)

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_tree'] = self.get_menu()
        return context
