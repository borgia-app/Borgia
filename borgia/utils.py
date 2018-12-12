from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from django.urls import NoReverseMatch, reverse
from django.views.generic.base import ContextMixin

from events.models import Event
from modules.models import OperatorSaleModule, SelfSaleModule
from notifications.models import (Notification, NotificationGroup,
                                  NotificationTemplate)
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
        (User, 'Utilisateurs', 'user', 'noSubs', 'List'),
        (Shop, 'Magasins', 'shopping-basket', 'noSubs', 'List'),
        (Notification, 'Notifications', 'bell', 'noSubs', 'List'),
        (NotificationTemplate, 'Templates notification', 'list-alt', 'noSubs', 'List'),
        (Event, 'Evènements', 'calendar', 'noSubs', 'List'),
        (NotificationGroup, 'Groupes', '', 'List', 'Add'),
    ]

    nav_tree = []

    # If Gadzart, simplify the menu
    # if group.name == INTERNALS_GROUP_NAME:
    return lateral_menu_members(user, active)

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

    # Models
    for model in models_checked:
        if lateral_menu_model(model, group) is not None:
            nav_tree.append(lateral_menu_model(model, group))

    # Groups management
    nav_management_groups = {
        'label': 'Gestion des groupes',
        'icon': 'users',
        'id': 'lm_group_management',
        'subs': []
    }
    for g in Group.objects.all():
        if permission_to_manage_group(g)[0] in group.permissions.all():
            nav_management_groups['subs'].append(simple_lateral_link(
                'Gestion ' + group_name_display(g),
                'users',
                'lm_group_manage_' + g.name,
                reverse('url_group_update', kwargs={
                    'group_name': group.name,
                    'pk': g.pk})
            ))
    if len(nav_management_groups['subs']) > 1:
        nav_tree.append(nav_management_groups)
    elif len(nav_management_groups['subs']) == 1:
        nav_tree.append(nav_management_groups['subs'][0])
    else:
        pass

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
        'label': 'Ventes',
        'icon': 'shopping-cart',
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
                    kwargs={'group_name': group.name}
                )
            ))
    except ObjectDoesNotExist:
        pass

    # List rechargings
    try:
        if (Permission.objects.get(codename='view_recharging')
                in group.permissions.all()):
            nav_sale_lists['subs'].append(simple_lateral_link(
                label='Rechargements',
                fa_icon='money',
                id_link='lm_recharging_list',
                url=reverse(
                    'url_recharging_list',
                    kwargs={'group_name': group.name}
                )
            ))
    except ObjectDoesNotExist:
        pass

    # List transferts
    try:
        if (Permission.objects.get(codename='view_transfert')
                in group.permissions.all()):
            nav_sale_lists['subs'].append(simple_lateral_link(
                label='Transferts',
                fa_icon='exchange',
                id_link='lm_transfert_list',
                url=reverse(
                    'url_transfert_list',
                    kwargs={'group_name': group.name}
                )
            ))
    except ObjectDoesNotExist:
        pass

    # List exceptionnal movements
    try:
        if (Permission.objects.get(codename='view_exceptionnalmovement')
                in group.permissions.all()):
            nav_sale_lists['subs'].append(simple_lateral_link(
                label='Exceptionnels',
                fa_icon='exclamation-triangle',
                id_link='lm_exceptionnalmovement_list',
                url=reverse(
                    'url_exceptionnalmovement_list',
                    kwargs={'group_name': group.name}
                )
            ))
    except ObjectDoesNotExist:
        pass

    if len(nav_sale_lists['subs']) > 1:
        nav_tree.append(nav_sale_lists)
    elif len(nav_sale_lists['subs']) == 1:
        nav_tree.append(nav_sale_lists['subs'][0])
    else:
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
                url=reverse(
                    'url_module_selfsale_workboard',
                    kwargs={'group_name': group.name}
                )
            ))
        # TODO: check perm
            nav_tree.append(simple_lateral_link(
                label='Module vente par opérateur',
                fa_icon='coffee',
                id_link='lm_operatorsale_module',
                url=reverse(
                    'url_module_operatorsale_workboard',
                    kwargs={'group_name': group.name}
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
                    'url_module_operatorsale',
                    kwargs={'group_name': group.name,
                            'shop_name': shop.name})
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

    # Global config
    try:
        if (Permission.objects.get(codename='change_setting')
                in group.permissions.all()):
            nav_tree.append(simple_lateral_link(
                label='Configuration',
                fa_icon='cogs',
                id_link='lm_global_config',
                url=reverse(
                    'url_list_config',
                    kwargs={'group_name': group.name})
            ))
    except ObjectDoesNotExist:
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


def lateral_menu_members(user, active=None):
    """
    - List of self sale modules
    - Lydia credit
    - Transferts
    - History of transactions
    - Shared events
    """

    nav_tree = []

    list_selfsalemodule = []
    for shop in Shop.objects.all().exclude(pk=1):
        try:
            module_sale = SelfSaleModule.objects.get(shop=shop)
            if module_sale.state is True:
                if user.has_perm('modules.use_selfsalemodule'):
                    list_selfsalemodule.append(shop)
        except ObjectDoesNotExist:
            pass

    # Groups of the user
    if lateral_menu_user_groups(user) is not None:
        nav_tree.append(
            lateral_menu_user_groups(user)
        )

    nav_tree.append(
        simple_lateral_link(
            'Accueil ' + INTERNALS_GROUP_NAME,
            'briefcase',
            'lm_workboard',
            reverse('url_members_workboard')))

    for shop in list_selfsalemodule:
        nav_tree.append(
            simple_lateral_link(
                'Vente directe ' + shop.name.title(),
                'shopping-basket',
                # Not currently used in modules.view
                'lm_selfsale_interface_module_' + shop.name,
                reverse('url_module_selfsale', kwargs={
                        'group_name': 'members', 'shop_name': shop.name})
            ))

    nav_tree.append(
        simple_lateral_link(
            'Rechargement de compte',
            'credit-card',
            'lm_self_lydia_create',
            reverse('url_self_lydia_create', kwargs={'group_name': 'members'})))

    if user.has_perm('finances.add_transfert'):
        nav_tree.append(
            simple_lateral_link(
                'Transfert',
                'exchange',
                'lm_self_transfert_create',
                reverse('url_self_transfert_create', kwargs={'group_name': 'members'})))

    nav_tree.append(
        simple_lateral_link(
            'Historique des transactions',
            'history',
            'lm_self_transaction_list',
            reverse('url_self_transaction_list', kwargs={'group_name': 'members'})))

    if user.has_perm('events.view_event'):
        nav_tree.append(
            simple_lateral_link(
                'Évènements',
                'calendar',
                'lm_event_list',
                reverse('url_event_list')))

    if active is not None:
        for link in nav_tree:
            try:
                for sub in link['subs']:
                    if sub['id'] == active:
                        sub['active'] = True
                        break
            except KeyError:
                if link['id'] == active:
                    link['active'] = True
                    break

    return nav_tree


def lateral_menu_model(model, group):
    """
    Build the object tree related to a model used to generate the lateral menu
    in the template lateral_menu.html.

    This function checks permissions of the group regarding the model,
    concerning the following actions :
        - list instances of model,
        - create instance of model

    :param model: Model to be used, mandatory. id/id_link: Id used in the nav tree, mandatory.
                                               fa_icon: Font Awesome icon used
    :param group: Group whose permissions are checked, mandatory.
    :type model: Model object
    :type group: Group object
    """
    if model[2]:
        fa_icon = model[2]
    else:
        fa_icon = "database"

    if 'noSubs' in model:
        model_tree = {
            'label': model[1],
            'icon': fa_icon,
            'id': 'lm_' + model[0]._meta.model_name,
            'url': '',
            'subs': []
        }
    else:
        model_tree = {
            'label': model[1],
            'icon': fa_icon,
            'id': 'lm_' + model[0]._meta.model_name,
            'subs': []
        }

    if 'Add' in model:
        add_permission = Permission.objects.get(
            codename='add_' + model[0]._meta.model_name)

        if add_permission in group.permissions.all():
            model_tree['subs'].append({
                'label': 'Nouveau',
                'icon': 'plus',
                'id': 'lm_' + model[0]._meta.model_name + '_create',
                'url': reverse(
                    'url_' + model[0]._meta.model_name + '_create',
                    kwargs={'group_name': group.name})
            })

    if 'List' in model:
        list_permission = Permission.objects.get(
            codename='list_' + model[0]._meta.model_name)

        if list_permission in group.permissions.all():
            if 'noSubs' in model:
                model_tree['url'] = reverse('url_' + model[0]._meta.model_name + '_list',
                                            kwargs={'group_name': group.name})
                model_tree['id'] = 'lm_' + model[0]._meta.model_name + '_list'
            else:
                model_tree['subs'].append({
                    'label': 'Liste',
                    'icon': 'list',
                    'id': 'lm_' + model[0]._meta.model_name + '_list',
                    'url': reverse(
                        'url_' + model[0]._meta.model_name + '_list',
                        kwargs={'group_name': group.name})
                })
        else:
            return None

    if len(model_tree['subs']) > 0 or 'noSubs' in model:
        return model_tree
    else:
        return None


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
                'url_stock_entry_create',
                kwargs={'group_name': group.name})
        })

    if list_permission_stockentry in group.permissions.all():
        product_tree['subs'].append({
            'label': 'Liste des entrées de stock',
            'icon': 'list',
            'id': 'lm_stockentry_list',
            'url': reverse(
                'url_stock_entry_list',
                kwargs={'group_name': group.name})
        })

    if add_permission_inventory in group.permissions.all():
        product_tree['subs'].append({
            'label': 'Nouvel inventaire',
            'icon': 'plus',
            'id': 'lm_inventory_create',
            'url': reverse(
                'url_inventory_create',
                kwargs={'group_name': group.name})
        })

    if list_permission_inventory in group.permissions.all():
        product_tree['subs'].append({
            'label': 'Liste des inventaires',
            'icon': 'list',
            'id': 'lm_inventory_list',
            'url': reverse(
                'url_inventory_list',
                kwargs={'group_name': group.name})
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
                        'url_module_selfsale',
                        kwargs={'group_name': group.name,
                                'shop_name': shop.name})
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
        context = super(GroupLateralMenuMixin, self).get_context_data(**kwargs)
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


class LateralMenuMixin(ContextMixin):
    lm_active = None

    def __init__(self):
        self.request = None
        self.kwargs = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_tree'] = lateral_menu_members(
            self.request.user,
            self.lm_active)
        return context


