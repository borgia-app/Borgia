#-*- coding: utf-8 -*-
from django.shortcuts import render, force_text
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth import logout
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from shops.models import *
from shops.forms import *
from users.models import User
from finances.models import Sale, DebitBalance, Payment


# FOYER

class ReplacementActiveKeyView(FormView):
    template_name = 'shops/replacement_active_keg.html'
    form_class = ReplacementActiveKegForm
    success_url = '/auth/login'

    def form_valid(self, form):

        # Définition des objets de travail

        # L'ancien fut, s'il existe, est envoyé vers le stock
        if self.request.GET.get('pk', None) is not '':
            old_keg = Container.objects.get(pk=self.request.GET.get('pk', None))
            old_keg.place = "stock foyer"
            old_keg.save()

        # Le nouveau est envoyé sous la tireuse
        new_keg = form.cleaned_data['new_keg']
        new_keg.place = self.request.GET.get('place', None)
        new_keg.save()

        return super(ReplacementActiveKeyView, self).form_valid(form)

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(ReplacementActiveKeyView, self).get_context_data(**kwargs)
        if self.request.GET.get('pk', None) is not '':
            context['old_active_keg'] = Container.objects.get(pk=self.request.GET.get('pk', None))
        else:
            context['old_active_keg'] = 'Pas de fut actuellement'
        return context


