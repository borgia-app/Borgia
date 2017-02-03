from django.contrib.auth.models import Group, Permission
from users.models import User
from shops.models import ProductBase, Shop
from django.views.generic.base import ContextMixin
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from django.urls import NoReverseMatch
from modules.models import *


def lateral_menu(user, group, active=None):
    """
    Build the object tree used to generate the lateral menu in the template
    lateral_menu.html.

    This function checks several permissions of the group treasurer and add
    links in the tree if allowed.
    """
    # TODO: try for reverse urls

    models_checked = [
        User, Shop
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
            reverse('url_group_workboard', kwargs={'group_name': group.name})))

    # Models
    for model in models_checked:
        if lateral_menu_model(model, group) is not None:
            nav_tree.append(lateral_menu_model(model, group))

    # Groups management
    for g in Group.objects.all():
        if permission_to_manage_group(g)[0] in group.permissions.all():
            nav_tree.append(simple_lateral_link(
                'Gestion ' + group_name_display(g),
                'users',
                'lm_group_manage_' + g.name,
                reverse('url_group_update', kwargs={
                    'group_name': group.name,
                    'pk': g.pk})
            ))

    # Functions
    # Link token to user
    try:
        if (Permission.objects.get(codename='link_token_user')
                in group.permissions.all()):
            nav_tree.append(simple_lateral_link(
                'Liaison jeton',
                'tag',
                'lm_link_token',
                reverse('url_user_link_token',
                        kwargs={'group_name': group.name})))
    except ObjectDoesNotExist:
        pass

    # Manage products
    if lateral_menu_product(group) is not None:
        nav_tree.append(
            lateral_menu_product(group)
            )

    # List sales
    try:
        if (Permission.objects.get(codename='list_sale')
                in group.permissions.all()):
            nav_tree.append(simple_lateral_link(
                label='Ventes',
                faIcon='shopping-cart',
                id='lm_sale_list',
                url=reverse(
                    'url_sale_list',
                    kwargs={'group_name': group.name}
                )
            ))
    except ObjectDoesNotExist:
        pass

    # List rechargings
    try:
        if (Permission.objects.get(codename='list_recharging')
                in group.permissions.all()):
            nav_tree.append(simple_lateral_link(
                label='Rechargements',
                faIcon='money',
                id='lm_recharging_list',
                url=reverse(
                    'url_recharging_list',
                    kwargs={'group_name': group.name}
                )
            ))
    except ObjectDoesNotExist:
        pass

    # List transferts
    try:
        if (Permission.objects.get(codename='list_transfert')
                in group.permissions.all()):
            nav_tree.append(simple_lateral_link(
                label='Transferts',
                faIcon='exchange',
                id='lm_transfert_list',
                url=reverse(
                    'url_transfert_list',
                    kwargs={'group_name': group.name}
                )
            ))
    except ObjectDoesNotExist:
        pass

    # List exceptionnal movements
    try:
        if (Permission.objects.get(codename='list_exceptionnal_movement')
                in group.permissions.all()):
            nav_tree.append(simple_lateral_link(
                label='Exceptionnels',
                faIcon='exclamation-triangle',
                id='lm_exceptionnalmovement_list',
                url=reverse(
                    'url_exceptionnalmovement_list',
                    kwargs={'group_name': group.name}
                )
            ))
    except ObjectDoesNotExist:
        pass

    # module of shop
    try:
        shop = shop_from_group(group)
        # TODO: check perm
        nav_tree.append(simple_lateral_link(
            label='Module vente libre service',
            faIcon='shopping-basket',
            id='lm_selfsale_module',
            url=reverse(
                'url_module_selfsale_workboard',
                kwargs={'group_name': group.name}
            )
        ))
        # TODO: check perm
        nav_tree.append(simple_lateral_link(
            label='Module vente par opérateur',
            faIcon='coffee',
            id='lm_operatorsale_module',
            url=reverse(
                'url_module_operatorsale_workboard',
                kwargs={'group_name': group.name}
            )
        ))
    except ValueError:
        pass

    # Shop sale for Gadz'Arts
    if group.name == 'gadzarts':
        for shop in Shop.objects.all():
            if lateral_menu_shop_sale(group, shop) is not None:
                nav_tree.append(lateral_menu_shop_sale(group, shop))

    # Shop sale for shop
    try:
        shop = shop_from_group(group)
        module, created = OperatorSaleModule.objects.get_or_create(shop=shop)
        if module.state is True:
            nav_tree.append(simple_lateral_link(
                label='Module vente',
                faIcon='shopping-basket',
                id='lm_operatorsale_module',
                url=reverse(
                    'url_module_operatorsale',
                    kwargs={'group_name': group.name,
                            'shop_name': shop.name})
            ))
    except ValueError:
        pass

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


