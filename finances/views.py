#-*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse, force_text, redirect, Http404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView, View
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.contrib.auth.models import Group
from datetime import timedelta
from django.utils.timezone import now
import json, time, re, csv, xlsxwriter, operator, hashlib, decimal
from django.views.decorators.csrf import csrf_exempt


from finances.forms import *
from finances.models import *
from shops.models import Container, ProductBase
from users.models import user_from_token_tap, list_year
from borgia.models import FormNextView, CreateNextView, UpdateNextView, ListCompleteView
from django.conf import settings
from users.templatetags import users_extra
from contrib.models import add_to_breadcrumbs
from settings_data.models import Setting


def electrovanne_request1(request):
    data = []
    try:
        # Variables
        container = Container.objects.get(place='tireuse %s' % request.GET.get('tireuse_pk'))
        id = request.GET.get('id')
        user = user_from_token_tap(request.GET.get('token_pk'))
        sig = request.GET.get('sig')

        # Quantité max possible
        if user.balance <= 0:
            max_quantity = 0
        else:
            max_quantity = round(float((container.product_base.quantity * user.balance) / container.product_base.get_moded_price()), 0)

        # Vérification de la signature
        params = {
            'tireuse_pk': request.GET.get('tireuse_pk'),
            'id': id,
            'token_pk': request.GET.get('token_pk'),
            'sig': sig
        }
        if verify_token_algo_lydia(params, settings.ELECTROVANNE_TOKEN):
            # Ecriture de la liste
            data.append(request.GET.get('token_pk'))
            data.append(request.GET.get('tireuse_pk'))
            data.append(id)
            data.append(max_quantity)
        else:
            data.append('error0')

    except ObjectDoesNotExist:
        data.append('error0')

    return HttpResponse(json.dumps(data))


def electrovanne_request2(request):
    data = []
    try:
        # Variables (id inutile pour nous)
        container = Container.objects.get(place='tireuse %s' % request.GET.get('tireuse_pk'))
        user = user_from_token_tap(request.GET.get('token_pk'))
        quantity = request.GET.get('quantity')
        id = request.GET.get('id')
        sig = request.GET.get('sig')

        # Vérification de la signature
        params = {
            'tireuse_pk': request.GET.get('tireuse_pk'),
            'id': id,
            'quantity': quantity,
            'token_pk': request.GET.get('token_pk'),
            'sig': sig
        }
        if verify_token_algo_lydia(params, settings.ELECTROVANNE_TOKEN):
            # Création Sale
            sale = Sale.objects.create(date=datetime.now(),
                                       sender=user,
                                       recipient=User.objects.get(username="AE_ENSAM"),
                                       operator=user)

            # Création Single product from container
            spfc = SingleProductFromContainer.objects.create(container=container,
                                                             sale=sale,
                                                             quantity=quantity,
                                                             sale_price=(container.product_base.get_moded_price()  /
                                                                         container.product_base.quantity) * int(
                                                                 quantity))
            sale.maj_amount()

            # Création paiement par compte foyer
            d_b = DebitBalance.objects.create(amount=sale.amount,
                                              date=datetime.now(),
                                              sender=sale.sender,
                                              recipient=sale.recipient)
            payment = Payment.objects.create()
            payment.debit_balance.add(d_b)
            payment.save()
            payment.maj_amount()

            sale.payment = payment
            sale.save()

            # Paiement par le client
            sale.payment.debit_balance.all()[0].set_movement()
            data.append(200)
        else:
            data.append(403)

    except ObjectDoesNotExist:
        data.append(0)

    return HttpResponse(json.dumps(data))


def electrovanne_date(request):
    data = [time.time()]
    return HttpResponse(json.dumps(data))


def workboard_treasury(request):
    add_to_breadcrumbs(request, 'Workboard trésoriers')
    return render(request, 'finances/workboard_tresury.html', locals())


