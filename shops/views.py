from django.core import serializers
from math import ceil

from django.shortcuts import render, force_text, HttpResponseRedirect, redirect
from django.shortcuts import HttpResponse, Http404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView, View
from django.contrib.auth import logout
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from shops.models import *
from shops.forms import *
from users.models import User
from finances.models import *
from notifications.models import notify
from borgia.utils import *


class ProductList(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                  GroupLateralMenuFormMixin):
    template_name = 'shops/product_list.html'
    perm_codename = 'list_product'
    lm_active = 'lm_product_list'
    form_class = ProductListForm

    search = None
    type = None

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context['product_list'] = self.form_query(
            ProductBase.objects.filter(shop=self.shop))
        return context

    def form_valid(self, form):
        if form.cleaned_data['search']:
            self.search = form.cleaned_data['search']

        if form.cleaned_data['type']:
            self.type = form.cleaned_data['type']

        return self.get(self.request, self.args, self.kwargs)

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(name__contains=self.search)
                | Q(description__contains=self.search)
            )
        if self.type:
            query = query.filter(type=self.type)
        return query


class ProductCreate(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                    GroupLateralMenuFormMixin):
    template_name = 'shops/product_create.html'
    perm_codename = 'add_product'
    lm_active = 'lm_product_create'
    form_class = ProductCreateForm
    product_class = None

    def dispatch(self, request, *args, **kwargs):
        try:
            if kwargs['product_class'] is ProductBase:
                self.product_class = ProductBase
                self.form_class = ProductBaseCreateForm
            if kwargs['product_class'] is ProductUnit:
                self.product_class = ProductUnit
                self.form_class = ProductUnitCreateForm
        except KeyError:
            pass
        return super(ProductCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if self.product_class is None:
            self.form_valid_instance(form)
        if self.product_class is ProductBase:
            self.form_valid_productbase(form)
            self.success_url = reverse(
                'url_product_create', kwargs={'group_name': self.group.name}
            )
        if self.product_class is ProductUnit:
            self.form_valid_productunit(form)
            self.success_url = reverse(
                'url_productbase_create', kwargs={'group_name': self.group.name}
            )
        return super(ProductCreate, self).form_valid(form)

    def form_valid_instance(self, form):

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

    def form_valid_productbase(self, form):
        if form.cleaned_data['type'] == 'container':
            ProductBase.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                brand=form.cleaned_data['brand'],
                type=form.cleaned_data['type'],
                shop=self.shop,
                quantity=form.cleaned_data['quantity'],
                product_unit=form.cleaned_data['product_unit']
            )
        if form.cleaned_data['type'] == 'single_product':
            ProductBase.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                brand=form.cleaned_data['brand'],
                type=form.cleaned_data['type'],
                shop=self.shop
            )

    def form_valid_productunit(self, form):
        ProductUnit.objects.create(
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'],
            unit=form.cleaned_data['unit'],
            type=form.cleaned_data['type'],
            shop=self.shop
        )

    def get_initial(self):
        initial = super(ProductCreate, self).get_initial()
        if self.product_class is None:
            initial['purchase_date'] = now
        return initial

    def get_context_data(self, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)
        context['shop'] = self.shop
        context['group'] = self.group
        try:
            context['product_class'] = self.product_class._meta.model_name
        except AttributeError:
            pass
        return context

    def get_form_kwargs(self):
        kwargs_form = super(ProductCreate, self).get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form


class ProductDeactivate(GroupPermissionMixin, ProductShopFromGroupMixin, View,
                        GroupLateralMenuMixin):
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


class ProductRetrieve(GroupPermissionMixin, ProductShopFromGroupMixin, View,
                      GroupLateralMenuMixin):
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