class GroupPermissionMixin(object):
    kwargs = None
    perm_codename = None
    group = None
    success_url = None
    request = None

    def dispatch(self, request, *args, **kwargs):
        """
        Check permissions for the view regarding a group.

        :param request:
        :param kwargs: ['group_name'] name of the group
        :raises: Http404 if group_name not given
        :raises: Http404 if group_name doesn't match a group
        :raises: Http404 if codename doesn't match a permission
        :raises: PermissionDenied if the group doesn't have the permission to access
        the view
        :raises: PermissionDenied if the user is not in the group
        :raises: Http404 if the group doesn't have a workboard to redirect to

        Define the self.success_url based on the group.
        perm_codename: codename of the permission to be
        checked

        :note:: self.success_url is defined here, even if not used in the
        original view, for instance when there is no form.
        """
        try:
            group = Group.objects.get(name=self.kwargs['group_name'])
            self.group = group
            try:
                if group not in request.user.groups.all():
                    raise PermissionDenied
                if self.perm_codename:
                    permission = Permission.objects.get(
                        codename=self.perm_codename)
                    if permission not in group.permissions.all():
                        raise PermissionDenied

            except ObjectDoesNotExist:
                raise Http404
        except KeyError:
            raise Http404
        except ObjectDoesNotExist:
            raise Http404

        try:
            self.success_url = reverse(
                'url_group_workboard',
                kwargs={'group_name': self.kwargs['group_name']})
        except NoReverseMatch:
            raise Http404

        return super(GroupPermissionMixin,
                     self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GroupPermissionMixin, self).get_context_data(**kwargs)
        context['group'] = self.group

        if (self.request.user.groups.all().exclude(
                pk__in=[1, 5, 6]).count() > 0):
            context['first_job'] = self.request.user.groups.all().exclude(
                pk__in=[1, 5, 6])[0]
        context['list_selfsalemodule'] = []

        for shop in Shop.objects.all().exclude(pk=1):
            try:
                module_sale = SelfSaleModule.objects.get(shop=shop)
                if module_sale.state is True:
                    context['list_selfsalemodule'].append(shop)
            except ObjectDoesNotExist:
                pass
        return context


