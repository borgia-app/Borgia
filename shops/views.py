from django.core import serializers
from math import ceil

from django.shortcuts import render, force_text, HttpResponseRedirect, redirect
from django.shortcuts import HttpResponse, Http404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView, View
from django.contrib.auth import logout

from borgia.models import FormNextView, CreateNextView, UpdateNextView, ListCompleteView
from shops.models import *
from shops.forms import *
from users.models import User
from finances.models import *
from notifications.models import notify
from contrib.models import add_to_breadcrumbs
from borgia.utils import *


class ProductList(GroupPermissionMixin, ShopFromGroupMixin, View, GroupLateralMenuMixin):
    template_name = 'shops/product_list.html'
    perm_codename = 'list_product'

    def get(self, request, *args, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context['product_list'] = ProductBase.objects.filter(shop=self.shop)
        return render(request, self.template_name, context=context)


class ProductCreate(GroupPermissionMixin, ShopFromGroupMixin, FormView, GroupLateralMenuFormMixin):
    template_name = 'shops/product_create.html'
    perm_codename = 'add_product'
    form_class = ProductCreateForm

    def form_valid(self, form):
        if form.cleaned_data['product_base'].type == 'container':
            if form.cleaned_data['product_base'].product_unit.type in ['meat', 'cheese']:
                product = Container.objects.create(price=(form.cleaned_data['price'] *1000/ form.cleaned_data['quantity'])*form.cleaned_data['product_base'].quantity,
                                                   quantity_remaining=form.cleaned_data['quantity'],
                                                   purchase_date=form.cleaned_data['purchase_date'],
                                                   expiry_date=form.cleaned_data['expiry_date'],
                                                   place=form.cleaned_data['place'],
                                                   product_base=form.cleaned_data['product_base'])
            else:
                for i in range(0, form.cleaned_data['quantity']):
                    product = Container.objects.create(price=form.cleaned_data['price'],
                                                       purchase_date=form.cleaned_data['purchase_date'],
                                                       expiry_date=form.cleaned_data['expiry_date'],
                                                       place=form.cleaned_data['place'],
                                                       product_base=form.cleaned_data['product_base'])
        elif form.cleaned_data['product_base'].type == 'single_product':
            for i in range(0, form.cleaned_data['quantity']):
                product = SingleProduct.objects.create(price=form.cleaned_data['price'],
                                                       purchase_date=form.cleaned_data['purchase_date'],
                                                       expiry_date=form.cleaned_data['expiry_date'],
                                                       place=form.cleaned_data['place'],
                                                       product_base=form.cleaned_data['product_base'])
        return super(ProductCreate, self).form_valid(form)

    def get_initial(self):
        initial = super(ProductCreate, self).get_initial()
        initial['purchase_date'] = now
        return initial

    def get_context_data(self, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)
        context['shop'] = self.shop
        return context

    def get_form_kwargs(self):
        kwargs_form = super(ProductCreate, self).get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form


class ProductDeactivate(GroupPermissionMixin, ProductShopFromGroupMixin, View, GroupLateralMenuMixin):
    """
    Deactivate a product and redirect to the workboard of the group.

    :param kwargs['group_name']: name of the group used.
    :param kwargs['pk']: pk of the product
    :param self.perm_codename: codename of the permission checked.
    """
    template_name = 'shops/product_deactivate.html'
    success_url = None
    perm_codename = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        if self.object.is_active is True:
            self.object.is_active = False
        else:
            self.object.is_active = True
        self.object.save()

        return redirect(force_text(self.success_url))


class ProductRetrieve(GroupPermissionMixin, ProductShopFromGroupMixin, View, GroupLateralMenuMixin):
    """
    Retrieve a Product.

    :param kwargs['group_name']: name of the group used.
    :param kwargs['pk']: pk of the product
    :param self.perm_codename: codename of the permission checked.
    """
    template_name = 'shops/product_retrieve.html'
    perm_codename = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)


# AUBERGE
# Doit devenir module
class PurchaseAuberge(FormView):
    form_class = PurchaseAubergeForm
    template_name = 'shops/sale_auberge.html'
    success_url = '/auth/login'

    def get_form_kwargs(self):
        kwargs = super(PurchaseAuberge, self).get_form_kwargs()
        kwargs['container_meat_list'] = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='meat')
        kwargs['container_cheese_list'] = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='cheese')
        kwargs['container_side_list'] = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='side')
        kwargs['single_product_available_list'] = Shop.objects.get(name='Auberge').list_product_base_single_product(status_sold=False)
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = super(PurchaseAuberge, self).get_initial()
        container_meat_list = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='meat')
        container_cheese_list = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='cheese')
        container_side_list = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='side')
        single_product_available_list = Shop.objects.get(name='Auberge').list_product_base_single_product(status_sold=False)

        for i in range(0, len(single_product_available_list)):
            initial['field_single_product_%s' % i] = 0
        for i in range(0, len(container_meat_list)):
            initial['field_container_meat_%s' % i] = 0
        for i in range(0, len(container_cheese_list)):
            initial['field_container_cheese_%s' % i] = 0
        for i in range(0, len(container_side_list)):
            initial['field_container_side_%s' % i] = 0

        return initial

    def get_context_data(self, **kwargs):
        context = super(PurchaseAuberge, self).get_context_data(**kwargs)
        form = self.get_form()
        dict_field_single_product = []
        dict_field_container_meat = []
        dict_field_container_cheese = []
        dict_field_container_side = []
        container_meat_list = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='meat')
        container_cheese_list = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='cheese')
        container_side_list = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='side')
        single_product_available_list = Shop.objects.get(name='Auberge').list_product_base_single_product(status_sold=False)
        for i in range(0, len(single_product_available_list)):
            dict_field_single_product.append((form['field_single_product_%s' % i],
                                              single_product_available_list[i][0], i))
        for i in range(0, len(container_meat_list)):
            dict_field_container_meat.append((form['field_container_meat_%s' % i],
                                              container_meat_list[i][0], i))
        for i in range(0, len(container_cheese_list)):
            dict_field_container_cheese.append((form['field_container_cheese_%s' % i],
                                                container_cheese_list[i][0], i))
        for i in range(0, len(container_side_list)):
            dict_field_container_side.append((form['field_container_side_%s' % i],
                                              container_side_list[i][0], i))
        context['dict_field_single_product'] = dict_field_single_product
        context['dict_field_container_meat'] = dict_field_container_meat
        context['dict_field_container_cheese'] = dict_field_container_cheese
        context['dict_field_container_side'] = dict_field_container_side
        context['single_product_available_list'] = single_product_available_list
        context['container_meat_list'] = container_meat_list
        context['container_cheese_list'] = container_cheese_list
        context['container_side_list'] = container_side_list
        return context

    def form_valid(self, form):

        container_meat_list = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='meat')
        container_cheese_list = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='cheese')
        container_side_list = Shop.objects.get(name='Auberge').list_product_base_container(status_sold=False, type='side')
        single_product_available_list = Shop.objects.get(name='Auberge').list_product_base_single_product(
            status_sold=False)
        list_results_container_meat = []
        list_results_container_cheese = []
        list_results_container_side = []
        list_results_single_product = []

        for i in range(0, len(single_product_available_list)):
            list_results_single_product.append((form.cleaned_data["field_single_product_%s" % i],
                                                single_product_available_list[i][0]))
        for i in range(0, len(container_meat_list)):
            list_results_container_meat.append((form.cleaned_data["field_container_meat_%s" % i],
                                                container_meat_list[i][0]))
        for i in range(0, len(container_cheese_list)):
            list_results_container_cheese.append((form.cleaned_data["field_container_cheese_%s" % i],
                                                  container_cheese_list[i][0]))
        for i in range(0, len(container_side_list)):
            list_results_container_side.append((form.cleaned_data["field_container_side_%s" % i],
                                                container_side_list[i][0]))

        # Objects vendus
        list_products_sold = []

        # Objects unitaires - ex: Skolls
        for e in list_results_single_product:
            if e[0] != 0:
                # Le client demande e[0] objets identiques au produit de base e[1]
                # On les prends dans l'ordre du queryset (on s'en fiche) des objets non vendus bien sûr
                # Le prix de vente est le prix du base product à l'instant de la vente
                for i in range(0, e[0]):
                    sp = SingleProduct.objects.filter(product_base=e[1], is_sold=False)[i]
                    sp.is_sold = True
                    sp.sale_price = sp.product_base.get_moded_usual_price()
                    sp.save()
                    list_products_sold.append(sp)

        # Food
        list_results_containers = list_results_container_meat + list_results_container_cheese + list_results_container_side
        for e in list_results_containers:
            if e[0] != 0:
                # Premier conteneur de la liste dans le queryset du product base
                list_products_sold.append(SingleProductFromContainer.objects.create(container=Container.objects.filter(product_base=e[1])[0],
                                                                                    quantity=e[0] * e[1].product_unit.usual_quantity(),
                                                                                    sale_price=ceil(e[1].get_moded_usual_price() * e[0]/10) / 100))

        if list_products_sold:
            s = sale_sale(sender=User.objects.get(username=form.cleaned_data['client_username']), operator=self.request.user, date=now(),
                          products_list=list_products_sold, wording='Vente auberge', to_return=True)

            # Deconnection
            # logout(self.request)

            # Affichage de la purchase au client
            return render(self.request, 'shops/sale_validation.html', {'sale': s,
                                                                       'next': '/shops/auberge/consumption/'})
        else:
            # Commande nulle

            # Deconnection
            logout(self.request)
            return redirect('/auberge')