class RetrieveMoneyView(ListCompleteView):
    form_class = RetrieveMoneyForm
    template_name = 'finances/retrieve_money.html'
    success_url = '/auth/login'
    attr = {
        'date_begin': now()-timedelta(days=7),
        'date_end': now()+timedelta(days=1),
        'operators': 'all',
        'order_by': 'date',
    }

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste rechargements')
        return super(RetrieveMoneyView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(RetrieveMoneyView, self).get_form_kwargs()
        kwargs['user_list'] = User.objects.filter(
            Q(groups__permissions=Permission.objects.get(codename='supply_account'))
            | Q(user_permissions=Permission.objects.get(codename='supply_account'))).distinct()
        return kwargs

    def get_initial(self):
        initial = super(RetrieveMoneyView, self).get_initial()
        if self.attr['operators'] == 'all':
            initial['all'] = True
        else:
            user_list = list(User.objects.filter(
                Q(groups__permissions=Permission.objects.get(codename='supply_account'))
                | Q(user_permissions=Permission.objects.get(codename='supply_account'))).distinct())
            for u in json.loads(self.attr['operators']):
                initial['field_user_%s' % user_list.index(User.objects.get(pk=u))] = True
        return initial

    def get_context_data(self, **kwargs):
        if self.attr['operators'] != 'all':
            operators = []
            for u in json.loads(self.attr['operators']):
                operators.append(User.objects.get(pk=u))
            self.query = Sale.objects.filter(category='recharging',
                                             date__range=[self.attr['date_begin'], self.attr['date_end']],
                                             operator__in=operators).order_by(self.attr['order_by'])
        else:
            self.query = Sale.objects.filter(category='recharging',
                                             date__range=[self.attr['date_begin'], self.attr['date_end']]).order_by(self.attr['order_by'])

        return super(RetrieveMoneyView, self).get_context_data(**kwargs)

    def form_valid(self, form, **kwargs):

        list_operators_result = []
        operators_list = list(User.objects.filter(
            Q(groups__permissions=Permission.objects.get(codename='supply_account'))
            | Q(user_permissions=Permission.objects.get(codename='supply_account'))).distinct())

        # Cas où "toutes les opérateurs" est coché
        if form.cleaned_data['all'] is True:
            self.attr['operators'] = 'all'
        # Sinon on choisi seulement les opérateurs sélectionnées
        else:
            for i in range(0, len(operators_list)):
                if form.cleaned_data["field_user_%s" % i] is True:
                    list_operators_result.append(operators_list[i])
            list_operators_results_pk = []
            for u in list_operators_result:
                list_operators_results_pk.append(u.pk)
            self.attr['operators'] = json.dumps(list_operators_results_pk)

        self.attr['date_begin'] = form.cleaned_data['date_begin']
        self.attr['date_end'] = form.cleaned_data['date_end']

        return self.render_to_response(self.get_context_data(**kwargs))


class TransfertCreateView(FormView):
    form_class = TransfertCreateForm
    template_name = 'finances/transfert_create.html'
    success_url = '/users/profile/'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Création transfert')
        return super(TransfertCreateView, self).get(request, *args, **kwargs)

    def form_valid(self, form):

        sale_transfert(sender=self.request.user, recipient=User.objects.get(username=form.cleaned_data['recipient']),
                       amount=form.cleaned_data['amount'], date=now(), justification=form.cleaned_data['justification'])

        return super(TransfertCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(TransfertCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


# Supply
class SupplyUnitedView(FormNextView):
    form_class = SupplyUnitedForm
    template_name = 'finances/supply_united.html'
    success_url = '/auth/login'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Rechargement compte')
        return super(SupplyUnitedView, self).get(request, *args, **kwargs)

    def form_valid(self, form):

        # Identification du gestionnaire
        # Le cas d'échec d'authentification est géré dans le form.clean()
        operator = authenticate(username=form.cleaned_data['operator_username'],
                                password=form.cleaned_data['operator_password'])
        sender = User.objects.get(username=form.cleaned_data['sender'])
        payment = []
        if form.cleaned_data['type'] == 'cheque':
            # Obtention du compte en banque
            bank_account = BankAccount.objects.get(
                pk=form.cleaned_data['bank_account'][0:form.cleaned_data['bank_account'].find(' ')])

            cheque = Cheque.objects.create(amount=form.cleaned_data['amount'],
                                           signature_date=form.cleaned_data['signature_date'],
                                           cheque_number=form.cleaned_data['unique_number'],
                                           sender=sender,
                                           recipient=User.objects.get(username='AE_ENSAM'),
                                           bank_account=bank_account)
            payment.append(cheque)

        elif form.cleaned_data['type'] == 'cash':
            cash = Cash.objects.create(sender=sender,
                                       recipient=User.objects.get(username='AE_ENSAM'),
                                       amount=form.cleaned_data['amount'])
            payment.append(cash)

        elif form.cleaned_data['type'] == 'lydia':
            lydia = Lydia.objects.create(date_operation=form.cleaned_data['signature_date'],
                                         id_from_lydia=form.cleaned_data['unique_number'],
                                         sender=sender,
                                         recipient=User.objects.get(username='AE_ENSAM'),
                                         amount=form.cleaned_data['amount'])
            payment.append(lydia)

        sale_recharging(sender=sender, operator=operator, payments_list=payment, date=now(),
                        wording='Rechargement manuel')

        return super(SupplyUnitedView, self).form_valid(form)

    def get_initial(self):
        initial = super(SupplyUnitedView, self).get_initial()
        initial['signature_date'] = now
        initial['operator_username'] = self.request.user.username
        return initial


class ExceptionnalMovementView(FormNextView):
    form_class = ExceptionnalMovementForm
    template_name = 'finances/exceptionnal_movement.html'
    success_url = '/auth/login'

    def form_valid(self, form):

        # Identification du gestionnaire
        # Le cas d'échec d'authentification est géré dans le form.clean()
        operator = authenticate(username=form.cleaned_data['operator_username'],
                                password=form.cleaned_data['operator_password'])

        affected = User.objects.get(username=form.cleaned_data['affected'])
        amount = form.cleaned_data['amount']
        is_credit = False

        if form.cleaned_data['type_movement'] == 'credit':
            is_credit = True

        sale_exceptionnal_movement(operator=operator, affected=affected,
                                   is_credit=is_credit, amount=amount, date=now(),
                                   justification=form.cleaned_data['justification'])

        return super(ExceptionnalMovementView, self).form_valid(form)

    def get_initial(self):
        initial = super(ExceptionnalMovementView, self).get_initial()
        initial['operator_username'] = self.request.user.username
        return initial

class SupplyLydiaSelfView(FormView):
    form_class = SupplyLydiaSelfForm
    template_name = 'finances/lydia_self.html'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Rechargement Lydia auto')
        return super(SupplyLydiaSelfView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SupplyLydiaSelfView, self).get_form_kwargs()
        try:
            kwargs['min_value'] = Setting.objects.get(name='LYDIA_MIN_PRICE').get_value()
        except ObjectDoesNotExist:
            kwargs['min_value'] = 0
        try:
            kwargs['max_value'] = Setting.objects.get(name='LYDIA_MAX_PRICE').get_value()
        except ObjectDoesNotExist:
            kwargs['max_value'] = 1000
        return kwargs

    def form_valid(self, form):
        return get_button_lydia(self.request, form.cleaned_data['amount'], form.cleaned_data['tel_number'])


def get_button_lydia(request, amount, tel_number):

    vendor_token = settings.LYDIA_VENDOR_TOKEN
    confirm_url = settings.LYDIA_CONFIRM_URL
    callback_url = settings.LYDIA_CALLBACK_URL

    amount = amount
    tel_number = tel_number
    message = "Ajout d'argent compte de" + request.user.__str__() + "Borgia AE ENSAM"
    return render(request, 'finances/lydia_self_button.html', locals())


class SupplyLydiaSelfConfirmView(View):
    def get(self, request, *args, **kwargs):
        transaction = self.request.GET.get('transaction')
        order = self.request.GET.get('order_ref')
        return render(request, 'finances/lydia_self_confirm.html', locals())


@csrf_exempt
def supply_lydia_self_callback(request):
    """
    Fonction qui permet de catch le callback de Lydia après un paiement automatique par carte bancaire.
    Crée une vente entre celui qui a envoyé un paiement et l'AE ENSAM. C'est une vente de la catégorie 'rechargement'
    avec comme wording 'rechargement automatique', l'opérateur est l'émetteur du paiement lui-même.
    :param user_pk: en GET. Pk correspondant à l'utilisateur qui a envoyé le paiement.
    :param currency: en POST. Sigle représentant la monnaie utilisée, ex : EUR
    :param request_id: en POST. Id de requete chez Lydia.
    :param amount: en POST. Montant du paiement, dans la monnaie "currency"
    :param signed: en POST. ?
    :param transaction_identifier: en POST. Id de transaction chez Lydia.
    :param vendor_token: en POST. Token de l'AE ENSAM publique.
    :param sig: en POST. Signature générée par Lydia avec l'algorithme Lydia
    :type user_pk: integer strictement positif
    :type currency: chaîne de caractère
    :type request_id: chaîne de caractère
    :type amount: en POST. Montant du paiement, dans la monnaie "currency"
    :type signed: booleen
    :type transaction_identifier: chaîne de caractère
    :type vendor_token: chaîne de caractère
    :type sig: chaîne de caractère

    Remarque : même si certains paramètres ne sont pas utilisés (signed, request_id), ils ne sont pas pour autant optionnels. Ils sont en
    effet utilisés pour vérifié la signature.

    :return:
     Erreur 403 si la signature n'est pas la bonne.
     300 si l'utilisateur n'existe pas dans notre base ou s'il manque un paramètre.
     200 si tout s'est bien passé : la signature est identifiée, la vente créée et l'utilisateur crédité.
    """
    params_dict = {
        "currency": request.POST.get("currency"),
        "request_id": request.POST.get("request_id"),
        "amount": request.POST.get("amount"),
        "signed": request.POST.get("signed"),
        "transaction_identifier": request.POST.get("transaction_identifier"),
        "vendor_token": request.POST.get("vendor_token"),
        "sig": request.POST.get("sig")
    }

    # Verification du token
    if verify_token_algo_lydia(params_dict, settings.LYDIA_API_TOKEN) is True:

        try:
            sale_recharging(sender=User.objects.get(pk=request.GET.get('user_pk')),
                            operator=User.objects.get(pk=request.GET.get('user_pk')),
                            date=now(),
                            wording='Rechargement automatique',
                            payments_list=[Lydia.objects.create(date_operation=now(),
                                                                amount=decimal.Decimal(params_dict['amount']),
                                                                id_from_lydia=params_dict['transaction_identifier'],
                                                                sender=User.objects.get(pk=request.GET.get('user_pk')),
                                                                recipient=User.objects.get(username='AE_ENSAM'))])

        except KeyError or ObjectDoesNotExist:
            return HttpResponse('300')

        return HttpResponse('200')

    else:
        raise PermissionDenied


def bank_account_from_user(request):
    try:
        data = serializers.serialize('json',
                                     BankAccount.objects.filter(owner=User.objects.get(
                                         username=request.GET.get('user_username'))))
        return HttpResponse(data)

    except ObjectDoesNotExist:
        return HttpResponse([])


# Models
class BankAccountCreateView(FormNextView):
    form_class = BankAccountCreateForm
    template_name = 'finances/bank_account_create.html'
    success_url = '/finances/bank_account'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Création compte en banque')
        return super(BankAccountCreateView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        BankAccount.objects.create(owner=User.objects.get(username=form.cleaned_data['owner']),
                                   bank=form.cleaned_data['bank'],
                                   account=form.cleaned_data['account'])
        return super(BankAccountCreateView, self).form_valid(form)


class BankAccountCreateOwnView(FormNextView):
    form_class = BankAccountCreateOwnForm
    template_name = 'finances/bank_account_create.html'
    success_url = '/finances/bank_account'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Création compte en banque')
        return super(BankAccountCreateOwnView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        BankAccount.objects.create(owner=self.request.user,
                                   bank=form.cleaned_data['bank'],
                                   account=form.cleaned_data['account'])
        return super(BankAccountCreateOwnView, self).form_valid(form)


class BankAccountUpdateView(UpdateView):
    model = BankAccount
    fields = ['bank', 'account']
    template_name = 'finances/bank_account_update.html'
    success_url = '/finances/bank_account/'

    def get(self, request, *args, **kwargs):
        if request.user != BankAccount.objects.get(pk=self.kwargs['pk']).owner:
            if request.user.has_perm('finances.change_bankaccount') is False:
                raise PermissionDenied

        add_to_breadcrumbs(request, 'Modification compte en banque')
        return super(BankAccountUpdateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BankAccountUpdateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.request.POST.get('next', self.success_url))
        return context

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))


class BankAccountDeleteView(DeleteView):
    model = BankAccount
    template_name = 'finances/bank_account_delete.html'
    success_url = '/finances/bank_account'

    def get(self, request, *args, **kwargs):
        if request.user != BankAccount.objects.get(pk=self.kwargs['pk']).owner:
            if request.user.has_perm('finances.delete_bankaccount') is False:
                raise PermissionDenied
        add_to_breadcrumbs(request, 'Suppression compte en banque')
        return super(BankAccountDeleteView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BankAccountDeleteView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.request.POST.get('next', self.success_url))
        return context

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))


class BankAccountListView(ListView):
    model = BankAccount
    template_name = "finances/bank_account_list.html"
    queryset = BankAccount.objects.all()

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste comptes en banque')
        return super(BankAccountListView, self).get(request, *args, **kwargs)


class ChequeRetrieveView(DetailView):
    model = Cheque
    template_name = "finances/cheque_retrieve.html"

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Détail chèque')
        return super(ChequeRetrieveView, self).get(request, *args, **kwargs)


class ChequeListView(ListView):
    model = Cheque
    template_name = "finances/cheque_list.html"
    queryset = Cheque.objects.all()

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste chèques')
        return super(ChequeListView, self).get(request, *args, **kwargs)


class CashRetrieveView(DetailView):
    model = Cash
    template_name = "finances/cash_retrieve.html"

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Détail espèces')
        return super(CashRetrieveView, self).get(request, *args, **kwargs)


class CashListView(ListView):
    model = Cash
    template_name = "finances/cash_list.html"
    queryset = Cash.objects.all()

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste espèces')
        return super(CashListView, self).get(request, *args, **kwargs)


class LydiaRetrieveView(DetailView):
    model = Lydia
    template_name = "finances/lydia_retrieve.html"

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Détail virement Lydia')
        return super(LydiaRetrieveView, self).get(request, *args, **kwargs)


class LydiaListView(ListView):
    model = Lydia
    template_name = "finances/lydia_list.html"
    queryset = Lydia.objects.all()

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste virements Lydia')
        return super(LydiaListView, self).get(request, *args, **kwargs)


class SaleRetrieveView(DetailView):
    model = Sale
    template_name = 'finances/sale_retrieve.html'

    def get(self, request, *args, **kwargs):

        # Recherche si l'user est lié à la sale
        is_linked = False
        sale = Sale.objects.get(pk=int(kwargs['pk']))
        if sale.operator == request.user or sale.sender == request.user or sale.recipient == request.user:
            is_linked = True

        for se in sale.list_shared_events()[0]:
            if request.user in se.participants.all():
                is_linked = True

        if request.user.has_perm('finances.retrieve_sale') is False and is_linked is False:
            raise PermissionDenied

        add_to_breadcrumbs(request, 'Détail transaction')
        return super(SaleRetrieveView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SaleRetrieveView, self).get_context_data(**kwargs)
        if self.request.GET.get('for_user') is not None:
            try:
                context['for_user'] = User.objects.get(pk=self.request.GET.get('for_user'))
            except ObjectDoesNotExist:
                pass
        else:
            context['for_user'] = self.request.user
        return context


class SaleListOrganeView(ListView):
    template_name = 'finances/sale_list_organe.html'
    paginate_by = 25
    order_by = '-date'

    def get(self, request, *args, **kwargs):

        if request.GET.get('order_by') is not None:
            self.order_by = request.GET.get('order_by')

        if self.kwargs['organe'] in ['foyer', 'auberge', 'cvis', 'bkars']:
            self.queryset = Sale.objects.filter(category='sale', wording='Vente ' + self.kwargs['organe']).order_by(self.order_by)
            add_to_breadcrumbs(request, 'Liste ventes ' + self.kwargs['organe'])
            return super(SaleListOrganeView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(SaleListOrganeView, self).get_context_data(**kwargs)
        context['organe'] = self.kwargs['organe']
        return context


class SaleListAllView(ListCompleteView):
    form_class = SaleListAllForm
    template_name = 'finances/sale_list_all.html'
    success_url = '/auth/login'
    attr = {
        'date_begin': now() - timedelta(days=14),
        'date_end': now() + timedelta(days=1),
        'category': 'all_categories',
        'order_by': '-date',
    }

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste ventes')
        return super(SaleListAllView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        if self.attr['category'] == 'all_categories':
            self.query = Sale.objects.filter(date__range=[self.attr['date_begin'], self.attr['date_end']])
        else:
            self.query = Sale.objects.filter(date__range=[self.attr['date_begin'], self.attr['date_end']],
                                             category=self.attr['category'])

        self.query = self.query.order_by(self.attr['order_by'])

        return super(SaleListAllView, self).get_context_data(**kwargs)

    def form_valid(self, form, **kwargs):

        self.attr['date_begin'] = form.cleaned_data['date_begin']
        self.attr['date_end'] = form.cleaned_data['date_end']
        self.attr['category'] = form.cleaned_data['category']

        return self.render_to_response(self.get_context_data(**kwargs))


class SaleListLightView(ListView):
    model = Sale
    template_name = "finances/sale_list_light.html"
    queryset = Sale.objects.all()

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Détail transaction light')
        return super(SaleListLightView, self).get(request, *args, **kwargs)


class SharedEventCreateView(FormNextView):
    form_class = SharedEventCreateForm
    template_name = 'finances/shared_event_create.html'
    success_url = '/auth/login'

    def form_valid(self, form):

        se = SharedEvent.objects.create(description=form.cleaned_data['description'],
                                        date=form.cleaned_data['date'],
                                        manager=self.request.user)
        if form.cleaned_data['price']:
            se.price = form.cleaned_data['price']
        if form.cleaned_data['bills']:
            se.bills = form.cleaned_data['bills']
        se.save()

        return super(SharedEventCreateView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Création événement')
        return super(SharedEventCreateView, self).get(request, *args, **kwargs)


def shared_event_registration(request):
    try:
        se = SharedEvent.objects.get(pk=request.GET.get('se_pk'))
        user = User.objects.get(pk=request.GET.get('user_pk'))
        se.registered.add(user)
        se.save()
    except ObjectDoesNotExist:
        pass
    return redirect('/finances/shared_event/list')


class SharedEventManageListView(FormView):
    form_class = SharedEventManageListForm
    template_name = 'finances/shared_event_manage_list.html'
    success_url = '/auth/login'

    def form_valid(self, form, **kwargs):

        date_begin = form.cleaned_data['date_begin']
        date_end = form.cleaned_data['date_end']
        all = form.cleaned_data['all']
        order_by = form.cleaned_data['order_by']
        done = form.cleaned_data['done']
        if done != 'both':

            if done == 'False':
                done = False
            elif done == 'True':
                done = True

            if all is True:
                query_shared_event = SharedEvent.objects.filter(done=done)
            else:
                if date_end is None:
                    query_shared_event = SharedEvent.objects.filter(date__gte=date_begin, done=done)
                else:
                    query_shared_event = SharedEvent.objects.filter(date__range=[date_begin, date_end], done=done)
        else:
            if all is True:
                query_shared_event = SharedEvent.objects.all()
            else:
                if date_end is None:
                    query_shared_event = SharedEvent.objects.filter(date__gte=date_begin)
                else:
                    query_shared_event = SharedEvent.objects.filter(date__range=[date_begin, date_end])
        context = self.get_context_data(**kwargs)
        context['query_shared_event'] = query_shared_event.order_by(order_by)

        return self.render_to_response(context)

    def get_initial(self):
        initial = super(SharedEventManageListView, self).get_initial()
        initial['date_begin'] = now()
        initial['done'] = False
        return initial

    def get_context_data(self, **kwargs):
        context = super(SharedEventManageListView, self).get_context_data(**kwargs)
        context['query_shared_event'] = SharedEvent.objects.filter(date__gte=now(), done=False)
        return context

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste événements pro')
        return super(SharedEventManageListView, self).get(request, *args, **kwargs)


def shared_event_list(request):
    query_shared_event = SharedEvent.objects.filter(done=False).order_by('-date')

    add_to_breadcrumbs(request, 'Liste événements')
    return render(request, 'finances/shared_event_list.html', locals())


class SharedEventManageView(View):
    template_name = 'finances/shared_event_manage.html'
    # TODO: bouton pour supprimer l'event

    def get_query_user(self, state):
        se = SharedEvent.objects.get(pk=self.kwargs['pk'])
        if state == 'participants':
            return se.list_of_participants_ponderation()
        elif state == 'registered':
            return se.list_of_registered_ponderation()

    @staticmethod
    def get_key(item, order_by):
        return getattr(item, order_by)

    def get(self, request, *args, **kwargs):

        # Variables
        se = SharedEvent.objects.get(pk=self.kwargs['pk'])
        state = ''
        query_user = []
        initial_list_user_form = {}
        payment_error = ''

        # Vérification des permissions
        # Si on a la perm on peut voir toujours (mais plus tout faire, cf les autres fonctions)
        # Si on est juste manager, on ne peux plus voir si done=True
        if request.user.has_perm('finances.manage_sharedevent') is False:
            if request.user == se.manager:
                if se.done:
                    raise PermissionDenied

        # Si on impose un state directement en GET (en venant d'un lien remove par exemple)
        if self.request.GET.get('state') is not None:
            if self.request.GET.get('state') == 'participants':
                initial_list_user_form = {
                    'state': 'participants',
                    'order_by': 'last_name',
                }
                query_user = sorted(self.get_query_user('participants'), key=lambda item: getattr(item[0], 'last_name'))
                state = 'participants'
            elif self.request.GET.get('state') == 'registered':
                initial_list_user_form = {
                    'state': 'registered',
                    'order_by': 'last_name',
                }
                query_user = sorted(self.get_query_user('registered'), key=lambda item: getattr(item[0], 'last_name'))
                state = 'registered'

        # Sinon on choisit en fonction de la date de l'event
        # S'il est passé, on liste les participants par défaut, sinon on liste les inscrits
        else:
            initial_list_user_form = {
                'state': 'participants',
                'order_by': 'last_name',
            }
            query_user = sorted(self.get_query_user('participants'), key=lambda item: getattr(item[0], 'last_name'))
            state = 'participants'

        initial_update_form = {
            'price': se.price,
            'bills': se.bills,
        }

        if request.GET.get('payment_error') == 'True':
            payment_error = 'Veuillez renseigner le prix de l\'événement ! '

        # Création des forms
        list_user_form = SharedEventManageUserListForm(prefix='list_user_form', initial=initial_list_user_form)
        update_form = SharedEventManageUpdateForm(prefix='update_form', initial=initial_update_form)
        upload_json_form = SharedEventManageUploadJSONForm(prefix='upload_json_form')
        add_user_form = SharedEventManageAddForm(prefix='add_user_form')
        download_xlsx_form = SharedEventManageDownloadXlsxForm(prefix='download_xlsx_form',
                                                               list_year=list_year())

        context = {
            'pk': self.kwargs['pk'],
            'list_user_form':    list_user_form,
            'upload_json_form': upload_json_form,
            'update_form': update_form,
            'add_user_form': add_user_form,
            'download_xlsx_form': download_xlsx_form,
            'query_user': query_user,
            'errors': 0,
            'state': state,
            'order_by': 'last_name',
            'done': se.done,
            'payment_error': payment_error,
            'next': request.GET.get('next')
        }

        add_to_breadcrumbs(request, 'Gestion événement')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        # Variables
        se = SharedEvent.objects.get(pk=self.kwargs['pk'])
        errors = 0
        state = request.POST.get('state')
        order_by = request.POST.get('order_by')
        query_user = sorted(self.get_query_user(state), key=lambda item: getattr(item[0], order_by))

        # Liaison des forms et détermination du form qui a été submited
        initial_update_form = {
            'price': se.price,
            'bills': se.bills,
        }
        initial_list_user_form = {
            'state': state,
            'order_by': order_by
        }
        list_user_form = SharedEventManageUserListForm(prefix='list_user_form', initial=initial_list_user_form)
        update_form = SharedEventManageUpdateForm(prefix='update_form', initial=initial_update_form)
        upload_json_form = SharedEventManageUploadJSONForm(prefix='upload_json_form')
        add_user_form = SharedEventManageAddForm(prefix='add_user_form')
        download_xlsx_form = SharedEventManageDownloadXlsxForm(prefix='download_xlsx_form',
                                                               list_year=list_year())
        action = self.request.POST['action']

        # Si form list_user_form
        if action == 'list_user':
            list_user_form = SharedEventManageUserListForm(request.POST, prefix='list_user_form')
            if list_user_form.is_valid():
                if list_user_form.cleaned_data['state'] == 'participants':
                    query_user = self.get_query_user('participants')
                    state = 'participants'
                if list_user_form.cleaned_data['state'] == 'registered':
                    query_user = self.get_query_user('registered')
                    state = 'registered'
                order_by = list_user_form.cleaned_data['order_by']
                query_user = sorted(query_user, key=lambda item: getattr(item[0], order_by))

        # Si form update
        if action == 'update':
            update_form = SharedEventManageUpdateForm(request.POST, prefix='update_form')
            if update_form.is_valid():
                se.price = update_form.cleaned_data['price']
                se.bills = update_form.cleaned_data['bills']
                se.save()

        # Si form upload_json
        elif action == 'upload_json':
            upload_json_form = SharedEventManageUploadJSONForm(request.POST, request.FILES,  prefix='upload_json_form')
            if upload_json_form.is_valid():
                lists = list_user_ponderation_errors_from_list(request.FILES['upload_json_form-file'],
                                                               upload_json_form.cleaned_data['token'])
                # Enregistrement des participants/inscrits et des pondérations
                if upload_json_form.cleaned_data['state'] == 'participants':
                    for i, u in enumerate(lists[0]):
                        try:
                            if lists[1][i] > 0:
                                se.add_participant(u, lists[1][i])
                        except KeyError:
                            pass
                else:
                    for u in lists[0]:
                        se.registered.add(u)
                se.save()

                errors = len(lists[2])
                query_user = self.get_query_user(state)

        elif action == 'add_user':
            add_user_form = SharedEventManageAddForm(request.POST, prefix='add_user_form')
            if add_user_form.is_valid():
                if add_user_form.cleaned_data['state'] == 'registered':
                    se.registered.add(User.objects.get(username=add_user_form.cleaned_data['username']))
                    se.save()
                elif add_user_form.cleaned_data['state'] == 'participant':
                    se.add_participant(User.objects.get(username=add_user_form.cleaned_data['username']),
                                       add_user_form.cleaned_data['ponderation'])
                query_user = self.get_query_user(state)

        elif action == 'download_xlsx':
            download_xlsx_form = SharedEventManageDownloadXlsxForm(request.POST, prefix='download_xlsx_form', list_year=list_year())
            if download_xlsx_form.is_valid():

                # Initialisation du fichier excel
                workbook, worksheet, response = workboot_init(se.__str__(), 'Feuil1.XLSM_to_JSON',
                                                              'Générer le fichier JSON')

                # Ajout de l'entête de la table
                worksheet_write_line(workbook=workbook, worksheet=worksheet,
                                     data=[['Nom prénom', 'Bucque', 'Username', 'Pondération']],
                                     bold=True)

                if download_xlsx_form.cleaned_data['state'] == 'year':
                    # Ajout des valeurs
                    list_year_result = []
                    data = []
                    for i in range(0, len(list_year())):
                        if download_xlsx_form.cleaned_data["field_year_%s" % i] is True:
                            list_year_result.append(list_year()[i])
                    for u in User.objects.filter(year__in=list_year_result).exclude(groups=Group.objects.get(pk=14)).order_by('last_name'):
                        data.append([u.last_name + ' ' + u.first_name, u.surname, u.username])
                    worksheet_write_line(workbook=workbook, worksheet=worksheet, data=data, init_row=1)
                    workbook.close()
                    return response

                elif download_xlsx_form.cleaned_data['state'] == 'participants':
                    data = []
                    for e in se.list_of_participants_ponderation():
                        u = e[0]
                        data.append([u.last_name + ' ' + u.first_name, u.surname, u.username, e[1]])
                    worksheet_write_line(workbook=workbook, worksheet=worksheet, data=data, init_row=1)
                    workbook.close()
                    return response

                elif download_xlsx_form.cleaned_data['state'] == 'registered':
                    data = []
                    for e in se.list_of_registered_ponderation():
                        u = e[0]
                        data.append([u.last_name + ' ' + u.first_name, u.surname, u.username, e[1]])
                    worksheet_write_line(workbook=workbook, worksheet=worksheet, data=data, init_row=1)
                    workbook.close()
                    return response

        context = {
            'pk': self.kwargs['pk'],
            'list_user_form': list_user_form,
            'upload_json_form': upload_json_form,
            'update_form': update_form,
            'add_user_form': add_user_form,
            'download_xlsx_form': download_xlsx_form,
            'query_user': query_user,
            'errors': errors,
            'state': state,
            'order_by': order_by,
            'done': se.done,
            'next': request.POST.get('next'),
        }

        return render(request, 'finances/shared_event_manage.html', context)


class SetPriceProductBaseView(FormView):
    template_name = 'finances/product_base_price.html'
    form_class = SetPriceProductBaseForm

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Modification prix produit')
        return super(SetPriceProductBaseView, self).get(request, *args, **kwargs)

    def get_initial(self):
        product_base = ProductBase.objects.get(pk=self.kwargs['pk'])
        initial = super(SetPriceProductBaseView, self).get_initial()
        initial['is_manual'] = product_base.is_manual
        initial['manual_price'] = product_base.manual_price
        return initial

    def get_context_data(self, **kwargs):
        context = super(SetPriceProductBaseView, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['product_base'] = ProductBase.objects.get(pk=self.kwargs['pk'])
        try:
            context['margin_profit'] = Setting.objects.get(name='MARGIN_PROFIT').get_value()
        except ObjectDoesNotExist:
            pass
        return context

    def form_valid(self, form):
        product_base = ProductBase.objects.get(pk=self.kwargs['pk'])
        product_base.is_manual = form.cleaned_data['is_manual']
        product_base.manual_price = form.cleaned_data['manual_price']
        product_base.save()
        return redirect('url_set_price_product_base', pk=self.kwargs['pk'])


# Autres
def remove_participant_se(request, pk):
    se = SharedEvent.objects.get(pk=pk)

    # Même en ayant la permission, on ne modifie plus une event terminé
    if request.user != se.manager and request.user.has_perm('finances.manage_sharedevent') is False:
        raise PermissionDenied
    elif se.done is True:
        raise PermissionDenied

    try:
        user_pk = request.GET.get('user_pk')
        if user_pk == 'ALL':
            for u in se.participants.all():
                se.remove_participant(u)
        else:
            se.remove_participant(User.objects.get(pk=user_pk))
    except ObjectDoesNotExist:
        pass
    return redirect('/finances/shared_event/manage/' + str(se.pk) + '/?state=participants#table_users')


def remove_registered_se(request, pk):
    se = SharedEvent.objects.get(pk=pk)

    if request.user != se.manager and request.user.has_perm('finances.manage_sharedevent') is False:
        raise PermissionDenied
    # Même en ayant la permission, on ne modifie plus une event terminé
    elif se.done is True:
        raise PermissionDenied
    # Si la date est passé et que le payment n'est pas fait, on ne modifie plus les inscrits
    elif datetime.date(now()) > se.date:
        raise PermissionDenied

    try:
        user_pk = request.GET.get('user_pk')
        if user_pk == 'ALL':
            for u in se.registered.all():
                se.registered.remove(u)
            se.save()
        else:
            se.registered.remove(User.objects.get(pk=user_pk))
            se.save()
    except ObjectDoesNotExist:
        pass
    return redirect('/finances/shared_event/manage/' + str(se.pk) + '/?state=registered#table_users')


def proceed_payment_se(request, pk):
    se = SharedEvent.objects.get(pk=pk)
    if se.done is True:
        raise PermissionDenied
    if se.price is not None:
        se.pay(request.user, User.objects.get(username='AE_ENSAM'))
        return redirect('url_manage_shared_event', pk=se.pk)
    else:
        return redirect('/finances/shared_event/manage/' + str(se.pk) + '/?payment_error=True')


def change_ponderation_se(request, pk):
    """
    Change la valeur de la pondération d'un participant user pour un événement
    Permissions :   Si événements terminé -> denied,
                    Si pas manager ou pas la perm 'finances.manage_sharedevent' -> denied
    :param pk: pk de l'événement
    :param user_pk: paramètre GET correspondant au pk de l'user
    :param pond_pk: paramètre GET correspondant à la nouvelle pondération
    :type pk, user_pk, pond_pk: int
    """


    try:
        # Variables d'entrées
        se = SharedEvent.objects.get(pk=pk)
        user = User.objects.get(pk=request.GET.get('user_pk'))
        pond = int(request.GET.get('pond'))

        # Permission
        if request.user != se.manager and request.user.has_perm('finances.manage_sharedevent') is False:
            raise PermissionDenied
        # Même en ayant la permission, on ne modifie plus une event terminé
        elif se.done is True:
            raise PermissionDenied

        if pond > 0:
            # Changement de la pondération
            se.remove_participant(user)
            se.add_participant(user, pond)

            # Réponse
            response = pond
        else:
            response = 0

    except KeyError:
        response = 0
    except ObjectDoesNotExist:
        response = 0
    except ValueError:
        response = 0

    return HttpResponse(response)


def list_base_ponderation_from_file(f):

    # Traitement sur le string pour le convertir en liste identifiable json
    initial = str(f.read())
    data_string = initial[2:len(initial)]
    data_string = data_string[0:len(data_string)-1]
    data_string = data_string.replace('\\n', '')

    # Gestion des erreurs si le fichier contient du blanc après les données
    data_string = data_string[0:data_string.rfind(']')+1]

    # Conversion json
    data = json.loads(data_string)

    # Lecture json
    list_base = []
    list_ponderation = []
    for dual in data:
        list_base.append(dual[0])
        list_ponderation.append(dual[1])
    return list_base, list_ponderation


def list_user_ponderation_errors_from_list(f, token):

    if token == 'True':
        token = True
    else:
        token = False

    list_base_ponderation = list_base_ponderation_from_file(f)

    list_user = []
    list_ponderation = []
    list_error = []

    for i, b in enumerate(list_base_ponderation[0]):

        # Si le fichier contient des numéros de jetons
        if token is True:
            try:
                list_user.append(User.objects.get(token_id=b))
                list_ponderation.append(list_base_ponderation[1][i])
            except ObjectDoesNotExist:
                list_error.append([b, list_base_ponderation[1][i]])

        # Si le fichier contient des usernames
        else:
            try:
                list_user.append(User.objects.get(username=b))
                list_ponderation.append(list_base_ponderation[1][i])
            except ObjectDoesNotExist:
                list_error.append([b, list_base_ponderation[1][i]])

    return list_user, list_ponderation, list_error, list_base_ponderation


def worksheet_write_line(workbook, worksheet, data, bold=False, init_column=0, init_row=0):
    """
    Ecrit dans worksheet une ligne par i dans data.
    Par exemple :
    data = [[user1, 1], [user2, 2]]
    Ecrit deux lignes [user1, 1] et [user2, 2] dans deux colonnes.
    Procède à l'autofit
    :param workbook: class workboot de xlsxwriter
    :param data: liste de lignes
    :param worksheet: class worksheet de xlsxwriter
    :param bold: Si vrai, les lignes sont en gras
    :param init_column: index où commencer à écrire
    :param init_row: index où commencer à écrire
    """

    col = init_column
    row = init_row
    max_width = [len('Nom Prénom'), len('Bucque'), len('Username'), len('Pondération')]

    for line in data:
        # Ecriture de la ligne
        worksheet.write_row(row, col, line, workbook.add_format({'bold': bold}))
        row += 1
        # Recherche de la taille max pour autofit
        for i, c in enumerate(line):
            try:
                if len(str(c)) > max_width[i]:
                    max_width[i] = len(str(c))
            except TypeError:  # Cas où ce n'est pas un élément convertissable en string
                pass

    # Application de l'autofit
    for i in range(0, len(max_width)):
        worksheet.set_column(i, i, max_width[i]+2)


def workboot_init(workbook_name, macro=None, button_caption=None):
    """
    Initialise le fichier Excel, avec ou sans macro (une macro max)
    :param workbook_name: string, nom à appliquer au fichier xl
    :param macro: string, nom de la macro à appliquer
    :param button_caption, string, valeur du bouton à lier à la macro
    :return workbook, worksheet
    """

    # Cas où une macro est ajouté, fichier xlxm
    if macro is not None:
        response = HttpResponse(content_type='text/xlsm')
        response['Content-Disposition'] = 'attachment; filename="' + workbook_name + '.xlsm"'
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})  # Stocké dans la RAM
        workbook.add_vba_project('vbaProject.bin')  # Ajout de la macro
        worksheet = workbook.add_worksheet()
        print(len(button_caption))
        worksheet.insert_button('F3', {'macro': macro,  # Ajout d'un bouton pour la macro
                                       'caption': button_caption,
                                       'width': len(button_caption)*10,
                                       'height': 30})
    # Cas où pas de macro, fichier xlsx
    else:
        response = HttpResponse(content_type='text/xlsx')
        response['Content-Disposition'] = 'attachment; filename="' + workbook_name + '.xlsx"'
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})  # Stocké dans la RAM
        worksheet = workbook.add_worksheet()

    # Set des noms du workbook et de la sheet
    # Doit être les mêmes que sur la macro, s'il y en a une. Permet d'éviter les problèmes des différentes versions.
    workbook.set_vba_name('ThisWorkbook')
    worksheet.set_vba_name('Feuil1')

    return workbook, worksheet, response


def verify_token_algo_lydia(params, token):
    """
    Fonction qui renvoie Vrai si la requete est valide, c'est à dire si l'algorithme vérifie que la signature est valide
    C'est qu'elle est basé sur le bon algorithme, et le bon token
    :param params: dictionnaire des param  tres avec sig dedans
    :param token: token à comparer
    """
    # FONCTION TESTEE ET VALIDEE AVEC REQUESTBIN
    try:
        # G  n  ration de l'hypoth  tique signature
        sig = params['sig']
        del params['sig']
        h_sig_table = []
        # Trie par ordre alphab  tique des noms de param  tres
        sorted_params = sorted(params.items(), key=operator.itemgetter(0))
        # Concat  nation des param  tres et des valeurs
        for p in sorted_params:
            h_sig_table.append(p[0] + '=' + p[1])
        h_sig = '&'.join(h_sig_table)
        # Ajout du token api
        h_sig += '&' + token  # Ce token est priv
        # Hash md5
        h_sig_hash = hashlib.md5(h_sig.encode())
        return h_sig_hash.hexdigest() == sig

    except KeyError:
        return False


# Obsolète
def raw_body_lydia_to_dict(s):
    # Suppression des caract  res issus de la conversion bytes -> string
    s = s[3: len(s) - 1]
    s = s.replace('\\n', '')
    s = s.replace('\\r', '')

    # Identification token csrf et suppression des occurences
    token_csrf = s[0: s.find('Content-Disposition: form-data;')]
    s = s.replace(token_csrf, '')

    # Identification des param  tres et des valeurs
    # du type string : "nom_param  tres"valeur
    params_string = []
    sep = "Content-Disposition: form-data; name="
    l = len(sep)

    for p in range(0, s.count(sep)):
        s = s[l: len(s)]
        if s.find(sep):
            params_string.append(s[0: s.find(sep) - 1])
            s = s[s.find(sep): len(s)]
        else:
            params_string.append(s[0, len(s)])

    # Cr  ation du dictionnaire de param  tres
    params_dict = {}
    for p in params_string:
        params_dict[p[1:p.find('"', 1)]] = p[p.find('"', 1) + 1:len(p)]

    # Correction pour sig
    try:
        params_dict['sig'] = params_dict['sig'][0: len(params_dict['sig']) - 1]
    except KeyError:
        pass

    return params_dict