def purchase_foyer(request):

    # Peut être utiliser une FormView (mais plus complexe a cause du tap_list qu'il faut envoyer ...)
    # Cf get_context_data avec kwargs: tap_list

    # Liste des conteneurs utilisés sous une tireuse
    active_keg_container_list = Container.objects.filter(product_base__shop=Shop.objects.get(name='Foyer'),
                                                         product_base__product_unit__type='keg',
                                                         place__startswith='tireuse')
    # Liste des objects unitaires disponibles au foyer (ex: skolls 33cl, ...)
    single_product_available_list = Shop.objects.get(name='Foyer').list_product_base_single_product(status_sold=False)
    # Liste des conteneurs, hors futs, disponibles au foyer (ex: sirop de fraise, ...)
    container_soft_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='soft')
    container_syrup_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False, type='syrup')
    container_liquor_list = Shop.objects.get(name='Foyer').list_product_base_container(status_sold=False,
                                                                                       type='liquor')

    # Cas du POST
    if request.method == 'POST':

        # Création du formulaire de base
        form = PurchaseFoyerForm(request.POST,
                                 active_keg_container_list=active_keg_container_list,
                                 single_product_available_list=single_product_available_list,
                                 container_soft_list=container_soft_list,
                                 container_syrup_list=container_syrup_list,
                                 container_liquor_list=container_liquor_list)

        # Formulaire valide -> traitement des données
        if form.is_valid():

            # Initialisation des listes de réponses
            list_results_active_keg_container = []
            list_results_single_product = []
            list_results_container_soft = []
            list_results_container_syrup = []
            list_results_container_liquor = []

            for i in range(0, len(active_keg_container_list)):
                list_results_active_keg_container.append((form.cleaned_data["field_active_keg_container_%s" % i],
                                                          active_keg_container_list[i]))
            for i in range(0, len(single_product_available_list)):
                list_results_single_product.append((form.cleaned_data["field_single_product_%s" % i],
                                                    single_product_available_list[i][0]))
            for i in range(0, len(container_soft_list)):
                list_results_container_soft.append((form.cleaned_data["field_container_soft_%s" % i],
                                                    container_soft_list[i][0]))
            for i in range(0, len(container_liquor_list)):
                list_results_container_liquor.append((form.cleaned_data["field_container_liquor_%s" % i],
                                                      container_liquor_list[i][0]))
            for i in range(0, len(container_syrup_list)):
                list_results_container_syrup.append((form.cleaned_data["field_container_syrup_%s" % i],
                                                     container_syrup_list[i][0]))

            # Creation de la vente entre l'AE ENSAM (représentée par le foyer) et le client

            # Informations generales
            sale = Sale(date=datetime.now(),
                        sender=request.user,
                        recipient=User.objects.get(username="AE_ENSAM"),
                        operator=request.user)
            sale.save()

            # Objects

            # Objects unitaires - ex: Skolls
            for e in list_results_single_product:
                if e[0] != 0:
                    # Le client demande e[0] objets identiques au produit de base e[1]
                    # On les prends dans l'ordre du queryset (on s'en fiche) des objets non vendus bien sûr
                    # Le prix de vente est le prix du base product à l'instant de la vente
                    for i in range(0, e[0]):
                        sp = SingleProduct.objects.filter(product_base=e[1])[0]
                        sp.save()
                        sp.is_sold = True
                        sp.sale = sale
                        sp.sale_price = sp.product_base.calculated_price
                        sp.save()

            # Issus d'un container
            # Fûts de bières, ce sont ceux qui sont sous les tireuses
            for e in list_results_active_keg_container:
                if e[0] != 0:  # Le client a pris un objet issu du container e[1]
                    # Création d'un objet fictif qui correspond à un bout du conteneur
                    # Le prix de vente est le prix du base product à l'instant de la vente
                    spfc = SingleProductFromContainer(container=e[1], sale=sale)
                    spfc.save()
                    spfc.quantity = spfc.container.product_base.product_unit.usual_quantity() * e[0]
                    spfc.sale_price = spfc.container.product_base.calculated_price_usual() * e[0]
                    spfc.save()

            # Soft, syrup et liquor
            # Le traitement est le même pour tous, je n'utilise qu'une seule liste
            list_results_container_no_keg = \
                list_results_container_soft + list_results_container_syrup + list_results_container_liquor
            for e in list_results_container_no_keg:
                if e[0] != 0:
                    # Premier conteneur de la liste dans le queryset du product base
                    spfc = SingleProductFromContainer(container=Container.objects.filter(product_base=e[1])[0],
                                                      sale=sale)
                    spfc.save()
                    spfc.quantity = e[0] * e[1].product_unit.usual_quantity()
                    spfc.sale_price = e[1].calculated_price_usual() * e[0]
                    spfc.save()

            # Payement total par le foyer ici

            # Total à payer d'après les achats
            sale.maj_amount()

            # Création d'un débit sur compte foyer
            d_b = DebitBalance(amount=sale.amount,
                               date=datetime.now(),
                               sender=sale.sender,
                               recipient=sale.recipient)
            d_b.save()

            # Création d'un paiement
            payment = Payment()
            payment.save()
            # Liaison entre le paiement et le debit sur compte foyer
            payment.debit_balance.add(d_b)
            payment.save()
            payment.maj_amount()
            payment.save()

            # Liaison entre le paiement et la vente
            sale.payment = payment
            sale.save()

            # Paiement par le client
            sale.payment.debit_balance.all()[0].set_movement()

            # Deconnection
            logout(request)

            # Affichage de la purchase au client
            return render(request, 'shops/sale_validation_foyer.html', {'sale': sale})

    else:
        # Creation des dictionnaires (field, element, n°) de correspondance
        # Sert a l'affichage sur le template et au post traitement
        dict_field_active_keg_container = []
        dict_field_single_product = []
        dict_field_container_soft = []
        dict_field_container_syrup = []
        dict_field_container_liquor = []
        initial = {}

        for i in range(0, len(active_keg_container_list)):
            initial['field_active_keg_container_%s' % i] = 0
        for i in range(0, len(single_product_available_list)):
            initial['field_single_product_%s' % i] = 0
        for i in range(0, len(container_soft_list)):
            initial['field_container_soft_%s' % i] = 0
        for i in range(0, len(container_syrup_list)):
            initial['field_container_syrup_%s' % i] = 0
        for i in range(0, len(container_liquor_list)):
            initial['field_container_liquor_%s' % i] = 0

        form = PurchaseFoyerForm(active_keg_container_list=active_keg_container_list,
                                 single_product_available_list=single_product_available_list,
                                 container_soft_list=container_soft_list,
                                 container_syrup_list=container_syrup_list,
                                 container_liquor_list=container_liquor_list,
                                 initial=initial)

        for i in range(0, len(active_keg_container_list)):
            dict_field_active_keg_container.append((form['field_active_keg_container_%s' % i],
                                                    active_keg_container_list[i], i))
        for i in range(0, len(single_product_available_list)):
            dict_field_single_product.append((form['field_single_product_%s' % i],
                                              single_product_available_list[i][0], i))
        for i in range(0, len(container_soft_list)):
            dict_field_container_soft.append((form['field_container_soft_%s' % i],
                                              container_soft_list[i][0], i))
        for i in range(0, len(container_syrup_list)):
            dict_field_container_syrup.append((form['field_container_syrup_%s' % i],
                                               container_syrup_list[i][0], i))
        for i in range(0, len(container_liquor_list)):
            dict_field_container_liquor.append((form['field_container_liquor_%s' % i],
                                                container_liquor_list[i][0], i))

    return render(request, 'shops/sale_foyer.html', locals())


def workboard_foyer(request):

    # Liste des conteneurs sous une tireuse
    active_keg_container_list = []

    for i in range(1, 6):
        try:  # essai si un conteneur est à la tireuse i
            active_keg_container_list.append(('tireuse %s' % i, Container.objects.get(place='tireuse %s' % i)))
        except ObjectDoesNotExist:  # Cas où la tireuse est vide
            active_keg_container_list.append(('tireuse %s' % i, None))

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