# Obsolète, cf group workboard
def workboard_auberge(request):
    group_gestionnaires_de_l_auberge_pk = 6
    add_to_breadcrumbs(request, 'Workboard auberge')
    return render(request, 'shops/workboard_auberge.html', locals())


# C-Vis
# Doit devenir module
class PurchaseCvis(FormView):
    form_class = PurchaseCvisForm
    template_name = 'shops/sale_cvis.html'
    success_url = '/auth/login'

    def get_form_kwargs(self):
        kwargs = super(PurchaseCvis, self).get_form_kwargs()
        # kwargs['container_consumable_list'] = Shop.objects.get(name='Cvis').list_product_base_container(status_sold=False, type='consumable')
        kwargs['single_product_available_list'] = Shop.objects.get(name='Cvis').list_product_base_single_product(status_sold=False)
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = super(PurchaseCvis, self).get_initial()
        # container_consumable_list = Shop.objects.get(name='Cvis').list_product_base_container(status_sold=False, type='consumable')
        single_product_available_list = Shop.objects.get(name='Cvis').list_product_base_single_product(status_sold=False)

        for i in range(0, len(single_product_available_list)):
            initial['field_single_product_%s' % i] = 0
        # for i in range(0, len(container_consumable_list)):
        #     initial['field_container_consumable_%s' % i] = 0

        return initial

    def get_context_data(self, **kwargs):
        context = super(PurchaseCvis, self).get_context_data(**kwargs)
        form = self.get_form()
        dict_field_single_product = []
        # dict_field_container_consumable = []
        # container_consumable_list = Shop.objects.get(name='Cvis').list_product_base_container(status_sold=False, type='consumable')
        single_product_available_list = Shop.objects.get(name='Cvis').list_product_base_single_product(status_sold=False)
        for i in range(0, len(single_product_available_list)):
            dict_field_single_product.append((form['field_single_product_%s' % i],
                                              single_product_available_list[i][0], i))
        # for i in range(0, len(container_consumable_list)):
        #     dict_field_container_consumable.append((form['field_container_consumable_%s' % i],
        #                                             container_consumable_list[i][0], i))
        context['dict_field_single_product'] = dict_field_single_product
        # context['dict_field_container_consumable'] = dict_field_container_consumable
        context['single_product_available_list'] = single_product_available_list
        # context['container_consumable_list'] = container_consumable_list
        return context

    def form_valid(self, form):

        # container_consumable_list = Shop.objects.get(name='Cvis').list_product_base_container(status_sold=False, type='consumable')
        single_product_available_list = Shop.objects.get(name='Cvis').list_product_base_single_product(
            status_sold=False)
        # list_results_container_consumable = []
        list_results_single_product = []

        for i in range(0, len(single_product_available_list)):
            list_results_single_product.append((form.cleaned_data["field_single_product_%s" % i],
                                                single_product_available_list[i][0]))
        # for i in range(0, len(container_consumable_list)):
        #     list_results_container_consumable.append((form.cleaned_data["field_container_consumable_%s" % i],
        #                                               container_consumable_list[i][0]))

        # Objects vendus
        list_products_sold = []

        # Objects unitaires - ex: Skolls
        for e in list_results_single_product:
            if e[0] != 0:
                # Le client demande e[0] objets identiques au produit de base e[1]
                # On les prends dans l'ordre du queryset (on s'en fiche) des objets non vendus bien sûr
                # Le prix de vente est le prix du base product à l'instant de la vente
                for i in range(0, e[0]):
                    sp = SingleProduct.objects.filter(product_base=e[1], is_sold=False)[i]
                    sp.is_sold = True
                    sp.sale_price = sp.product_base.get_moded_usual_price()
                    sp.save()
                    list_products_sold.append(sp)

        # Food
        # list_results_containers = list_results_container_consumable
        # for e in list_results_containers:
        #     if e[0] != 0:
        #         # Premier conteneur de la liste dans le queryset du product base
        #         list_products_sold.append(SingleProductFromContainer.objects.create(container=Container.objects.filter(product_base=e[1])[0],
        #                                                                             quantity=e[0] * e[1].product_unit.usual_quantity(),
        #                                                                             sale_price=ceil(e[1].get_moded_usual_price() * e[0]/10) / 100))

        if list_products_sold:
            s = sale_sale(sender=User.objects.get(username=form.cleaned_data['client_username']), operator=self.request.user, date=now(),
                          products_list=list_products_sold, wording='Vente cvis', to_return=True)

            # Deconnection
            # logout(self.request)

            # Affichage de la purchase au client
            return render(self.request, 'shops/sale_validation.html', {'sale': s,
                                                                       'next': '/shops/cvis/consumption/'})
        else:
            # Commande nulle

            # Deconnection
            logout(self.request)
            return redirect('/cvis')

# Obsolète, cf group workboard
def workboard_cvis(request):
    group_gestionnaires_de_la_cvis_pk = 12
    add_to_breadcrumbs(request, 'Workboard cvis')
    return render(request, 'shops/workboard_cvis.html', locals())

