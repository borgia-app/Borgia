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