class SingleProductCreateMultipleView(FormView):
    template_name = 'shops/singleproduct_create_multiple.html'
    form_class = SingleProductCreateMultipleForm
    success_url = '/shops/singleproduct/'

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def form_valid(self, form):

        for i in range(0, form.cleaned_data['quantity']):
            sp = SingleProduct(price=form.cleaned_data['price'],
                               purchase_date=form.cleaned_data['purchase_date'],
                               expiry_date=form.cleaned_data['expiry_date'],
                               place=form.cleaned_data['place'],
                               product_base=form.cleaned_data['product_base'])
            sp.save()

        return super(SingleProductCreateMultipleView, self).form_valid(form)

    def get_initial(self):
        initial = super(SingleProductCreateMultipleView, self).get_initial()
        initial['purchase_date'] = now
        return initial

    def get_context_data(self, **kwargs):
        context = super(SingleProductCreateMultipleView, self).get_context_data(**kwargs)
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


# Model CONTAINER
# C
class ContainerCreateView(SuccessMessageMixin, CreateView):
    model = Container
    fields = ['product_base', 'price', 'purchase_date', 'expiry_date', 'place']
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
            c = Container(price=form.cleaned_data['price'],
                          purchase_date=form.cleaned_data['purchase_date'],
                          expiry_date=form.cleaned_data['expiry_date'],
                          place=form.cleaned_data['place'],
                          product_base=form.cleaned_data['product_base'])
            c.save()

        return super(ContainerCreateMultipleView, self).form_valid(form)

    def get_initial(self):
        initial = super(ContainerCreateMultipleView, self).get_initial()
        initial['purchase_date'] = now
        return initial

    def get_context_data(self, **kwargs):
        context = super(ContainerCreateMultipleView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


# R
class ContainerRetrieveView(DetailView):
    model = Container
    template_name = 'shops/container_retrieve.html'


# U
class ContainerUpdateView(SuccessMessageMixin, UpdateView):
    model = Container
    fields = ['product_base', 'price', 'purchase_date', 'expiry_date', 'place']
    template_name = 'shops/container_update.html'
    success_url = '/shops/container/'
    success_message = "Container was updated successfully"

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.success_url))


# D
class ContainerDeleteView(SuccessMessageMixin, DeleteView):
    model = Container
    template_name = 'shops/container_delete.html'
    success_url = '/shops/container/'
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


# Model PRODUCTUNIT
# C
class ProductUnitCreateView(SuccessMessageMixin, CreateView):
    model = ProductUnit
    fields = ['name', 'description', 'unit', 'type']
    template_name = 'shops/productunit_create.html'
    success_url = '/shops/productunit/'
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
    fields = ['name', 'description', 'unit', 'type']
    template_name = 'shops/productunit_update.html'
    success_url = '/shops/productunit/'
    success_message = "%(name)s was updated successfully"

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.success_url))


# D
class ProductUnitDeleteView(SuccessMessageMixin, DeleteView):
    model = ProductUnit
    template_name = 'shops/productunit_delete.html'
    success_url = '/shops/productunit/'
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


# Model PRODUCTBASE
# C
class ProductBaseCreateView(SuccessMessageMixin, CreateView):
    model = ProductBase
    fields = ['name', 'description', 'brand', 'type', 'shop', 'calculated_price', 'quantity', 'product_unit']
    template_name = 'shops/productbase_create.html'
    success_url = '/shops/productbase/'
    success_message = "%(name)s was created successfully"

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(ProductBaseCreateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


# R
class ProductBaseRetrieveView(DetailView):
    model = ProductBase
    template_name = 'shops/productbase_retrieve.html'


# U
class ProductBaseUpdateView(SuccessMessageMixin, UpdateView):
    model = ProductBase
    fields = ['name', 'description', 'brand', 'type', 'shop', 'calculated_price', 'quantity', 'product_unit']
    template_name = 'shops/productbase_update.html'
    success_url = '/shops/productbase/'
    success_message = "%(name)s was updated successfully"

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.success_url))


# D
class ProductBaseDeleteView(SuccessMessageMixin, DeleteView):
    model = ProductUnit
    template_name = 'shops/productbase_delete.html'
    success_url = '/shops/productbase/'
    success_message = "Product base was delated successfully"

    # Nécessaire en attendant que SuccessMessageMixin fonctionne avec DeleteView
    # https://code.djangoproject.com/ticket/21926
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ProductBaseDeleteView, self).delete(request, *args, **kwargs)


# List
class ProductBaseListView(ListView):
    model = ProductBase
    template_name = 'shops/productbase_list.html'
    queryset = ProductBase.objects.all()