# Bkars
# Doit devenir module
class PurchaseBkars(FormView):
    form_class = PurchaseBkarsForm
    template_name = 'shops/sale_bkars.html'
    success_url = '/auth/login'

    def get_form_kwargs(self):
        kwargs = super(PurchaseBkars, self).get_form_kwargs()
        kwargs['single_product_available_list'] = Shop.objects.get(name='Bkars').list_product_base_single_product(status_sold=False)
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = super(PurchaseBkars, self).get_initial()
        single_product_available_list = Shop.objects.get(name='Bkars').list_product_base_single_product(status_sold=False)

        for i in range(0, len(single_product_available_list)):
            initial['field_single_product_%s' % i] = 0

        return initial

    def get_context_data(self, **kwargs):
        context = super(PurchaseBkars, self).get_context_data(**kwargs)
        form = self.get_form()
        dict_field_single_product = []
        single_product_available_list = Shop.objects.get(name='Bkars').list_product_base_single_product(status_sold=False)
        for i in range(0, len(single_product_available_list)):
            dict_field_single_product.append((form['field_single_product_%s' % i],
                                              single_product_available_list[i][0], i))

        context['dict_field_single_product'] = dict_field_single_product
        context['single_product_available_list'] = single_product_available_list
        return context

    def form_valid(self, form):

        single_product_available_list = Shop.objects.get(name='Bkars').list_product_base_single_product(status_sold=False)
        list_results_single_product = []

        for i in range(0, len(single_product_available_list)):
            list_results_single_product.append((form.cleaned_data["field_single_product_%s" % i],
                                                single_product_available_list[i][0]))


        # Objects vendus
        list_products_sold = []

        # Objects unitaires - ex: Skolls
        for e in list_results_single_product:
            if e[0] != 0:
                # Le client demande e[0] objets identiques au produit de base e[1]
                # On les prends dans l'ordre du queryset (on s'en fiche) des objets non vendus bien sûr
                # Le prix de vente est le prix du base product à l'instant de la vente
                for i in range(0, e[0]):
                    sp = SingleProduct.objects.filter(product_base=e[1], is_sold=False)[i]
                    sp.is_sold = True
                    sp.sale_price = sp.product_base.get_moded_usual_price()
                    sp.save()
                    list_products_sold.append(sp)


        if list_products_sold:
            s = sale_sale(sender=User.objects.get(username=form.cleaned_data['client_username']), operator=self.request.user, date=now(),
                          products_list=list_products_sold, wording='Vente bkars', to_return=True)

            # Deconnection
            # logout(self.request)

            # Affichage de la purchase au client
            return render(self.request, 'shops/sale_validation.html', {'sale': s,
                                                                       'next': '/shops/bkars/consumption/'})
        else:
            # Commande nulle

            # Deconnection
            logout(self.request)
            return redirect('/bkars')

# Obsolète, cf group workboard
def workboard_bkars(request):
    group_gestionnaires_de_la_bkars_pk = 14
    add_to_breadcrumbs(request, 'Workboard bkars')
    return render(request, 'shops/workboard_bkars.html', locals())

