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