def lateral_menu_model(model, group, faIcon='database'):
    """
    Build the object tree related to a model used to generate the lateral menu
    in the template lateral_menu.html.

    This function checks permissions of the group regarding the model,
    concerning the following actions :
        - list instances of model,
        - create instance of model

    :param model: Model to be used, mandatory.
    :param group: Group whose permissions are checked, mandatory.
    :param id: Id used in the nav tree, mandatory.
    :param faIcon: Font Awesome icon used.
    :type model: Model object
    :type group: Group object
    :type id: string or integer
    :type faIcon: string
    """
    model_tree = {
        'label': model._meta.model_name.capitalize(),
        'icon': faIcon,
        'id': 'lm_' + model._meta.model_name,
        'subs': []
    }

    add_permission = Permission.objects.get(
        codename='add_' + model._meta.model_name)
    list_permission = Permission.objects.get(
        codename='list_' + model._meta.model_name)

    if add_permission in group.permissions.all():
        model_tree['subs'].append({
            'label': 'Nouveau',
            'icon': 'plus',
            'id': 'lm_' + model._meta.model_name + '_create',
            'url': reverse(
                'url_' + model._meta.model_name + '_create',
                kwargs={'group_name': group.name})
        })

    if list_permission in group.permissions.all():
        model_tree['subs'].append({
            'label': 'Liste',
            'icon': 'list',
            'id': 'lm_' + model._meta.model_name + '_list',
            'url': reverse(
                'url_' + model._meta.model_name + '_list',
                kwargs={'group_name': group.name})
        })

    if len(model_tree['subs']) > 0:
        return model_tree
    else:
        return None


def lateral_menu_product(group):
    """
    """
    product_tree = {
        'label': 'Produits',
        'icon': 'cube',
        'id': 'lm_product',
        'subs': []
    }

    add_permission = Permission.objects.get(
        codename='add_product')
    list_permission = Permission.objects.get(
        codename='list_product')

    if add_permission in group.permissions.all():
        product_tree['subs'].append({
            'label': 'Nouveau',
            'icon': 'plus',
            'id': 'lm_product_create',
            'url': reverse(
                'url_product_create',
                kwargs={'group_name': group.name})
        })

    if list_permission in group.permissions.all():
        product_tree['subs'].append({
            'label': 'Liste',
            'icon': 'list',
            'id': 'lm_product_list',
            'url': reverse(
                'url_product_list',
                kwargs={'group_name': group.name})
        })

    if len(product_tree['subs']) > 0:
        return product_tree
    else:
        return None


def lateral_menu_user_groups(user):
    """
    """
    if len(user.groups.all()) > 1:
        user_groups_tree = {
            'label': 'Groupes',
            'icon': 'institution',
            'id': 'lm_user_groups',
            'class': 'info',
            'subs': []
        }
        for group in user.groups.all():
            user_groups_tree['subs'].append({
                'label': group_name_display(group),
                'icon': 'institution',
                'id': 'lm_user_groups_' + group.name,
                'url': reverse(
                    'url_group_workboard',
                    kwargs={'group_name': group.name})
            })
        return user_groups_tree
    else:
        return None