# Debit Zifoys
# Doit devenir module
class DebitZifoys(FormView):
    form_class = DebitZifoysForm
    template_name = 'shops/debit_zifoys.html'
    success_url = '/auth/login'

    def get_form_kwargs(self):
        kwargs = super(DebitZifoys, self).get_form_kwargs()
        kwargs['active_keg_container_list'] = Container.objects.filter(product_base__shop=Shop.objects.get(name='Foyer'),
                                                                       product_base__product_unit__type='keg',
                                                                       place__startswith='tireuse')
        kwargs['single_product_available_list'] = Shop.objects.get(name='Foyer').list_product_base_single_product(status_sold=False)
        kwargs['shooter_available_list'] = Shop.objects.get(name='Foyer').list_product_base_single_product_shooter(status_sold=False)
        kwargs['container_soft_list'] = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='soft')
        kwargs['container_syrup_list'] = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='syrup')
        kwargs['container_liquor_list'] = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False,
                                                                                                     type='liquor')
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(DebitZifoys, self).get_context_data(**kwargs)
        form = self.get_form()
        active_keg_container_list = Container.objects.filter(product_base__shop=Shop.objects.get(name='Foyer'),
                                                             product_base__product_unit__type='keg',
                                                             place__startswith='tireuse')
        single_product_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product(status_sold=False)
        shooter_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product_shooter(status_sold=False)
        container_soft_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='soft')
        container_syrup_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='syrup')
        container_liquor_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False,
                                                                                           type='liquor')
        dict_field_active_keg_container = []
        dict_field_single_product = []
        dict_field_shooter = []
        dict_field_container_soft = []
        dict_field_container_syrup = []
        dict_field_container_liquor = []

        for i in range(0, len(active_keg_container_list)):
            dict_field_active_keg_container.append((form['field_active_keg_container_%s' % i],
                                                    active_keg_container_list[i], i))
        for i in range(0, len(single_product_available_list)):
            dict_field_single_product.append((form['field_single_product_%s' % i],
                                              single_product_available_list[i][0], i))
        for i in range(0, len(shooter_available_list)):
            dict_field_shooter.append((form['field_shooter_%s' % i],
                                              shooter_available_list[i][0], i))
        for i in range(0, len(container_soft_list)):
            dict_field_container_soft.append((form['field_container_soft_%s' % i],
                                              container_soft_list[i][0], i))
        for i in range(0, len(container_syrup_list)):
            dict_field_container_syrup.append((form['field_container_syrup_%s' % i],
                                               container_syrup_list[i][0], i))
        for i in range(0, len(container_liquor_list)):
            dict_field_container_liquor.append((form['field_container_liquor_%s' % i],
                                                container_liquor_list[i][0], i,
                                                form['field_container_entire_liquor_%s' % i]))

        context['dict_field_active_keg_container'] = dict_field_active_keg_container
        context['dict_field_single_product'] = dict_field_single_product
        context['dict_field_shooter'] = dict_field_shooter
        context['dict_field_container_soft'] = dict_field_container_soft
        context['dict_field_container_syrup'] = dict_field_container_syrup
        context['dict_field_container_liquor'] = dict_field_container_liquor

        context['single_product_available_list'] = single_product_available_list
        context['shooter_available_list'] = shooter_available_list
        context['container_soft_list'] = container_soft_list
        context['container_syrup_list'] = container_syrup_list
        context['container_liquor_list'] = container_liquor_list
        context['active_keg_container_list'] = active_keg_container_list

        return context

    def get_initial(self):
        initial = super(DebitZifoys, self).get_initial()
        active_keg_container_list = Container.objects.filter(product_base__shop=Shop.objects.get(name='Foyer'),
                                                             product_base__product_unit__type='keg',
                                                             place__startswith='tireuse')
        single_product_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product(status_sold=False)
        shooter_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product_shooter(
            status_sold=False)
        container_soft_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='soft')
        container_syrup_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='syrup')
        container_liquor_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False,
                                                                                           type='liquor')

        for i in range(0, len(single_product_available_list)):
            initial['field_single_product_%s' % i] = 0
        for i in range(0, len(shooter_available_list)):
            initial['field_shooter_%s' % i] = 0
        for i in range(0, len(container_soft_list)):
            initial['field_container_soft_%s' % i] = 0
        for i in range(0, len(container_syrup_list)):
            initial['field_container_syrup_%s' % i] = 0
        for i in range(0, len(container_liquor_list)):
            initial['field_container_liquor_%s' % i] = 0
        for i in range(0, len(container_liquor_list)):
            initial['field_container_entire_liquor_%s' % i] = 0
        for i in range(0, len(active_keg_container_list)):
            initial['field_active_keg_container_%s' % i] = 0
        return initial

    def form_valid(self, form):

        active_keg_container_list = Container.objects.filter(product_base__shop=Shop.objects.get(name='Foyer'),
                                                             product_base__product_unit__type='keg',
                                                             place__startswith='tireuse')
        single_product_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product(status_sold=False)
        shooter_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product_shooter(status_sold=False)
        container_soft_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='soft')
        container_syrup_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='syrup')
        container_liquor_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False,
                                                                                           type='liquor')
        list_results_active_keg_container = []
        list_results_single_product = []
        list_results_shooter = []
        list_results_container_soft = []
        list_results_container_syrup = []
        list_results_container_liquor = []
        list_results_container_entire_liquor = []

        for i in range(0, len(active_keg_container_list)):
            list_results_active_keg_container.append((form.cleaned_data["field_active_keg_container_%s" % i],
                                                      active_keg_container_list[i]))
        for i in range(0, len(single_product_available_list)):
            list_results_single_product.append((form.cleaned_data["field_single_product_%s" % i],
                                                single_product_available_list[i][0]))
        for i in range(0, len(shooter_available_list)):
            list_results_shooter.append((form.cleaned_data["field_shooter_%s" % i],
                                                shooter_available_list[i][0]))
        for i in range(0, len(container_soft_list)):
            list_results_container_soft.append((form.cleaned_data["field_container_soft_%s" % i],
                                                container_soft_list[i][0]))
        for i in range(0, len(container_liquor_list)):
            list_results_container_liquor.append((form.cleaned_data["field_container_liquor_%s" % i],
                                                  container_liquor_list[i][0]))
        for i in range(0, len(container_liquor_list)):
            list_results_container_entire_liquor.append((form.cleaned_data["field_container_entire_liquor_%s" % i],
                                                         container_liquor_list[i][0]))
        for i in range(0, len(container_syrup_list)):
            list_results_container_syrup.append((form.cleaned_data["field_container_syrup_%s" % i],
                                                 container_syrup_list[i][0]))

        # Objects vendus
        list_products_sold = []

        # Objects unitaires - ex: Skolls
        for e in list_results_single_product:
            if e[0] != 0:
                # Le client demande e[0] objets identiques au produit de base e[1]
                # On les prends dans l'ordre du queryset (on s'en fiche) des objets non vendus bien sûr
                # Le prix de vente est le prix du base product à l'instant de la vente
                for i in range(0, e[0]):
                    try:
                        sp = SingleProduct.objects.filter(product_base=e[1], is_sold=False)[i]
                        sp.is_sold = True
                        sp.sale_price = sp.product_base.get_moded_usual_price()
                        sp.save()
                        list_products_sold.append(sp)
                    except IndexError:
                        pass

        for e in list_results_shooter:
            if e[0] != 0:
                for i in range(0, e[0]):
                    try:
                        sht = SingleProduct.objects.filter(product_base=e[1], is_sold=False,
                                                        product_base__description__contains="shooter")[i]
                        sht.is_sold = True
                        sht.sale_price = sht.product_base.get_moded_usual_price()
                        sht.save()
                        list_products_sold.append(sht)
                    except IndexError:
                        pass

        # Issus d'un container
        # Fûts de bières, ce sont ceux qui sont sous les tireuses
        for e in list_results_active_keg_container:
            if e[0] != 0:  # Le client a pris un objet issu du container e[1]
                # Création d'un objet fictif qui correspond à un bout du conteneur
                # Le prix de vente est le prix du base product à l'instant de la vente
                list_products_sold.append(SingleProductFromContainer.objects.create(
                    container=e[1],
                    quantity=e[1].product_base.product_unit.usual_quantity() * e[0],
                    sale_price=e[1].product_base.get_moded_usual_price() * e[0]
                ))

        # Soft, syrup et liquor
        # Le traitement est le même pour tous, je n'utilise qu'une seule liste
        list_results_container_no_keg = \
            list_results_container_soft + list_results_container_syrup + list_results_container_liquor
        for e in list_results_container_no_keg:
            if e[0] != 0:
                # Premier conteneur de la liste dans le queryset du product base
                # Order_by par pk pour être sur que le query renvoie toujours le même order (ce qui n'est pas certain
                # sinon)
                list_products_sold.append(SingleProductFromContainer(container=Container.objects.filter(product_base=e[1]).order_by('pk')[0],
                                                                     quantity=e[0] * e[1].product_unit.usual_quantity(),
                                                                     sale_price=e[1].get_moded_usual_price() * e[0]))

        for e in list_results_container_entire_liquor:
            if e[0] != 0:
                # Deuxième conteneur de la liste dans le queryset du product base
                # Le premier est celui utilisé pour les verres cf au dessus
                # Sinon (cas possible si on en a pris 2), on passe
                # Order_by par pk pour être sur que le query renvoie toujours le même order (ce qui n'est pas certain
                # sinon)
                for i in range(0, e[0]):
                    try:
                        container = Container.objects.filter(product_base=e[1], is_sold=False).order_by('pk')[1]
                        list_products_sold.append(SingleProductFromContainer(container=container,
                                                                             quantity=e[1].quantity,
                                                                             sale_price=e[1].get_moded_price()))
                        container.is_sold = True
                        container.save()
                    except IndexError:
                        try:
                            container = Container.objects.filter(product_base=e[1], is_sold=False).order_by('pk')[0]
                            list_products_sold.append(SingleProductFromContainer(container=container,
                                                                                 quantity=e[1].quantity,
                                                                                 sale_price=e[1].get_moded_price()))
                            container.is_sold = True
                            container.save()
                        except IndexError:
                            pass

        if list_products_sold:
            s = sale_sale(sender=User.objects.get(username=form.cleaned_data['client_username']), operator=self.request.user, date=now(),
                          products_list=list_products_sold, wording='Vente foyer', to_return=True)

            # Deconnection
            # logout(self.request)

            # Affichage de la purchase au client
            return render(self.request, 'shops/sale_validation.html', {'sale': s,
                                                                       'next': '/shops/foyer/debit/'})
        else:
            # Commande nulle

            # Deconnection
            logout(self.request)
            return redirect('/foyer')


