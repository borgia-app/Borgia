from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import logout
from django.db.models import Q

from shops.models import *
from shops.forms import *
from finances.models import Purchase
from users.models import User


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
    # Liste des unites de produits, hors bières issues de fûts, disponibles au foyer (ex: sirop de fraise, ...)
    product_unit_other_list = ProductUnit.objects.filter(Q(type='other'))

    # Cas du premier envoi
    if request.method == 'POST':
        form = PurchaseFoyerForm(request.POST, tap_list=tap_list, single_product_list=single_product_list,
                                 product_unit_other_list=product_unit_other_list)

        if form.is_valid():

            # Creations des dictionnaires (demande, element) de correspondance
            list_results_tap = []
            list_results_single_product = []
            list_results_product_unit_other = []

            for i in range(0, len(tap_list)):
                list_results_tap.append((form.cleaned_data["field_tap_%s" % i], tap_list[i]))
            for i in range(0, len(single_product_list)):
                list_results_single_product.append((form.cleaned_data["field_single_product_%s" % i],
                                                    single_product_list[i]))
            for i in range(0, len(product_unit_other_list)):
                list_results_product_unit_other.append((form.cleaned_data["field_product_unit_other_%s" % i],
                                                        product_unit_other_list[i]))

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
                    spfc = SingleProductFromContainer(container=e[1].container, quantity=e[0]*25,
                                                      price=e[0]*e[1].container.product_unit.price_glass(),
                                                      purchase=purchase)
                    spfc.save()

            # Sirops, softs et alcools fort
            for e in list_results_product_unit_other:
                if e[0] != 0:
                    # 1 ou 0 pour debut de la liste ?
                    # 4 ou 25 cl ? ou même autre chose, il faut differencier les cas
                    # soft -> 25 cl
                    # alcool fort, sirop -> 4 cl
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
                    k = 0  # k est le nombres d'objets similaires a e[1] que l'on a lie a la purchase courante
                    if e[0] <= len(SingleProduct.objects.filter(Q(name=e[1]) & Q(is_sold=False))):
                        lim = e[0]
                    else:
                        lim = len(SingleProduct.objects.filter(Q(name=e[1]) & Q(is_sold=False)))
                    while k < lim:
                        sp = SingleProduct.objects.filter(Q(name=e[1]) & Q(is_sold=False))[k]
                        sp.purchase = purchase
                        sp.is_sold = True
                        sp.save()
                        k += 1

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
        dict_field_product_unit_other = []
        initial = {}

        for i in range(0, len(tap_list)):
            initial['field_tap_%s' % i] = 0
        for i in range(0, len(single_product_list)):
            initial['field_single_product_%s' % i] = 0
        for i in range(0, len(product_unit_other_list)):
            initial['field_product_unit_other_%s' % i] = 0

        form = PurchaseFoyerForm(tap_list=tap_list, single_product_list=single_product_list,
                                 product_unit_other_list=product_unit_other_list, initial=initial)

        for i in range(0, len(tap_list)):  # Envoi de l'object directement
            dict_field_tap.append((form['field_tap_%s' % i], tap_list[i], i))
        for i in range(0, len(single_product_list)):  # Attention, envoi d'un object, mais ce sont tous les mêmes
            dict_field_single_product.append((form['field_single_product_%s' % i],
                                              SingleProduct.objects.filter(name=single_product_list[i])[0], i))
        for i in range(0, len(product_unit_other_list)):  # Attention, envoi d'un object, mais ce sont tous les mêmes
            dict_field_product_unit_other.append((form['field_product_unit_other_%s' % i],
                                                  ProductUnit.objects.filter(name=product_unit_other_list[i])[0], i))

    return render(request, 'shops/purchase_foyer.html', locals())


def workboard_foyer(request):
    return render(request, 'shops/workboard_foyer.html')


# Model TAP
# C
class TapCreateView(CreateView):
    model = Tap
    fields = ['number']
    template_name = 'shops/tap_create.html'
    success_url = '/shops/tap/list'


# R
class TapRetrieveView(DetailView):
    model = Tap
    template_name = 'shops/tap_retrieve.html'