class ProductShopMixin(object):
    def __init__(self):
        self.kwargs = None
        self.shop = None
        self.product = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.shop = Shop.objects.get(name='shop_name')
        except ObjectDoesNotExist:
            raise Http404
        try:
            self.product = Product.objects.get(
                name=self.kwargs['pk'], is_removed=False)
        except ObjectDoesNotExist:
            raise Http404
        if self.product.shop is not self.shop:
            raise PermissionDenied
        return super(ProductShopMixin, self).dispatch(request, *args, **kwargs)


class ShopFromGroupMixin(object):
    """
    :note:: Be carefull, this mixin doesn't raise 404 if no shop. You must
    handle the case of no shop with overriden.
    """

    def __init__(self):
        self.group = None
        self.shop = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.shop = shop_from_group(self.group)
        except ValueError:
            self.shop = None

        return super(ShopFromGroupMixin,
                     self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ShopFromGroupMixin, self).get_context_data(**kwargs)
        context['shop'] = self.shop
        return context


class ShopContextMixin(ContextMixin):
    """
    :note:: Be carefull, this mixin doesn't raise 404 if no shop. You must
    handle the case of no shop with overriden.
    """

    def __init__(self):
        self.shop = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.shop = Shop.objects.get(name='shop_name')
        except ValueError:
            self.shop = None
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        return context