# FOYER
# Doit devenir module
class ReplacementActiveKeyView(FormNextView):
    """
    Vue de remplacement d'un fût sous une tireuse pas un autre.
    Ce fût peut être considéré vide, il est alors is_sold=True et ne sera plus proposé comme conteneur à mettre, si ce
    n'est pas le cas il sera reproposé dans la liste.
    Le nouveau fût est selectionné dans une liste de produit de base de fût, qui affiche le nombre de fûts restants de
    ce type, hors le fût utilisé.
    """
    template_name = 'shops/replacement_active_keg.html'
    form_class = ReplacementActiveKegForm
    success_url = '/auth/login'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Remplacement fût')
        return super(ReplacementActiveKeyView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ReplacementActiveKeyView, self).get_form_kwargs()
        kwargs['list_active_keg'] = Container.objects.filter(place__startswith='tireuse')
        return kwargs

    def form_valid(self, form):
        # Définition des objets de travail

        # L'ancien fut, s'il existe, est envoyé vers le stock
        if self.request.GET.get('pk', None) is not '':
            old_keg = Container.objects.get(pk=self.request.GET.get('pk', None))
            old_keg.place = "stock foyer"
            if form.cleaned_data['is_sold']:
                old_keg.is_sold = True
            old_keg.save()

        # Cas où l'on remet un fût
        if form.cleaned_data['new_keg_product_base'] is not None:
            # Le nouveau est envoyé sous la tireuse
            # Le nouveau fût est pris dans la liste des conteneurs qui viennent du produit de base déterminé, à laquelle
            # on a enlevé l'ancien fût automatiquement (car on filtre avec is_sold = False)
            new_keg = Container.objects.filter(product_base=form.cleaned_data['new_keg_product_base'], is_sold=False)[0]
            new_keg.place = self.request.GET.get('place', None)
            new_keg.save()

        return super(ReplacementActiveKeyView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ReplacementActiveKeyView, self).get_context_data(**kwargs)
        if self.request.GET.get('pk', None) is not '':
            context['old_active_keg'] = Container.objects.get(pk=self.request.GET.get('pk', None))
        else:
            context['old_active_keg'] = 'Pas de fut actuellement'
        return context

# Doit devenir module
class PurchaseFoyer(FormView):
    form_class = PurchaseFoyerForm
    template_name = 'shops/sale_foyer.html'
    success_url = '/auth/login'

    def get_form_kwargs(self):
        kwargs = super(PurchaseFoyer, self).get_form_kwargs()
        kwargs['active_keg_container_list'] = Container.objects.filter(product_base__shop=Shop.objects.get(name='Foyer'),
                                                                       product_base__product_unit__type='keg',
                                                                       place__startswith='tireuse')
        kwargs['single_product_available_list'] = Shop.objects.get(name='Foyer').list_product_base_single_product(status_sold=False)
        kwargs['shooter_available_list'] = Shop.objects.get(name='Foyer').list_product_base_single_product_shooter(status_sold=False)
        kwargs['container_soft_list'] = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='soft')
        kwargs['container_syrup_list'] = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='syrup')
        kwargs['container_liquor_list'] = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False,
                                                                                                     type='liquor')
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Consommation foyer')
        return super(PurchaseFoyer, self).get(request, *args, **kwargs)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(PurchaseFoyer, self).get_context_data(**kwargs)
        form = self.get_form()
        active_keg_container_list = Container.objects.filter(product_base__shop=Shop.objects.get(name='Foyer'),
                                                             product_base__product_unit__type='keg',
                                                             place__startswith='tireuse')
        single_product_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product(status_sold=False)
        shooter_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product_shooter(status_sold=False)
        container_soft_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='soft')
        container_syrup_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='syrup')
        container_liquor_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False,
                                                                                           type='liquor')
        dict_field_active_keg_container = []
        dict_field_single_product = []
        dict_field_shooter = []
        dict_field_container_soft = []
        dict_field_container_syrup = []
        dict_field_container_liquor = []

        for i in range(0, len(active_keg_container_list)):
            dict_field_active_keg_container.append((form['field_active_keg_container_%s' % i],
                                                    active_keg_container_list[i], i))
        for i in range(0, len(single_product_available_list)):
            dict_field_single_product.append((form['field_single_product_%s' % i],
                                              single_product_available_list[i][0], i))
        for i in range(0, len(shooter_available_list)):
            dict_field_shooter.append((form['field_shooter_%s' % i],
                                              shooter_available_list[i][0], i))
        for i in range(0, len(container_soft_list)):
            dict_field_container_soft.append((form['field_container_soft_%s' % i],
                                              container_soft_list[i][0], i))
        for i in range(0, len(container_syrup_list)):
            dict_field_container_syrup.append((form['field_container_syrup_%s' % i],
                                               container_syrup_list[i][0], i))
        for i in range(0, len(container_liquor_list)):
            dict_field_container_liquor.append((form['field_container_liquor_%s' % i],
                                                container_liquor_list[i][0], i,
                                                form['field_container_entire_liquor_%s' % i]))

        context['dict_field_active_keg_container'] = dict_field_active_keg_container
        context['dict_field_single_product'] = dict_field_single_product
        context['dict_field_shooter'] = dict_field_shooter
        context['dict_field_container_soft'] = dict_field_container_soft
        context['dict_field_container_syrup'] = dict_field_container_syrup
        context['dict_field_container_liquor'] = dict_field_container_liquor

        context['single_product_available_list'] = single_product_available_list
        context['shooter_available_list'] = shooter_available_list
        context['container_soft_list'] = container_soft_list
        context['container_syrup_list'] = container_syrup_list
        context['container_liquor_list'] = container_liquor_list
        context['active_keg_container_list'] = active_keg_container_list

        return context

    def get_initial(self):
        initial = super(PurchaseFoyer, self).get_initial()
        active_keg_container_list = Container.objects.filter(product_base__shop=Shop.objects.get(name='Foyer'),
                                                             product_base__product_unit__type='keg',
                                                             place__startswith='tireuse')
        single_product_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product(status_sold=False)
        shooter_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product_shooter(status_sold=False)
        container_soft_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='soft')
        container_syrup_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='syrup')
        container_liquor_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False,
                                                                                           type='liquor')

        for i in range(0, len(single_product_available_list)):
            initial['field_single_product_%s' % i] = 0
        for i in range(0, len(shooter_available_list)):
            initial['field_shooter_%s' % i] = 0
        for i in range(0, len(container_soft_list)):
            initial['field_container_soft_%s' % i] = 0
        for i in range(0, len(container_syrup_list)):
            initial['field_container_syrup_%s' % i] = 0
        for i in range(0, len(container_liquor_list)):
            initial['field_container_liquor_%s' % i] = 0
        for i in range(0, len(container_liquor_list)):
            initial['field_container_entire_liquor_%s' % i] = 0
        for i in range(0, len(active_keg_container_list)):
            initial['field_active_keg_container_%s' % i] = 0
        return initial

    def form_valid(self, form):

        active_keg_container_list = Container.objects.filter(product_base__shop=Shop.objects.get(name='Foyer'),
                                                             product_base__product_unit__type='keg',
                                                             place__startswith='tireuse')
        single_product_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product(status_sold=False)
        shooter_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product_shooter(status_sold=False)
        container_soft_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='soft')
        container_syrup_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='syrup')
        container_liquor_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False,
                                                                                           type='liquor')
        list_results_active_keg_container = []
        list_results_single_product = []
        list_results_shooter = []
        list_results_container_soft = []
        list_results_container_syrup = []
        list_results_container_liquor = []
        list_results_container_entire_liquor = []

        for i in range(0, len(active_keg_container_list)):
            list_results_active_keg_container.append((form.cleaned_data["field_active_keg_container_%s" % i],
                                                      active_keg_container_list[i]))
        for i in range(0, len(single_product_available_list)):
            list_results_single_product.append((form.cleaned_data["field_single_product_%s" % i],
                                                single_product_available_list[i][0]))
        for i in range(0, len(shooter_available_list)):
            list_results_shooter.append((form.cleaned_data["field_shooter_%s" % i],
                                                shooter_available_list[i][0]))
        for i in range(0, len(container_soft_list)):
            list_results_container_soft.append((form.cleaned_data["field_container_soft_%s" % i],
                                                container_soft_list[i][0]))
        for i in range(0, len(container_liquor_list)):
            list_results_container_liquor.append((form.cleaned_data["field_container_liquor_%s" % i],
                                                  container_liquor_list[i][0]))
        for i in range(0, len(container_liquor_list)):
            list_results_container_entire_liquor.append((form.cleaned_data["field_container_entire_liquor_%s" % i],
                                                         container_liquor_list[i][0]))
        for i in range(0, len(container_syrup_list)):
            list_results_container_syrup.append((form.cleaned_data["field_container_syrup_%s" % i],
                                                 container_syrup_list[i][0]))

        # Objects vendus
        list_products_sold = []

        # Objects unitaires - ex: Skolls
        for e in list_results_single_product:
            if e[0] != 0:
                # Le client demande e[0] objets identiques au produit de base e[1]
                # On les prends dans l'ordre du queryset (on s'en fiche) des objets non vendus bien sûr
                # Le prix de vente est le prix du base product à l'instant de la vente
                for i in range(0, e[0]):
                    try:
                        sp = SingleProduct.objects.filter(product_base=e[1], is_sold=False)[i]
                        sp.is_sold = True
                        sp.sale_price = sp.product_base.get_moded_usual_price()
                        sp.save()
                        list_products_sold.append(sp)
                    except IndexError:
                        pass

        for e in list_results_shooter:
            if e[0] != 0:
                for i in range(0, e[0]):
                    try:
                        sht = SingleProduct.objects.filter(product_base=e[1], is_sold=False,
                                                           product_base__description__contains="shooter")[i]
                        sht.is_sold = True
                        sht.sale_price = sht.product_base.get_moded_usual_price()
                        sht.save()
                        list_products_sold.append(sht)
                    except IndexError:
                        pass

        # Issus d'un container
        # Fûts de bières, ce sont ceux qui sont sous les tireuses
        for e in list_results_active_keg_container:
            if e[0] != 0:  # Le client a pris un objet issu du container e[1]
                # Création d'un objet fictif qui correspond à un bout du conteneur
                # Le prix de vente est le prix du base product à l'instant de la vente
                list_products_sold.append(SingleProductFromContainer.objects.create(
                    container=e[1],
                    quantity=e[1].product_base.product_unit.usual_quantity() * e[0],
                    sale_price=e[1].product_base.get_moded_usual_price() * e[0]
                ))

        # Soft, syrup et liquor
        # Le traitement est le même pour tous, je n'utilise qu'une seule liste
        list_results_container_no_keg = \
            list_results_container_soft + list_results_container_syrup + list_results_container_liquor
        for e in list_results_container_no_keg:
            if e[0] != 0:
                # Premier conteneur de la liste dans le queryset du product base
                # Order_by par pk pour être sur que le query renvoie toujours le même order (ce qui n'est pas certain
                # sinon)
                list_products_sold.append(SingleProductFromContainer(container=Container.objects.filter(product_base=e[1]).order_by('pk')[0],
                                                                     quantity=e[0] * e[1].product_unit.usual_quantity(),
                                                                     sale_price=e[1].get_moded_usual_price() * e[0]))

        for e in list_results_container_entire_liquor:
            if e[0] != 0:
                # Deuxième conteneur de la liste dans le queryset du product base
                # Le premier est celui utilisé pour les verres cf au dessus
                # Sinon (cas possible si on en a pris 2), on passe
                # Order_by par pk pour être sur que le query renvoie toujours le même order (ce qui n'est pas certain
                # sinon)
                for i in range(0, e[0]):
                    try:
                        container = Container.objects.filter(product_base=e[1], is_sold=False).order_by('pk')[1]
                        list_products_sold.append(SingleProductFromContainer(container=container,
                                                                             quantity=e[1].quantity,
                                                                             sale_price=e[1].get_moded_price()))
                        container.is_sold = True
                        container.save()
                    except IndexError:
                        try:
                            container = Container.objects.filter(product_base=e[1], is_sold=False).order_by('pk')[0]
                            list_products_sold.append(SingleProductFromContainer(container=container,
                                                                                 quantity=e[1].quantity,
                                                                                 sale_price=e[1].get_moded_price()))
                            container.is_sold = True
                            container.save()
                        except IndexError:
                            pass

        if list_products_sold:
            s = sale_sale(sender=self.request.user, operator=self.request.user, date=now(),
                          products_list=list_products_sold, wording='Vente foyer', to_return=True)

            # Deconnection
            logout(self.request)

            # Affichage de la purchase au client
            return render(self.request, 'shops/sale_validation.html', {'sale': s,
                                                                       'next': '/shops/foyer/consumption'})
        else:
            # Commande nulle

            # Deconnection
            logout(self.request)
            return redirect('/shops/foyer/consumption')