def lateral_menu_shop_sale(group, shop):
    """
    """
    shop_tree = {
        'label': shop.name,
        'icon': 'cube',
        'id': 'lm_shop_' + shop.name,
        'subs': []
    }

    try:
        if (Permission.objects.get(codename='use_selfsalemodule')
                in group.permissions.all()):
            module = SelfSaleModule.objects.get(shop=shop)
            if module.state is True:
                shop_tree['subs'].append(simple_lateral_link(
                    label='Vente libre service',
                    faIcon='shopping-basket',
                    id='lm_selfsale_module_'+shop.name,
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


def simple_lateral_link(label, faIcon, id, url):
    return {
        'label': label,
        'icon': faIcon,
        'id': id,
        'url': url
    }


class GroupLateralMenuFormMixin(ContextMixin):
    lm_active = None

    def get_context_data(self, **kwargs):
        context = super(GroupLateralMenuFormMixin, self).get_context_data(
            **kwargs)
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


class GroupLateralMenuMixin(ContextMixin):
    lm_active = None

    def get_context_data(self, **kwargs):
        context = {}
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


class GroupPermissionMixin(object):
    #perm_codename = None

    def dispatch(self, request, *args, **kwargs):
        """
        Check permissions for the view regarding a group.

        :param self.perm_codename: codename of the permission to be
        checked
        :param self.kwargs['group_name']: name of the group

        :raises: Http404 if group_name not given
        :raises: Http404 if group_name doesn't match a group
        :raises: Http404 if codename doesn't match a permission
        :raises: Http404 if the group doesn't have the permission to access
        the view
        :raises: PermissionDenied if the user is not in the group
        :raises: Http404 if the group doesn't have a workboard to redirect to

        Define the self.success_url based on the group.

        :note:: self.success_url is defined here, even if not used in the
        original view, for instance when there is no form.
        """
        try:
            group = Group.objects.get(name=self.kwargs['group_name'])
            self.group = group
            try:
                if self.perm_codename:
                    permission = Permission.objects.get(
                        codename = self.perm_codename)
                    if permission not in group.permissions.all():
                        raise Http404
                    else:
                        if group not in request.user.groups.all():
                            raise PermissionDenied
                else:
                    if group not in request.user.groups.all():
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


class ProductShopMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.shop = Shop.objects.get(name='shop_name')
        except ObjectDoesNotExist:
            raise Http404
        try:
            self.product = ProductBase.objects.get(name=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        if self.product.shop is not self.shop:
            raise PermissionDenied
        return super(ProductShopMixin, self).dispatch(request, *args, **kwargs)


class ShopMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.shop = Shop.objects.get(name='shop_name')
        except ObjectDoesNotExist:
            raise Http404
        return super(ShopMixin, self).dispatch(request, *args, **kwargs)


class ShopFromGroupMixin(object):
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


class ProductShopFromGroupMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.shop = shop_from_group(self.group)
        except ValueError:
            self.shop = None
        try:
            self.object = ProductBase.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        if self.shop:
            if self.object.shop != self.shop:
                raise PermissionDenied
        return super(ProductShopFromGroupMixin,
                     self).dispatch(request, *args, **kwargs)


class UserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        """
        Add self.user and modify success_url to be the retrieve of the user by
        default.

        Add the user to self and to context. Modify the success_url to be the
        retrieve of the user.

        :param kwargs['user_pk']: pk of the user
        :type kwargs['user_pk']: positiv integer
        :raises: Http404 if no user found
        """
        try:
            self.user = User.objects.get(pk=self.kwargs['user_pk'])
        except ObjectDoesNotExist:
            raise Http404
        self.success_url = reverse('url_user_retrieve', kwargs={
            'group_name': self.kwargs['group_name'],
            'pk': self.user.pk})
        return super(UserMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserMixin, self).get_context_data(**kwargs)
        context['user'] = self.user
        return context


class ShopModuleMixin(object):
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
    perm = Permission.objects.get(codename=('manage_group_'+group.name))
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
    [treasurers, presidents, vice-presidents-internal, chiefs-<group_name>,
    associates-<group_name>]

    :param group: group, mandatory
    :type group: Group object
    :raises: ValueError if unrecognized group name
    :returns: readable group name
    :rtype: string
    """
    if group.name == 'treasurers':
        return 'trésoriers'
    elif group.name == 'presidents':
        return 'présidents'
    elif group.name == 'vice-presidents-internal':
        return 'vice-présidents vie interne'
    elif 'chiefs-' in group.name:
        return 'chefs ' + group.name.split('-')[1]
    elif 'associates-' in group.name:
        return 'associés ' + group.name.split('-')[1]
    elif group.name == 'specials':
        return 'membres spéciaux'
    elif group.name == 'gadzarts':
        return 'Gadz\'Arts'
    elif group.name == 'honnored':
        return 'membres d\'honneur'
    else:
        raise ValueError('Unrecognized group name')


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