class ProductShopFromGroupMixin(object):
    def __init__(self):
        self.shop = None
        self.object = None
        self.group = None
        self.kwargs = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.shop = shop_from_group(self.group)
        except ValueError:
            pass
        try:
            self.object = Product.objects.get(
                pk=self.kwargs['pk'], is_removed=False)
        except ObjectDoesNotExist:
            raise Http404
        try:
            if self.shop:
                if self.object.shop != self.shop:
                    raise PermissionDenied
        except AttributeError:
            pass
        return super(ProductShopFromGroupMixin,
                     self).dispatch(request, *args, **kwargs)


class UserMixin(object):
    def __init__(self):
        self.kwargs = None
        self.user = None
        self.success_url = None

    def dispatch(self, request, *args, **kwargs):
        """
        Add self.user and modify success_url to be the retrieve of the user by
        default.

        Add the user to self and to context. Modify the success_url to be the
        retrieve of the user.

        :param request:
        :param kwargs: ['user_pk'] pk of the user
        :type kwargs: ['user_pk'] positive integer
        :raises: Http404 if no user found
        """
        try:
            self.user = User.objects.get(pk=self.kwargs['user_pk'])
        except ObjectDoesNotExist:
            raise Http404
        self.success_url = reverse('url_user_retrieve', kwargs={
            'pk': self.user.pk})
        return super(UserMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserMixin, self).get_context_data(**kwargs)
        context['user'] = self.user
        return context


class ShopModuleMixin(object):
    def __init__(self):
        self.kwargs = None
        self.module_class = None
        self.shop = None
        self.module = None
        self.success_url = None

    def dispatch(self, request, *args, **kwargs):
        """
        Add self.module and modify success_url to be the workboard of the shop
        module by default.

        If no module, create one.
        """
        try:
            module_class = self.kwargs['module_class']
        except KeyError:
            module_class = self.module_class
        if module_class == SelfSaleModule:
            self.module, created = SelfSaleModule.objects.get_or_create(
                shop=self.shop)
            self.success_url = reverse(
                'url_module_selfsale_workboard', kwargs={
                    'group_name': self.kwargs['group_name']})
        elif module_class == OperatorSaleModule:
            self.module, created = OperatorSaleModule.objects.get_or_create(
                shop=self.shop)
            self.success_url = reverse(
                'url_module_operatorsale_workboard', kwargs={
                    'group_name': self.kwargs['group_name']})
        return super(ShopModuleMixin,
                     self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ShopModuleMixin, self).get_context_data(**kwargs)
        context['module'] = self.module
        return context


def permission_to_manage_group(group):
    """
    Récupère la permission qui permet de gérer le groupe 'group'
    Utilisable directement dans has_perm
    :param group:
    :return: (objet permission, permission name formatée pour has_perm)
    """
    perm = Permission.objects.get(codename=('manage_'+group.name+'_group'))
    perm_name = 'users.' + perm.codename
    return perm, perm_name


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
        ('notification', 'notification'),
        ('notificationclass', 'classe de notifications'),
        ('notificationgroup', 'groupe de notifications'),
        ('notificationtemplate', 'template de notifications'),
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