# Obsolète, cf group workboard
def workboard_foyer(request):
    group_gestionnaires_du_foyer_pk = 4
    add_to_breadcrumbs(request, 'Workboard foyer')
    return render(request, 'shops/workboard_foyer.html', locals())


def list_active_keg(request):
    """
    Fonction qui liste les conteneurs qui sont sous une tireuse au foyer.
    Ce sont les conteneurs dont l'attribut place commence par "tireuse", par exemple:
    place="tireuse 3".
    Le paramètre objet Setting permet de définir le nombre de tireuse au foyer actuellement.
    :return liste [("tireuse i", objet conteneur i, i), ("tireuse j", objet conteneur j, j), ...]
    """
    active_keg_container_list = []

    # Nombre de tireuses, par défaut = 5
    try:
        nb_tireuses = Setting.objects.get(name="NUMBER_TAPS").get_value()
    except ObjectDoesNotExist:
        nb_tireuses = 5

    for i in range(1, nb_tireuses+1):
        try:  # essai si un conteneur est à la tireuse i
            active_keg_container_list.append(('tireuse %s' % i, Container.objects.get(place='tireuse %s' % i), i))
        except ObjectDoesNotExist:  # Cas où la tireuse est vide
            active_keg_container_list.append(('tireuse %s' % i, None))

    add_to_breadcrumbs(request, 'Liste fûts en cours')
    return render(request, 'shops/list_active_keg.html', locals())


# A voir
class SingleProductRetrieveView(DetailView):
    model = SingleProduct
    template_name = 'shops/singleproduct_retrieve.html'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Détail produit unitaire')
        return super(SingleProductRetrieveView, self).get(request, *args, **kwargs)

# A voir
class SingleProductListView(ListView):
    model = SingleProduct
    template_name = 'shops/singleproduct_list.html'
    queryset = SingleProduct.objects.all()

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste produits unitaires')
        return super(SingleProductListView, self).get(request, *args, **kwargs)

# A voir
class ContainerRetrieveView(DetailView):
    model = Container
    template_name = 'shops/container_retrieve.html'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Détail conteneur')
        return super(ContainerRetrieveView, self).get(request, *args, **kwargs)

# A voir
class ContainerListView(ListView):
    model = Container
    template_name = 'shops/container_list.html'
    queryset = Container.objects.all()

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste conteneurs')
        return super(ContainerListView, self).get(request, *args, **kwargs)


