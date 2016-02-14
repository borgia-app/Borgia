#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect, force_text
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth import logout
from django.db.models import Q
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from shops.models import *
from shops.forms import *
from finances.models import Purchase
from users.models import User


# FOYER
# TODO: a modifier
def purchase_foyer(request):

    # PB a resoudre :
    # Pas de problème si l'integer field est mal renseigne (negatif ou alpha etc)
    # Mais problème s'il est vide !
    # La methode post passe quand même, mais on n'entre pas dans le if, que faire ??

    # Ne pas commander avec un solde negatif

    # Peut être utiliser une FormView (mais plus complexe a cause du tap_list qu'il faut envoyer ...)
    # Cf get_context_data avec kwargs: tap_list

    # Que se passe-t-il si on change un fut entre temps sur une tireuse ?
    # Il vaut peut être mieux passer le container plutôt que la tireuse ?

    # Liste des tireuses en service (qui ont un container)
    tap_list = Tap.objects.filter(container__isnull=False)
    # Liste des objects unitaires disponibles au foyer (ex: skolls 33cl, ...)
    single_product_list = Shop.objects.get(name="Foyer").list_single_product_unsold_name()
    single_product_list_qt = Shop.objects.get(name="Foyer").list_single_product_unsold_qt()
    # Liste des unites de produits, hors bières issues de fûts, disponibles au foyer (ex: sirop de fraise, ...)
    product_unit_soft_list = ProductUnit.objects.filter(Q(type='soft'))
    product_unit_liquor_list = ProductUnit.objects.filter(Q(type='liquor'))

    # Cas du premier envoi
    if request.method == 'POST':
        form = PurchaseFoyerForm(request.POST, tap_list=tap_list, single_product_list=single_product_list,
                                 single_product_list_qt=single_product_list_qt,
                                 product_unit_soft_list=product_unit_soft_list,
                                 product_unit_liquor_list=product_unit_liquor_list)

        if form.is_valid():

            # Creations des dictionnaires (demande, element) de correspondance
            list_results_tap = []
            list_results_single_product = []
            list_results_product_unit_soft = []
            list_results_product_unit_liquor = []

            for i in range(0, len(tap_list)):
                list_results_tap.append((form.cleaned_data["field_tap_%s" % i], tap_list[i]))
            for i in range(0, len(single_product_list)):
                list_results_single_product.append((form.cleaned_data["field_single_product_%s" % i],
                                                    single_product_list[i]))
            for i in range(0, len(product_unit_soft_list)):
                list_results_product_unit_soft.append((form.cleaned_data["field_product_unit_soft_%s" % i],
                                                       product_unit_soft_list[i]))
            for i in range(0, len(product_unit_liquor_list)):
                list_results_product_unit_liquor.append((form.cleaned_data["field_product_unit_liquor_%s" % i],
                                                         product_unit_liquor_list[i]))

                # Creation de la purchase
                # Informations generales
            purchase = Purchase(operator=User.objects.get(username="AE_ENSAM"), client=request.user)
            purchase.save()

            # Objects
            # Issus d'un container
            # Fûts de bières, ce sont ceux qui sont sous les tireuses
            for e in list_results_tap:
                if e[0] != 0:  # Le client a pris un objet issu du container e[1]
                    # Creation d'un objet issu de e[1] lie a la purchase et sauvegarde
                    spfc = SingleProductFromContainer(container=e[1].container, quantity=e[0]*75,
                                                      price=e[0]*e[1].container.product_unit.price_glass(),
                                                      purchase=purchase)
                    spfc.save()

            # Sirops, softs et alcools fort
            for e in list_results_product_unit_soft:
                if e[0] != 0:
                    spfc = SingleProductFromContainer(container=Container.objects.filter(product_unit__name=e[1])[0],
                                                      quantity=e[0]*75,
                                                      price=e[0]*ProductUnit.objects.filter(name=e[1])[0].price_glass(),
                                                      purchase=purchase)
                    spfc.save()
            for e in list_results_product_unit_liquor:
                if e[0] != 0:
                    spfc = SingleProductFromContainer(container=Container.objects.filter(product_unit__name=e[1])[0],
                                                      quantity=e[0]*4,
                                                      price=e[0]*ProductUnit.objects.filter(name=e[1])[0].price_shoot(),
                                                      purchase=purchase)
                    spfc.save()

            # Objects unitaires - ex: Skolls
            # Nous avons seulement le nom, on s'en fiche de savoir quel est l'objet que l'on prend, on le prend
            # dans l'ordre de la liste ...
            # Il faut supposer que les prix sont les mêmes pour tous, si ce n'est pas le cas il faudra lisser les prix
            # quand on ajoute un produit plus ou moins cher dans la liste
            for e in list_results_single_product:
                if e[0] != 0:
                    # Le client demande e[0] objets identiques a e[1]
                    # On les prends dans l'ordre du queryset (on s'en fiche) des objets non vendus bien sûr
                    # La limitation se fait directement dans le form, via _list_qt
                    for i in range(0, e[0]):
                        sp = SingleProduct.objects.filter(Q(name=e[1]) & Q(is_sold=False))[i]
                        sp.purchase = purchase
                        sp.is_sold = True
                        sp.save()

            # Payement total par le foyer
            # Debit du client + verification
            if purchase.client.debit(purchase.total_product()) == purchase.total_product():
                purchase.foyer = purchase.total_product()
                purchase.save()
            # SINON ERREUR

            # Deconnection
            logout(request)

            # Affichage de la purchase au client
            return render(request, 'shops/purchase_validation_foyer.html', {'purchase': purchase})

    else:
        # Creation des dictionnaires (field, element, n°) de correspondance
        # Sert a l'affichage sur le template et au post traitement
        dict_field_tap = []
        dict_field_single_product = []
        dict_field_product_unit_soft = []
        dict_field_product_unit_liquor = []
        initial = {}

        for i in range(0, len(tap_list)):
            initial['field_tap_%s' % i] = 0
        for i in range(0, len(single_product_list)):
            initial['field_single_product_%s' % i] = 0
        for i in range(0, len(product_unit_soft_list)):
            initial['field_product_unit_soft_%s' % i] = 0
        for i in range(0, len(product_unit_liquor_list)):
            initial['field_product_unit_liquor_%s' % i] = 0
        form = PurchaseFoyerForm(tap_list=tap_list, single_product_list=single_product_list,
                                 single_product_list_qt=single_product_list_qt,
                                 product_unit_soft_list=product_unit_soft_list,
                                 product_unit_liquor_list=product_unit_liquor_list, initial=initial)

        for i in range(0, len(tap_list)):  # Envoi de l'object directement
            dict_field_tap.append((form['field_tap_%s' % i], tap_list[i], i))
        for i in range(0, len(single_product_list)):  # Attention, envoi d'un object, mais ce sont tous les mêmes
            dict_field_single_product.append((form['field_single_product_%s' % i],
                                              SingleProduct.objects.filter(name=single_product_list[i])[0], i))
        for i in range(0, len(product_unit_soft_list)):
            dict_field_product_unit_soft.append((form['field_product_unit_soft_%s' % i],
                                                 ProductUnit.objects.filter(name=product_unit_soft_list[i])[0], i))
        for i in range(0, len(product_unit_liquor_list)):
            dict_field_product_unit_liquor.append((form['field_product_unit_liquor_%s' % i],
                                                   ProductUnit.objects.filter(name=product_unit_liquor_list[i])[0], i))

    return render(request, 'shops/purchase_foyer.html', locals())