# U
class TapUpdateView(UpdateView):
    model = Tap
    fields = ['number', 'container']
    template_name = 'shops/tap_update.html'
    success_url = '/shops/tap/list'


# D
class TapDeleteView(DeleteView):
    model = Tap
    template_name = 'shops/tap_delete.html'
    success_url = '/shops/tap/list'


# List
class TapListView(ListView):
    model = Tap
    template_name = 'shops/tap_list.html'
    queryset = Tap.objects.all()


# Model SHOP
# C
class ShopCreateView(CreateView):
    model = Shop
    fields = ['name', 'description']
    template_name = 'shops/shop_create.html'
    success_url = '/shops/shop/list'


# R
class ShopRetrieveView(DetailView):
    model = Shop
    template_name = 'shops/shop_retrieve.html'


# U
class ShopUpdateView(UpdateView):
    model = Shop
    fields = ['name', 'description']
    template_name = 'shops/shop_update.html'
    success_url = '/shops/shop/list'


# D
class ShopDeleteView(DeleteView):
    model = Shop
    template_name = 'shops/shop_delete.html'
    success_url = '/shops/shop/list'


# List
class ShopListView(ListView):
    model = Shop
    template_name = 'shops/shop_list.html'
    queryset = Shop.objects.all()


# Model SINGLEPRODUCT
# C
class SingleProductCreateView(CreateView):
    model = SingleProduct
    fields = ['name', 'description', 'price', 'shop']
    template_name = 'shops/singleproduct_create.html'
    success_url = '/shops/singleproduct/list'


# R
class SingleProductRetrieveView(DetailView):
    model = SingleProduct
    template_name = 'shops/singleproduct_retrieve.html'


# U
class SingleProductUpdateView(UpdateView):
    model = SingleProduct
    fields = ['name', 'description', 'is_available_for_sale', 'is_available_for_borrowing', 'peremption_date',
              'is_sold', 'price', 'shop']
    template_name = 'shops/singleproduct_update.html'
    success_url = '/shops/singleproduct/list'


# D
class SingleProductDeleteView(DeleteView):
    model = SingleProduct
    template_name = 'shops/singleproduct_delete.html'
    success_url = '/shops/singleproduct/list'


# List
class SingleProductListView(ListView):
    model = SingleProduct
    template_name = 'shops/singleproduct_list.html'
    queryset = SingleProduct.objects.all()


# Model CONTAINER
# C
class ContainerCreateView(CreateView):
    model = Container
    fields = ['product_unit', 'initial_quantity', 'is_returnable', 'value_when_returned']
    template_name = 'shops/container_create.html'
    success_url = '/shops/container/list'


# R
class ContainerRetrieveView(DetailView):
    model = Container
    template_name = 'shops/container_retrieve.html'


# U
class ContainerUpdateView(UpdateView):
    model = Container
    fields = ['product_unit', 'initial_quantity', 'is_returnable', 'value_when_returned']
    template_name = 'shops/container_update.html'
    success_url = '/shops/container/list'


# D
class ContainerDeleteView(DeleteView):
    model = Container
    template_name = 'shops/container_delete.html'
    success_url = '/shops/container/list'


# List
class ContainerListView(ListView):
    model = Container
    template_name = 'shops/container_list.html'
    queryset = Container.objects.all()


# Model PRODUCTUNIT
# C
class ProductUnitCreateView(CreateView):
    model = ProductUnit
    fields = ['name', 'description', 'price', 'unit', 'type', 'shop']
    template_name = 'shops/productunit_create.html'
    success_url = '/shops/productunit/list'


# R
class ProductUnitRetrieveView(DetailView):
    model = ProductUnit
    template_name = 'shops/productunit_retrieve.html'


# U
class ProductUnitUpdateView(UpdateView):
    model = ProductUnit
    fields = ['name', 'description', 'price', 'unit', 'type', 'shop']
    template_name = 'shops/productunit_update.html'
    success_url = '/shops/productunit/list'


# D
class ProductUnitDeleteView(DeleteView):
    model = ProductUnit
    template_name = 'shops/productunit_delete.html'
    success_url = '/shops/productunit/list'


# List
class ProductUnitListView(ListView):
    model = ProductUnit
    template_name = 'shops/productunit_list.html'
    queryset = ProductUnit.objects.all()