# A refaire
class ProductUnitCreateView(CreateNextView):
    model = ProductUnit
    fields = ['name', 'description', 'unit', 'type']
    template_name = 'shops/productunit_create.html'
    success_url = '/shops/productunit/'

    def get_success_url(self):
        # Notifications

        notify(self.request,
               "product_unit_creation",
               self.object,
               None)
        return force_text(self.request.POST.get('next', self.success_url))

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Création unité de produit')
        return super(ProductUnitCreateView, self).get(request, *args, **kwargs)

# A voir
class ProductUnitRetrieveView(DetailView):
    model = ProductUnit
    template_name = 'shops/productunit_retrieve.html'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Détail unité de produit')
        return super(ProductUnitRetrieveView, self).get(request, *args, **kwargs)

# A voir
class ProductUnitUpdateView(UpdateView):
    model = ProductUnit
    fields = ['name', 'description', 'unit', 'type']
    template_name = 'shops/productunit_update.html'
    success_url = '/shops/productunit/'

    def get_context_data(self, **kwargs):
        context = super(ProductUnitUpdateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.request.POST.get('next', self.success_url))
        return context

    def get_success_url(self):
        # Notifications
        notify(self.request,
               "product_unit_updating",
               self.object,
               None)
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Modification unité de produit')
        return super(ProductUnitUpdateView, self).get(request, *args, **kwargs)

