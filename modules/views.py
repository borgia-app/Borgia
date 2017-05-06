from django.utils.timezone import now
from django.shortcuts import render, redirect, Http404, reverse
from functools import partial, wraps

from django.contrib.auth.models import Group
from django.views.generic import FormView, View
from django.forms.formsets import formset_factory
from django.core.exceptions import ObjectDoesNotExist

from modules.forms import (OperatorSaleShopModule, SelfSaleShopModule,
                           ModuleCategoryForm, ModuleContainerCaseForm,
                           ShopModuleConfigForm)
from modules.models import OperatorSaleModule, SelfSaleModule, Category
from borgia.utils import (GroupPermissionMixin, GroupLateralMenuFormMixin,
                          ShopFromGroupMixin, ShopModuleMixin,
                          GroupLateralMenuMixin, shop_from_group,
                          lateral_menu)
from shops.models import (ProductBase, SingleProduct, Container,
                          SingleProductFromContainer, ContainerCase, Shop)
from finances.models import sale_sale
from users.models import User


class SaleShopModuleInterface(GroupPermissionMixin, FormView,
                              GroupLateralMenuFormMixin):
    """
    Generic FormView for handling invoice concerning product bases through a
    shop.

    :param self.template_name: template, mandatory.
    :param self.form_class: form class, mandatory.
    :param self.module_class: module class, mandatory.
    :param self.perm_codename: permission to check
    :type self.template_name: string
    :type self.form_class: Form class object
    :type self.module_class: ShopModule class object
    :type self.perm_codename: string
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            self.shop = Shop.objects.get(name=kwargs['shop_name'])
            self.module = self.module_class.objects.get(shop=self.shop)
        except ObjectDoesNotExist:
            raise Http404
        if self.module.state is False:
            raise Http404
        return super(SaleShopModuleInterface,
                     self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        kwargs = super(SaleShopModuleInterface,
                       self).get_form_kwargs(**kwargs)
        kwargs['module'] = self.module
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SaleShopModuleInterface,
                        self).get_context_data(**kwargs)
        context['shop'] = self.shop
        context['categories'] = self.module.categories.all()
        return context

    def form_valid(self, form):

        products = []

        for field in form.cleaned_data:
            if field != 'client':
                invoice = form.cleaned_data[field]
                if invoice != 0 and isinstance(invoice, int):
                    product_pk = field.split('-')[0]
                    if 'container_cases' in field:
                        element = ContainerCase.objects.get(
                            pk=product_pk).product
                    else:
                        element = ProductBase.objects.get(pk=product_pk)
                    products += self.get_products_with_strategy(
                        element, invoice)

        sale = sale_sale(sender=self.client, operator=self.request.user,
                         date=now(), products_list=products,
                         wording='Vente '+self.shop.name, to_return=True)

        return sale_shop_module_resume(self.request, sale, self.group,
                                       self.shop, self.module, self.success_url)

    def get_products_with_strategy(self, element, invoice):
        """
        Return a list of real products (single products or products from
        container) knowing what the client want and how many
        product he want.

        This method takes the right product in the queryset of products from
        the product base. In order to choose the product used (sold for a
        single product or consume for a container), the method check if the
        product is directly a container (from a ContainerCase), then you
        consumme this container or a productbase and select the right.

        Concerning single products:
            Bought products are the firsts in the queryset.


        Concerning containers:
            Bought products are consumed from the container the first in the
            queryset, but not in a container place.

        Concerning containers from places:
            Bought products are consumed from this container.

        :param element: product the client want,
        mandatory.
        :aram invoice: number of products the client want, mandatory.
        :type element: ProductBase instance or Container instance
        :type invoice: strictly positiv integer
        """
        products = []

        if isinstance(element, Container):
            product = SingleProductFromContainer.objects.create(
                container=element,
                quantity=(element.product_base.product_unit.usual_quantity()
                          * invoice),
                sale_price=(element.product_base.get_moded_usual_price()
                            * invoice)
            )
            products.append(product)

        elif isinstance(element, ProductBase):
            product_base = element

            if (product_base.type == 'single_product'):
                for i in range(0, invoice):
                    try:
                        product = SingleProduct.objects.filter(
                            product_base=product_base,
                            is_sold=False)[i]
                        product.is_sold = True
                        product.sale_price = product_base.get_moded_usual_price()
                        product.save()
                        products.append(product)
                    except IndexError:
                        pass

            if (product_base.type == 'container'):
                try:
                    container = Container.objects.filter(
                        product_base=product_base,
                        is_sold=False).exclude(
                            pk__in=self.module.container_pk_in_container_cases()
                            )[0]

                    product = SingleProductFromContainer.objects.create(
                        container=container,
                        quantity=(product_base.product_unit.usual_quantity()
                                  * invoice),
                        sale_price=(product_base.get_moded_usual_price()
                                    * invoice)
                    )
                    products.append(product)

                    if container.estimated_quantity_remaining()[0] <= 0:
                        container.is_sold = True
                        container.save()
                except IndexError:
                    pass

        else:
            pass

        return products


class SelfSaleShopModuleInterface(SaleShopModuleInterface):
    """
    Sale interface for SelfSaleModule.
    """
    template_name = 'modules/shop_module_selfsale_interface.html'
    form_class = SelfSaleShopModule
    module_class = SelfSaleModule
    perm_codename = 'use_selfsalemodule'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(SelfSaleShopModuleInterface,
                       self).get_form_kwargs(**kwargs)
        kwargs['client'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.client = self.request.user
        self.success_url = reverse(
            'url_module_selfsale',
            kwargs={
                'group_name': self.group.name,
                'shop_name': self.shop.name
            }
        )
        return super(SelfSaleShopModuleInterface, self).form_valid(form)


class OperatorSaleShopModuleInterface(SaleShopModuleInterface):
    """
    Sale interface for SelfOperatorModule.
    """
    template_name = 'modules/shop_module_operatorsale_interface.html'
    form_class = OperatorSaleShopModule
    module_class = OperatorSaleModule
    perm_codename = 'use_operatorsalemodule'
    lm_active = 'lm_operatorsale_interface_module'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(OperatorSaleShopModuleInterface,
                       self).get_form_kwargs(**kwargs)
        kwargs['client'] = None
        return kwargs

    def form_valid(self, form):
        client_pk = int(form.cleaned_data['client'].split('/')[0])
        self.client = User.objects.get(pk=client_pk)
        self.success_url = reverse(
            'url_module_operatorsale',
            kwargs={
                'group_name': self.group.name,
                'shop_name': self.shop.name
            }
        )
        return super(OperatorSaleShopModuleInterface, self).form_valid(form)


def sale_shop_module_resume(request, sale, group, shop, module, success_url):
    template_name = 'modules/shop_module_sale_resume.html'

    # Context construction, based on LateralMenuViewMixin and
    # GroupPermissionMixin in borgia.utils
    context = {
        'group': group,
        'shop': shop,
        'module': module,
        'sale': sale,
        'delay': module.delay_post_purchase,
        'success_url': success_url
    }
    context['nav_tree'] = lateral_menu(
        request.user,
        group,
        None)
    if (request.user.groups.all().exclude(
            pk__in=[1, 5, 6]).count() > 0):
        context['first_job'] = request.user.groups.all().exclude(
            pk__in=[1, 5, 6])[0]
    context['list_selfsalemodule'] = []
    for s in Shop.objects.all().exclude(pk=1):
        try:
            m = SelfSaleModule.objects.get(shop=s)
            if m.state is True:
                context['list_selfsalemodule'].append(s)
        except ObjectDoesNotExist:
            pass

    # Check if you should logout after sale
    if module.logout_post_purchase:
        context['success_url'] = reverse('url_logout')

    return render(request, template_name, context=context)


class SaleShopModuleResume(GroupPermissionMixin, View,GroupLateralMenuMixin):
    sale = None
    delay = None
    success_url = None
    context = None
    template_name = 'modules/shop_module_sale_resume.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.sale = kwargs['sale_pk']
        except KeyError:
            raise Http404
        try:
            self.delay = kwargs['delay']
        except KeyError:
            pass
        try:
            self.success_url = kwargs['success_url']
        except KeyError:
            pass
        return super(SaleShopModuleResume,
                     self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['sale'] = self.sale
        context['delay'] = self.delay
        context['success_url'] = self.success_url
        return render(request, self.template_name, context=context)


class SelfSaleShopModuleWorkboard(GroupPermissionMixin, ShopFromGroupMixin,
                                  ShopModuleMixin, View,
                                  GroupLateralMenuMixin):
    """
    View of the workboard of an SelfSale module of a shop.

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    """
    template_name = 'modules/shop_module_selfsale_workboard.html'
    perm_codename = None
    lm_active = 'lm_selfsale_module'
    module_class = SelfSaleModule

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)


class OperatorSaleShopModuleWorkboard(GroupPermissionMixin, ShopFromGroupMixin,
                                      ShopModuleMixin, View,
                                      GroupLateralMenuMixin):
    """
    View of the workboard of an OperatorSale module of a shop.

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    """
    template_name = 'modules/shop_module_operatorsale_workboard.html'
    perm_codename = None
    lm_active = 'lm_operatorsale_module'
    module_class = OperatorSaleModule

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)


class ShopModuleCategories(GroupPermissionMixin, ShopFromGroupMixin,
                           ShopModuleMixin, View,
                           GroupLateralMenuMixin):
    """
    View to manage categories of a self shop module.

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['module_class']: class of the shop module, mandatory
    :type kwargs['group_name']: string
    :type kwargs['module_class']: class object
    """
    template_name = 'modules/shop_module_categories.html'
    form_class = None
    perm_codename = None
    lm_active = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.group = Group.objects.get(name=kwargs['group_name'])
            self.shop = shop_from_group(self.group)
            if kwargs['module_class'] == SelfSaleModule:
                self.module, created = SelfSaleModule.objects.get_or_create(
                    shop=self.shop)
            elif kwargs['module_class'] == OperatorSaleModule:
                self.module, created = OperatorSaleModule.objects.get_or_create(
                    shop=self.shop)
            if self.module.categories.all().count() == 0:
                extra = 1
            else:
                extra = 0
        except ObjectDoesNotExist:
            raise Http404
        except ValueError:
            raise Http404

        self.form_class = formset_factory(wraps(ModuleCategoryForm)(partial(ModuleCategoryForm, shop=self.shop)), extra=extra)
        return super(ShopModuleCategories,
                     self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        categories_data = [{'name': c.name, 'products': c.product_bases.all(),
                            'pk': c.pk} for c in self.module.categories.all()]
        context['cat_form'] = self.form_class(initial=categories_data)
        context['places_form'] = wraps(ModuleContainerCaseForm)(
            partial(ModuleContainerCaseForm, shop=self.shop))(
            initial={'container_cases': self.module.container_cases.all()})
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        cat_form = self.form_class(request.POST)
        places_form = wraps(ModuleContainerCaseForm)(
            partial(ModuleContainerCaseForm, shop=self.shop))(request.POST)
        if cat_form.is_valid():
            self.cat_form_valid(cat_form)
        if places_form.is_valid():
            self.places_form_valid(places_form)

        return redirect(self.get_success_url())

    def cat_form_valid(self, form):

        list_pk = []
        for category_form in form:
            try:
                list_pk.append(category_form.cleaned_data['pk'])
            except KeyError:
                pass
        for category in self.module.categories.all():
            if category.pk not in list_pk:
                category.delete()

        for category_form in form:
            try:
                if category_form.cleaned_data['pk'] is not None:
                    category = Category.objects.get(pk=category_form.cleaned_data['pk'])
                    category.name = category_form.cleaned_data['name']
                    category.product_bases.clear()
                else:
                    category = Category.objects.create(
                        name=category_form.cleaned_data['name'],
                        module=self.module
                    )
                for product in category_form.cleaned_data['products']:
                    category.product_bases.add(product)
                category.save()
            except KeyError:
                pass

    def places_form_valid(self, form):
        self.module.container_cases.clear()
        print(form.cleaned_data)
        print(form.cleaned_data['container_cases'])
        for container_case in form.cleaned_data['container_cases']:
            self.module.container_cases.add(container_case)
        self.module.save()
        print(self.module.container_cases.all())

    def get_success_url(self):
        if self.kwargs['module_class'] == SelfSaleModule:
            self.success_url = reverse(
                'url_module_selfsale_categories', kwargs={
                'group_name': self.kwargs['group_name']})
        elif self.kwargs['module_class'] == OperatorSaleModule:
            self.success_url = reverse(
                'url_module_operatorsale_categories', kwargs={
                'group_name': self.kwargs['group_name']})
        return self.success_url


class ShopModuleConfig(GroupPermissionMixin, ShopFromGroupMixin,
                       ShopModuleMixin, FormView,
                       GroupLateralMenuFormMixin):
    """
    View to manage config of a self shop module.

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['module_class']: class of the shop module, mandatory
    :type kwargs['group_name']: string
    :type kwargs['module_class']: class object
    """
    template_name = 'modules/shop_module_config.html'
    form_class = ShopModuleConfigForm
    perm_codename = None
    lm_active = None

    def get_initial(self):
        initial = super(ShopModuleConfig, self).get_initial()
        initial['state'] = self.module.state
        initial['logout_post_purchase'] = self.module.logout_post_purchase
        initial['limit_purchase'] = self.module.limit_purchase
        if self.module.delay_post_purchase:
            initial['infinite_delay_post_purchase'] = False
        else:
            initial['infinite_delay_post_purchase'] = True
        initial['delay_post_purchase'] = self.module.delay_post_purchase
        return initial

    def form_valid(self, form):
        self.module.state = form.cleaned_data['state']
        self.module.logout_post_purchase = form.cleaned_data['logout_post_purchase']
        self.module.limit_purchase = form.cleaned_data['limit_purchase']
        if form.cleaned_data['infinite_delay_post_purchase'] is True:
            self.module.delay_post_purchase = None
        else:
            self.module.delay_post_purchase = form.cleaned_data['delay_post_purchase']
        self.module.save()
        return super(ShopModuleConfig, self).form_valid(form)