class ProductUpdate(GroupPermissionMixin, ProductShopFromGroupMixin ,FormView,
                    GroupLateralMenuFormMixin):
    """
    Update a product and redirect to the workboard of the group.

    :param kwargs['group_name']: name of the group used.
    :param kwargs['pk']: pk of the product
    :param self.perm_codename: codename of the permission checked.
    """
    form_class = ProductUpdateForm
    template_name = 'shops/product_update.html'
    success_url = None
    perm_codename = None

    def get_context_data(self, **kwargs):
        context = super(ProductUpdate, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def get_initial(self):
        initial = super(ProductUpdate, self).get_initial()
        for k in ProductUpdateForm().fields.keys():
            initial[k] = getattr(self.object, k)
        return initial

    def form_valid(self, form):
        for k in form.fields.keys():
            if form.cleaned_data[k] != getattr(self.object, k):
                setattr(self.object, k, form.cleaned_data[k])
        self.object.save()
        return super(ProductUpdate, self).form_valid(form)


class ShopCreate(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    template_name = 'shops/shop_create.html'
    perm_codename = 'add_shop'
    lm_active = 'lm_shop_create'
    form_class = ShopCreateForm
    perm_chiefs = ['add_user', 'supply_money_user', 'add_product',
                   'change_product', 'retrieve_product', 'list_product',
                   'list_sale', 'retrieve_sale', 'user_operatorsalemodule']
    perm_associates = ['add_user', 'supply_money_user', 'add_product',
                   'change_product', 'retrieve_product', 'list_product',
                   'list_sale', 'retrieve_sale', 'user_operatorsalemodule']

    def form_valid(self, form):
        """
        Create the shop instance and relating groups and permissions.
        """
        shop = Shop.objects.create(
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'])

        content_type = ContentType.objects.get(app_label='users', model='user')
        manage_chiefs = Permission.objects.create(
            name='Gérer le groupe des chiefs du magasin '+shop.name,
            codename='manage_group_chiefs-'+shop.name,
            content_type=content_type
        )
        manage_associates = Permission.objects.create(
            name='Gérer le groupe des associés du magasin '+shop.name,
            codename='manage_group_associates-'+shop.name,
            content_type=content_type
        )

        chiefs = Group.objects.create(
            name='chiefs-' + shop.name
        )
        associates = Group.objects.create(
            name='associates-' + shop.name
        )

        for codename in self.perm_chiefs:
            try:
                chiefs.permissions.add(
                    Permission.objects.get(codename=codename)
                )
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned:
                pass
        chiefs.permissions.add(manage_associates)
        chiefs.save()
        for codename in self.perm_associates:
            try:
                associates.permissions.add(
                    Permission.objects.get(codename=codename)
                )
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned:
                pass
        associates.save()

        presidents = Group.objects.get(pk=2)
        presidents.permissions.add(manage_chiefs)
        presidents.save()
        vice_presidents = Group.objects.get(pk=3)
        vice_presidents.permissions.add(manage_chiefs)
        vice_presidents.save()
        return super(ShopCreate, self).form_valid(form)


class ShopList(GroupPermissionMixin, View, GroupLateralMenuMixin):
    template_name = 'shops/shop_list.html'
    perm_codename = 'list_shop'
    lm_active = 'lm_shop_list'

    def get(self, request, *args, **kwargs):
        context = super(ShopList, self).get_context_data(**kwargs)
        context['shop_list'] = Shop.objects.all().exclude(pk=1)
        return render(request, self.template_name, context=context)


class PurchaseFoyer(FormView):
    form_class = PurchaseFoyerForm
    template_name = 'shops/sale_foyer.html'
    success_url = '/auth/login'

    def get_form_kwargs(self):
        kwargs = super(PurchaseFoyer, self).get_form_kwargs()
        kwargs['active_keg_container_list'] = Container.objects.filter(product_base__shop=Shop.objects.get(name='foyer'),
                                                                       product_base__product_unit__type='keg',
                                                                       place__startswith='tireuse')
        kwargs['single_product_available_list'] = Shop.objects.get(name='foyer').list_product_base_single_product(status_sold=False)
        kwargs['shooter_available_list'] = Shop.objects.get(name='foyer').list_product_base_single_product_shooter(status_sold=False)
        kwargs['container_soft_list'] = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False, type='soft')
        kwargs['container_syrup_list'] = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False, type='syrup')
        kwargs['container_liquor_list'] = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False,
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
        active_keg_container_list = Container.objects.filter(product_base__shop=Shop.objects.get(name='foyer'),
                                                             product_base__product_unit__type='keg',
                                                             place__startswith='tireuse')
        single_product_available_list = Shop.objects.get(name='foyer').list_product_base_single_product(status_sold=False)
        shooter_available_list = Shop.objects.get(name='foyer').list_product_base_single_product_shooter(status_sold=False)
        container_soft_list = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False, type='soft')
        container_syrup_list = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False, type='syrup')
        container_liquor_list = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False,
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
        active_keg_container_list = Container.objects.filter(product_base__shop=Shop.objects.get(name='foyer'),
                                                             product_base__product_unit__type='keg',
                                                             place__startswith='tireuse')
        single_product_available_list = Shop.objects.get(name='foyer').list_product_base_single_product(status_sold=False)
        shooter_available_list = Shop.objects.get(name='foyer').list_product_base_single_product_shooter(status_sold=False)
        container_soft_list = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False, type='soft')
        container_syrup_list = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False, type='syrup')
        container_liquor_list = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False,
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

        active_keg_container_list = Container.objects.filter(product_base__shop=Shop.objects.get(name='foyer'),
                                                             product_base__product_unit__type='keg',
                                                             place__startswith='tireuse')
        single_product_available_list = Shop.objects.get(name='foyer').list_product_base_single_product(status_sold=False)
        shooter_available_list = Shop.objects.get(name='foyer').list_product_base_single_product_shooter(status_sold=False)
        container_soft_list = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False, type='soft')
        container_syrup_list = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False, type='syrup')
        container_liquor_list = Shop.objects.get(name='foyer').list_product_base_container(status_sold=False,
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