# A voir
class ProductUnitDeleteView(UpdateView):
    model = ProductUnit
    fields = []
    template_name = 'shops/productunit_delete.html'
    success_url = '/shops/productunit/'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Suppression unité de produit')
        return super(ProductUnitDeleteView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save()
        return super(ProductUnitDeleteView, self).form_valid(form)

# A voir
class ProductUnitListView(ListView):
    model = ProductUnit
    template_name = 'shops/productunit_list.html'
    queryset = ProductUnit.objects.all()

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste unités de produit')
        return super(ProductUnitListView, self).get(request, *args, **kwargs)


# A refaire
class ProductBaseCreateView(FormNextView):
    form_class = ProductBaseCreateForm
    template_name = 'shops/productbase_create.html'
    success_url = '/shops/productbase/'
    object = None

    def get_success_url(self):
        # Notifications
        if self.object.shop.name == 'Foyer':
            notify(self.request,
                   "foyer_product_base_creation",
                   self.object,
                   None)
        elif self.object.shop.name == 'Auberge':
            notify(self.request,
                   "auberge_product_base_creation",
                   self.object,
                   None)
        elif self.object.shop.name == 'Cvis':
            notify(self.request,
                   "cvis_product_base_creation",
                   self.object,
                   None)
        elif self.object.shop.name == 'Bkars':
            notify(self.request,
                   "bkars_product_base_creation",
                   self.object,
                   None)
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))

    def get_initial(self):
        initial = super(ProductBaseCreateView, self).get_initial()
        initial['type'] = 'container'
        return initial

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Création base de produits')
        return super(ProductBaseCreateView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        if form.cleaned_data['type'] == 'container':
            self.object = ProductBase.objects.create(name=form.cleaned_data['name'],
                                                     description=form.cleaned_data['description'],
                                                     shop=form.cleaned_data['shop'],
                                                     brand=form.cleaned_data['brand'],
                                                     type=form.cleaned_data['type'],
                                                     product_unit=form.cleaned_data['product_unit'],
                                                     quantity=form.cleaned_data['quantity'])
        elif form.cleaned_data['type'] == 'single_product':
            self.object = ProductBase.objects.create(name=form.cleaned_data['name'],
                                                     description=form.cleaned_data['description'],
                                                     shop=form.cleaned_data['shop'],
                                                     brand=form.cleaned_data['brand'],
                                                     type=form.cleaned_data['type'])
        return super(ProductBaseCreateView, self).form_valid(form)

# A refaire
class ProductBaseRetrieveView(DetailView):
    model = ProductBase
    template_name = 'shops/productbase_retrieve.html'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Détail base de produits')
        return super(ProductBaseRetrieveView, self).get(request, *args, **kwargs)

# A voir
class ProductBaseUpdateView(UpdateView):
    model = ProductBase
    fields = ['name', 'description', 'brand', 'type', 'quantity', 'product_unit']
    template_name = 'shops/productbase_update.html'
    success_url = '/shops/productbase/'

    def get_context_data(self, **kwargs):
        context = super(ProductBaseUpdateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.request.POST.get('next', self.success_url))
        return context

    def get_success_url(self):
        # Notification
        if self.object.shop.name == 'Foyer':
            notify(self.request,
                   "foyer_product_base_updating",
                   self.object,
                   None)
        elif self.object.shop.name == 'Auberge':
            notify(self.request,
                   "auberge_product_base_updating",
                   self.object,
                   None)
        elif self.object.shop.name == 'Cvis':
            notify(self.request,
                   "cvis_product_base_updating",
                   self.object,
                   None)
        elif self.object.shop.name == 'Bkars':
            notify(self.request,
                   "bkars_product_base_updating",
                   self.object,
                   None)
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Modification base de produits')
        return super(ProductBaseUpdateView, self).get(request, *args, **kwargs)

# A voir
class ProductBaseDeleteView(UpdateView):
    model = ProductBase
    fields = []
    template_name = 'shops/productbase_delete.html'
    success_url = '/shops/productbase/'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Suppression base de produits')
        return super(ProductBaseDeleteView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save()
        return super(ProductBaseDeleteView, self).form_valid(form)

# A refaire
class ProductListView(ListCompleteView):
    form_class = ProductListForm
    template_name = 'shops/product_list.html'
    success_url = '/auth/login'
    attr = {
        'order_by': 'name',
        'shop': 1,
        'type_product': 'product_base'
    }  # Celui par défaut

    def get_form_kwargs(self):
        kwargs = super(ProductListView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        # if self.kwargs['organe'] in ['foyer', 'auberge', 'cvis', 'bkars']:
        #     if self.kwargs['organe'] == 'foyer':
        #         self.attr['shop'] = 1
        #     if self.kwargs['organe'] == 'auberge':
        #         self.attr['shop'] = 2
        #     if self.kwargs['organe'] == 'cvis':
        #         self.attr['shop'] = 3
        #     if self.kwargs['organe'] == 'bkars':
        #         self.attr['shop'] = 4

        if Group.objects.get(pk=5) in request.user.groups.all() or Group.objects.get(pk=6) in request.user.groups.all():
            self.attr['shop'] = 2
        if Group.objects.get(pk=11) in request.user.groups.all() or Group.objects.get(pk=12) in request.user.groups.all():
            self.attr['shop'] = 3
        if Group.objects.get(pk=13) in request.user.groups.all() or Group.objects.get(pk=14) in request.user.groups.all():
            self.attr['shop'] = 4

        return super(ProductListView, self).post(request, *args, **kwargs)
        # else:
        #     raise Http404

    def get(self, request, *args, **kwargs):
        if Group.objects.get(pk=5) in request.user.groups.all() or Group.objects.get(pk=6) in request.user.groups.all():
            self.attr['shop'] = 2
        if Group.objects.get(pk=11) in request.user.groups.all() or Group.objects.get(pk=12) in request.user.groups.all():
            self.attr['shop'] = 3
        if Group.objects.get(pk=13) in request.user.groups.all() or Group.objects.get(pk=14) in request.user.groups.all():
            self.attr['shop'] = 4

        add_to_breadcrumbs(request, 'Liste produits')
        return super(ProductListView, self).get(request, *args, **kwargs)
        # else:
        #     raise Http404

    def get_context_data(self, **kwargs):

        if self.attr['type_product'] == 'product_base':
            # En cas de problème avec order_by
            if self.attr['order_by'] not in [f.name for f in ProductBase._meta.get_fields()] \
                    and self.attr['order_by'] not in ['sell_price', '-sell_price', 'quantity_stock', '-quantity_stock']:
                self.query = \
                    ProductBase.objects.filter(shop=Shop.objects.get(pk=self.attr['shop']), is_active=True).exclude(pk=1)
            else:
                # Cas sell price
                if self.attr['order_by'] in ['sell_price', '-sell_price']:
                    if self.attr['order_by'] == '-sell_price':
                        reverse = True
                    else:
                        reverse = False
                    self.query = sorted(
                        ProductBase.objects.filter(shop=Shop.objects.get(pk=self.attr['shop']), is_active=True).exclude(pk=1),
                        key=lambda pb: pb.get_moded_usual_price(), reverse=reverse)
                # Cas quantité en stock
                elif self.attr['order_by'] in ['quantity_stock', '-quantity_stock']:
                    if self.attr['order_by'] == '-quantity_stock':
                        reverse = True
                    else:
                        reverse = False
                    self.query = sorted(
                        ProductBase.objects.filter(shop=Shop.objects.get(pk=self.attr['shop']), is_active=True).exclude(pk=1),
                        key=lambda pb: pb.quantity_products_stock(), reverse=reverse)
                # Cas normal
                else:
                    self.query = \
                        ProductBase.objects.filter(shop=Shop.objects.get(pk=self.attr['shop']), is_active=True).order_by(
                            self.attr['order_by']).exclude(pk=1)

        elif self.attr['type_product'] == 'product_unit':
            # En cas de problème avec order_by
            if self.attr['order_by'] not in [f.name for f in ProductUnit._meta.get_fields()] \
                    and self.attr['order_by'] not in ['type', '-type']:
                self.query = \
                    ProductUnit.objects.filter(product_unit__shop=Shop.objects.get(pk=self.attr['shop']), is_active=True).exclude(pk=1)

            else:
                # Cas du type
                if self.attr['order_by'] in ['type', '-type']:
                    if self.attr['order_by'] == '-type':
                        reverse = True
                    else:
                        reverse = False
                    self.query = sorted(
                        ProductUnit.objects.filter(product_unit__shop=Shop.objects.get(pk=self.attr['shop']), is_active=True).exclude(pk=1),
                        key=lambda pb: pb.get_type_display(), reverse=reverse)
                # Cas normal
                else:
                    self.query = \
                        ProductUnit.objects.filter(product_unit__shop=Shop.objects.get(pk=self.attr['shop']), is_active=True).order_by(
                            self.attr['order_by']).exclude(pk=1)

        return super(ProductListView, self).get_context_data(**kwargs)

    def form_valid(self, form, **kwargs):
        self.attr['shop'] = form.cleaned_data['shop'].pk
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_initial(self):
        initial = super(ProductListView, self).get_initial()
        initial['shop'] = Shop.objects.get(pk=self.attr['shop'])
        return initial

# A refaire
class ProductCreateMultipleView(FormNextView):
    """
    Vue de création de 1 ou plusieurs produits. Il faut différencier les produits classiques (conteneurs et produits
    unitaires) dont les contenants sont au peu prés fixes dans le temps des autres produits spécifiques.

    Par exemple, dans le cas d'un produit classique :
    la base de produit contient une quantité d'unité, un fût de 5000 cl de Kronembourg
    Cette vue permet de créer 10 fûts de 5000 cl en une fois, via le champ "quantity"

    Mais dans le cas des conteneurs dont la quantité varie à chaque fois car le packaging n'est pas fixe, par exemple un
    jambon qui pèse entre 2 et 3 kg, il faut utiliser une autre méthode.
    Les produits de bases sont calibrés à 1000 g. Ainsi l'ajout d'un produit de cette base demande d'entrée la quantité
    dans le conteneur actuel via le champ "quantity", par exemple 2,45 kg.
    Le prix entré est celui des 2,45kg.
    La vue permet de créer un produit de cette base, en ajustant le prix pour le ramener à 1000 g du coup.
    L'information de quantité initiale du vrai conteneur peut être utile un jour, donc nous la stockons dans le champ
    du model Container quantity_remaining qui était devenu obsolète.
    Cette méthode s'applique aux produits dont l'unité est de type "meat" ou "cheese". A priori ce problème est
    spécifique à l'auberge et ne vaut pas la peine de remettre en question toute la structure de la base de donnée.
    """
    template_name = 'shops/product_create_multiple.html'
    form_class = ProductCreateMultipleForm
    success_url = '/auth/login'

    def form_valid(self, form):

        if form.cleaned_data['product_base'].type == 'container':

            # Cas spécifique des produits alimentaires de l'auberge
            # On crée un container de 1000 g en ajustant le prix, mais on stocke l'info de quantité dans remaining
            # quantity (car le champ est la et est inutile)7
            if form.cleaned_data['product_base'].product_unit.type in ['meat', 'cheese']:
                product = Container.objects.create(price=(form.cleaned_data['price'] *1000/ form.cleaned_data['quantity'])*form.cleaned_data['product_base'].quantity,
                                                   quantity_remaining=form.cleaned_data['quantity'],
                                                   purchase_date=form.cleaned_data['purchase_date'],
                                                   expiry_date=form.cleaned_data['expiry_date'],
                                                   place=form.cleaned_data['place'],
                                                   product_base=form.cleaned_data['product_base'])

                # Notifications
                if product.product_base.shop.name == 'Foyer':
                    notify(self.request,
                           "foyer_container_creation",
                           product,
                           None)

                elif product.product_base.shop.name == 'Auberge':
                    notify(self.request,
                           "auberge_container_creation",
                           product,
                           None)

            else:
                for i in range(0, form.cleaned_data['quantity']):
                    product = Container.objects.create(price=form.cleaned_data['price'],
                                                       purchase_date=form.cleaned_data['purchase_date'],
                                                       expiry_date=form.cleaned_data['expiry_date'],
                                                       place=form.cleaned_data['place'],
                                                       product_base=form.cleaned_data['product_base'])

        elif form.cleaned_data['product_base'].type == 'single_product':
            for i in range(0, form.cleaned_data['quantity']):
                product = SingleProduct.objects.create(price=form.cleaned_data['price'],
                                                       purchase_date=form.cleaned_data['purchase_date'],
                                                       expiry_date=form.cleaned_data['expiry_date'],
                                                       place=form.cleaned_data['place'],
                                                       product_base=form.cleaned_data['product_base'])

        return super(ProductCreateMultipleView, self).form_valid(form)

    def get_initial(self):
        initial = super(ProductCreateMultipleView, self).get_initial()
        initial['purchase_date'] = now
        return initial

    def get_context_data(self, **kwargs):
        context = super(ProductCreateMultipleView, self).get_context_data(**kwargs)
        context['shop'] = self.kwargs['shop']
        return context

    def get_form_kwargs(self):
        kwargs_form = super(ProductCreateMultipleView, self).get_form_kwargs()
        kwargs_form['shop'] = Shop.objects.get(name=self.kwargs['shop'])
        return kwargs_form

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Création produits')
        return super(ProductCreateMultipleView, self).get(request, *args, **kwargs)