# TODO: a modifier
def workboard_foyer(request):

    list_tap = Tap.objects.all()
    return render(request, 'shops/workboard_foyer.html', locals())


# Model SHOP
# C
class ShopCreateView(SuccessMessageMixin, CreateView):
    model = Shop
    fields = ['name', 'description']
    template_name = 'shops/shop_create.html'
    success_url = '/shops/shop/'
    success_message = "%(name)s was created successfully"

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(ShopCreateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


# R
class ShopRetrieveView(DetailView):
    model = Shop
    template_name = 'shops/shop_retrieve.html'


# U
class ShopUpdateView(SuccessMessageMixin, UpdateView):
    model = Shop
    fields = ['name', 'description']
    template_name = 'shops/shop_update.html'
    success_url = '/shops/shop/'
    success_message = "%(name)s was updated successfully"

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.success_url))


# D
class ShopDeleteView(SuccessMessageMixin, DeleteView):
    model = Shop
    template_name = 'shops/shop_delete.html'
    success_url = '/shops/shop/'
    success_message = "Shop was deleted successfully"

    # Nécessaire en attendant que SuccessMessageMixin fonctionne avec DeleteView
    # https://code.djangoproject.com/ticket/21926
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ShopDeleteView, self).delete(request, *args, **kwargs)


