from django.utils.timezone import now
from django.shortcuts import render, HttpResponse, force_text, redirect, Http404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from functools import partial, wraps

from django.contrib.auth.models import Permission, Group
from django.views.generic import FormView, View
from django.forms.formsets import formset_factory

from modules.forms import *
from modules.models import *
from borgia.utils import *
from shops.models import ProductBase, SingleProduct, Container, SingleProductFromContainer
from finances.models import Sale, sale_sale


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
        context['categories'] = self.module.categories.all()
        return context

    def form_valid(self, form):

        products = []

        for field in form.cleaned_data:
            if field != 'client':
                invoice = form.cleaned_data[field]
                product_base_pk = field.split('-')[0]
                product_base = ProductBase.objects.get(pk=product_base_pk)

                if invoice != 0:
                    products += self.get_products_with_strategy(
                        product_base, invoice)

        s = sale_sale(sender=self.client, operator=self.request.user,
                      date=now(), products_list=products,
                      wording='Vente '+self.shop.name, to_return=True)

        return redirect(self.success_url)

    def get_products_with_strategy(self, product_base, invoice):
        """
        Return a list of real products (single products or products from
        container) knowing what the client want (product base) and how many
        product he want.

        This method takes the right product in the queryset of products from
        the product base. In order to choose the product used (sold for a
        single product or consume for a container), the method check if the
        product base is important regarding the stock or not through the
        attribute major_stocked.

        :note:: If you buy single product major_stocked, you buy one by one.

        Concerning single products:
            if not major_stocked:
                Bought products are the firsts in the queryset.
            if major_stocked:
                Bought product is the one in the queryset with the right
                indication attribute.

        Concerning containers:
            if not major_stocked:
                Bought products are consumed from the container with the
                attribute buffer.
            if major_stocked:
                Bought products are consumed from the container with the right
                indication attribute.

        :param product_base: product base the client want,
        mandatory.
        :aram invoice: number of products the client want, mandatory.
        :type product_base: ProductBase instance
        :type invoice: strictly positiv integer
        """
        # TODO: indication and major_stocked in model
        products = []

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
                    is_sold=False)[0]

                product = SingleProductFromContainer.objects.create(
                    container=container,
                    quantity=product_base.product_unit.usual_quantity() * invoice,
                    sale_price=product_base.get_moded_usual_price() * invoice
                )
                products.append(product)
            except IndexError:
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

    def form_valid(self, form):
        self.client = self.request.user
        return super(SelfSaleShopModuleInterface, self).form_valid(form)


class OperatorSaleShopModuleInterface(SaleShopModuleInterface):
    """
    Sale interface for SelfOperatorModule.
    """
    template_name = 'modules/shop_module_operatorsale_interface.html'
    form_class = OperatorSaleShopModule
    module_class = OperatorSaleModule
    perm_codename = 'use_operatorsalemodule'

    def form_valid(self, form):
        client_pk = int(form.cleaned_data['client'].split('/')[0])
        self.client = User.objects.get(pk=client_pk)
        return super(OperatorSaleShopModuleInterface, self).form_valid(form)


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
                                  ShopModuleMixin, FormView,
                                  GroupLateralMenuFormMixin):
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

    def get_initial(self):
        categories_data = [{'name': c.name, 'products': c.product_bases.all(), 'pk': c.pk}
            for c in self.module.categories.all()]
        return categories_data

    def form_valid(self, form):

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

        return super(ShopModuleCategories, self).form_valid(form)

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
        return initial

    def form_valid(self, form):
        self.module.state = form.cleaned_data['state']
        self.module.save()
        return super(ShopModuleConfig, self).form_valid(form)