# List
class ShopListView(ListView):
    model = Shop
    template_name = 'shops/shop_list.html'
    queryset = Shop.objects.all()


# Model SINGLEPRODUCT
# C
class SingleProductCreateView(SuccessMessageMixin, CreateView):
    model = SingleProduct
    fields = ['product_base', 'price', 'purchase_date', 'expiry_date', 'place']
    template_name = 'shops/singleproduct_create.html'
    success_url = '/shops/singleproduct/'
    success_message = "single product was created successfully"

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(SingleProductCreateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


# TODO: à modifier
class SingleProductCreateMultipleView(FormView):
    template_name = 'shops/singleproduct_create_multiple.html'
    form_class = SingleProductCreateMultipleForm
    success_url = '/shops/singleproduct/'

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def form_valid(self, form):

        for i in range(0, form.cleaned_data['quantity']):
            SingleProduct(name=form.cleaned_data['single_product'].name,
                          description=form.cleaned_data['single_product'].description,
                          price=form.cleaned_data['price'],
                          shop=Shop.objects.get(name=self.request.GET.get('shop', 'Foyer'))
                          ).save()

        return super(SingleProductCreateMultipleView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(SingleProductCreateMultipleView, self).get_form_kwargs()
        kwargs['single_product_list'] = Shop.objects.get(name=self.request.GET.get('shop', 'Foyer')).list_single_product()

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SingleProductCreateMultipleView, self).get_context_data(**kwargs)
        context['shop'] = Shop.objects.get(name=self.request.GET.get('shop', 'Foyer'))
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


# R
class SingleProductRetrieveView(DetailView):
    model = SingleProduct
    template_name = 'shops/singleproduct_retrieve.html'


# U
class SingleProductUpdateView(SuccessMessageMixin, UpdateView):
    model = SingleProduct
    fields = ['product_base', 'price', 'purchase_date', 'expiry_date', 'place', 'is_sold']
    template_name = 'shops/singleproduct_update.html'
    success_url = '/shops/singleproduct/'
    success_message = "%(name)s was updated successfully"

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.success_url))


# D
class SingleProductDeleteView(SuccessMessageMixin, DeleteView):
    model = SingleProduct
    template_name = 'shops/singleproduct_delete.html'
    success_url = '/shops/singleproduct/'
    success_message = "Single product was delated successfully"

    # Nécessaire en attendant que SuccessMessageMixin fonctionne avec DeleteView
    # https://code.djangoproject.com/ticket/21926
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(SingleProductDeleteView, self).delete(request, *args, **kwargs)


# List
class SingleProductListView(ListView):
    model = SingleProduct
    template_name = 'shops/singleproduct_list.html'
    queryset = SingleProduct.objects.all()


# TODO: a modifier
# Model CONTAINER
# C
class ContainerCreateView(SuccessMessageMixin, CreateView):
    model = Container
    fields = ['product_unit', 'initial_quantity', 'is_returnable', 'value_when_returned']
    template_name = 'shops/container_create.html'
    success_url = '/shops/container/'
    success_message = "Container was created successfully"

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(ContainerCreateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


class ContainerCreateMultipleView(FormView):
    template_name = 'shops/container_create_multiple.html'
    form_class = ContainerCreateMultipleForm
    success_url = '/shops/container/'

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def form_valid(self, form):

        for i in range(0, form.cleaned_data['quantity']):
            Container(product_unit=form.cleaned_data['container'].product_unit,
                      initial_quantity=form.cleaned_data['container'].initial_quantity,
                      is_returnable=form.cleaned_data['container'].is_returnable,
                      shop=Shop.objects.get(name=self.request.GET.get('shop', 'Foyer'))).save()

        return super(ContainerCreateMultipleView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ContainerCreateMultipleView, self).get_form_kwargs()
        kwargs['container_list'] = Container.objects.filter(
                shop=Shop.objects.get(name=self.request.GET.get('shop', 'Foyer')))

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ContainerCreateMultipleView, self).get_context_data(**kwargs)
        context['shop'] = Shop.objects.get(name=self.request.GET.get('shop', 'Foyer'))
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


# R
class ContainerRetrieveView(DetailView):
    model = Container
    template_name = 'shops/container_retrieve.html'


# U
class ContainerUpdateView(SuccessMessageMixin, UpdateView):
    model = Container
    fields = ['product_unit', 'initial_quantity', 'is_returnable', 'value_when_returned']
    template_name = 'shops/container_update.html'
    success_url = '/shops/container/'
    success_message = "Container was updated successfully"

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.success_url))


# D
class ContainerDeleteView(SuccessMessageMixin, DeleteView):
    model = Container
    template_name = 'shops/container_delete.html'
    success_url = '/shops/container/list'
    success_message = "Container was delated successfully"

    # Nécessaire en attendant que SuccessMessageMixin fonctionne avec DeleteView
    # https://code.djangoproject.com/ticket/21926
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ContainerDeleteView, self).delete(request, *args, **kwargs)


# List
class ContainerListView(ListView):
    model = Container
    template_name = 'shops/container_list.html'
    queryset = Container.objects.all()


# TODO: a modifier
# Model PRODUCTUNIT
# C
class ProductUnitCreateView(SuccessMessageMixin, CreateView):
    model = ProductUnit
    fields = ['name', 'description', 'price', 'unit', 'type', 'shop']
    template_name = 'shops/productunit_create.html'
    success_url = '/shops/productunit/list'
    success_message = "%(name)s was created successfully"

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(ProductUnitCreateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


# R
class ProductUnitRetrieveView(DetailView):
    model = ProductUnit
    template_name = 'shops/productunit_retrieve.html'


# U
class ProductUnitUpdateView(SuccessMessageMixin, UpdateView):
    model = ProductUnit
    fields = ['name', 'description', 'price', 'unit', 'type', 'shop']
    template_name = 'shops/productunit_update.html'
    success_url = '/shops/productunit/list'
    success_message = "%(name)s was updated successfully"

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.success_url))


# D
class ProductUnitDeleteView(SuccessMessageMixin, DeleteView):
    model = ProductUnit
    template_name = 'shops/productunit_delete.html'
    success_url = '/shops/productunit/list'
    success_message = "Product unit was delated successfully"

    # Nécessaire en attendant que SuccessMessageMixin fonctionne avec DeleteView
    # https://code.djangoproject.com/ticket/21926
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ProductUnitDeleteView, self).delete(request, *args, **kwargs)


# List
class ProductUnitListView(ListView):
    model = ProductUnit
    template_name = 'shops/productunit_list.html'
    queryset = ProductUnit.objects.all()