#-*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse, force_text, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Permission
from django.db.models import Q
from datetime import datetime
import json, time, re

from finances.forms import *
from finances.models import *
from shops.models import Container
from users.models import user_from_token_tap


def electrovanne_request1(request):
    data = []
    try:
        # Variables
        container = Container.objects.get(place='tireuse %s' % request.GET.get('tireuse_pk'))
        id = request.GET.get('id')
        user = user_from_token_tap(request.GET.get('token_pk'))

        # Quantité max possible
        if user.balance <= 0:
            max_quantity = 0
        else:
            max_quantity = round(float((container.product_base.quantity * user.balance) / container.product_base.calculated_price), 0)

        # Ecriture de la liste
        data.append(request.GET.get('token_pk'))
        data.append(request.GET.get('tireuse_pk'))
        data.append(id)
        data.append(max_quantity)

    except ObjectDoesNotExist:
        data.append('error0')

    return HttpResponse(json.dumps(data))


def electrovanne_request2(request):

    try:
        # Variables (id inutile pour nous)
        container = Container.objects.get(place='tireuse %s' % request.GET.get('tireuse_pk'))
        user = user_from_token_tap(request.GET.get('token_pk'))
        quantity = request.GET.get('quantity')

        # Création Sale
        sale = Sale.objects.create(date=datetime.now(),
                                   sender=user,
                                   recipient=User.objects.get(username="AE_ENSAM"),
                                   operator=user)

        # Création Single product from container
        spfc = SingleProductFromContainer.objects.create(container=container,
                                                         sale=sale,
                                                         quantity=quantity,
                                                         sale_price=(container.product_base.calculated_price /
                                                                     container.product_base.quantity) * int(quantity))
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

        return HttpResponse('200')

    except ObjectDoesNotExist:
        return HttpResponse('0')


def electrovanne_date(request):
    data = [time.time()]
    return HttpResponse(json.dumps(data))


def workboard_treasury(request):

    return render(request, 'finances/workboard_tresury.html', locals())


class RetrieveMoneyView(FormView):
    form_class = RetrieveMoneyForm
    template_name = 'finances/retrieve_money.html'
    success_url = '/auth/login'

    def get_form_kwargs(self):
        kwargs = super(RetrieveMoneyView, self).get_form_kwargs()
        kwargs['user_list'] = User.objects.filter(
            Q(groups__permissions=Permission.objects.get(codename='supply_account'))
            | Q(user_permissions=Permission.objects.get(codename='supply_account'))).distinct()
        return kwargs

    def form_valid(self, form, **kwargs):

        user_list = User.objects.filter(
            Q(groups__permissions=Permission.objects.get(codename='supply_account'))
            | Q(user_permissions=Permission.objects.get(codename='supply_account'))).distinct()
        list_user_result = []
        for i in range(0, len(user_list)):
            list_user_result.append((form.cleaned_data["field_user_%s" % i], user_list[i]))

        date_begin = form.cleaned_data['date_begin']
        date_end = form.cleaned_data['date_end']

        query_supply = Sale.objects.none()
        for e in list_user_result:
            if e[0] != 0:
                query_supply = query_supply | Sale.objects.filter(singleproductfromcontainer__container=Container.objects.get(
                    product_base__product_unit__name='Argent fictif'), operator=e[1],
                    date__range=[date_begin, date_end])

        # Enlever les transferts
        for e in query_supply:
            if e.payment.list_debit_balance()[1] != 0:
                query_supply = query_supply.exclude(pk=e.pk)

        context = self.get_context_data(**kwargs)
        context['query_supply'] = query_supply.order_by(form.cleaned_data['order_by'])
        return self.render_to_response(context)


class TransfertCreateView(FormView):
    form_class = TransfertCreateForm
    template_name = 'finances/transfert_create.html'
    success_url = '/users/profile'

    def form_valid(self, form):

        # Création du virement par compte foyer
        debit_balance = DebitBalance(amount=form.cleaned_data['amount'],
                                     sender=self.request.user,
                                     recipient=User.objects.get(username=form.cleaned_data['recipient']))
        debit_balance.save()

        # Création du paiement
        payment = Payment()
        payment.save()
        payment.debit_balance.add(debit_balance)
        payment.maj_amount()
        payment.save()

        # Création de la vente
        sale = Sale(date=datetime.now(),
                    sender=self.request.user,
                    operator=self.request.user,
                    recipient=User.objects.get(username=form.cleaned_data['recipient']),
                    payment=payment)
        sale.save()

        # Création d'un spfc d'argent fictif
        spfc = SingleProductFromContainer(container=Container.objects.get(
            product_base__product_unit__name='Argent fictif'), quantity=payment.amount*100,
            sale_price=payment.amount, sale=sale)
        spfc.save()

        # Mise à jour des comptes foyer
        sale.maj_amount()
        sale.save()
        self.request.user.debit(sale.amount)
        self.request.user.save()
        User.objects.get(username=form.cleaned_data['recipient']).credit(sale.amount)
        User.objects.get(username=form.cleaned_data['recipient']).save()

        return super(TransfertCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(TransfertCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


# Supply
class SupplyUnitedView(FormView):
    form_class = SupplyUnitedForm
    template_name = 'finances/supply_united.html'
    success_url = '/auth/login'

    def form_valid(self, form):

        # Identification du gestionnaire
        # Le cas d'échec d'authentification est géré dans le form.clean()
        operator = authenticate(username=form.cleaned_data['operator_username'],
                                password=form.cleaned_data['operator_password'])
        sender = User.objects.get(username=form.cleaned_data['sender'])
        # Création du paiement
        payment = Payment.objects.create()

        if form.cleaned_data['type'] == 'cheque':

            cheque = Cheque.objects.create(amount=form.cleaned_data['amount'],
                                           signature_date=form.cleaned_data['signature_date'],
                                           cheque_number=form.cleaned_data['unique_number'],
                                           sender=sender,
                                           recipient=User.objects.get(username='AE_ENSAM'),
                                           bank_account=form.cleaned_data['bank_account'])
            payment.cheques.add(cheque)
            payment.maj_amount()
            payment.save()

        elif form.cleaned_data['type'] == 'cash':
            cash = Cash.objects.create(sender=sender,
                                       recipient=User.objects.get(username='AE_ENSAM'),
                                       amount=form.cleaned_data['amount'])
            payment.cashs.add(cash)
            payment.maj_amount()
            payment.save()

        elif form.cleaned_data['type'] == 'lydia':
            lydia = Lydia.objects.create(date_operation=form.cleaned_data['signature_date'],
                                         id_from_lydia=form.cleaned_data['unique_number'],
                                         sender_user_id=sender,
                                         recipient_user_id=User.objects.get(username='AE_ENSAM'),
                                         amount=form.cleaned_data['amount'])
            payment.lydias.add(lydia)
            payment.maj_amount()
            payment.save()

        # Création de la vente
        sale = Sale.objects.create(date=datetime.now(),
                                   sender=sender,
                                   operator=operator,
                                   recipient=User.objects.get(username='AE_ENSAM'),
                                   payment=payment)

        # Création d'un spfc d'argent fictif
        spfc = SingleProductFromContainer.objects.create(container=Container.objects.get(
            product_base__product_unit__name='Argent fictif'), quantity=payment.amount*100,
            sale_price=payment.amount, sale=sale)

        # Mise à jour du compte foyer du client
        sale.maj_amount()
        sale.save()
        sender.credit(sale.amount)

        return super(SupplyUnitedView, self).form_valid(form)

    def get_initial(self):
        initial = super(SupplyUnitedView, self).get_initial()
        initial['signature_date'] = now
        return initial

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(SupplyUnitedView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


def bank_account_from_user(request):
    data = serializers.serialize('xml',
                                 BankAccount.objects.filter(owner=User.objects.get(
                                     username=request.GET.get('user_username'))))
    return HttpResponse(data)


# Models
class BankAccountCreateView(CreateView):
    model = BankAccount
    fields = ['bank', 'account', 'owner']
    template_name = 'finances/bank_account_create.html'
    success_url = '/finances/bank_account'

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(BankAccountCreateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


class BankAccountUpdateView(UpdateView):
    model = BankAccount
    fields = ['bank', 'account', 'owner']
    template_name = 'finances/bank_account_update.html'
    success_url = '/finances/bank_account/'


class BankAccountDeleteView(DeleteView):
    model = BankAccount
    template_name = 'finances/bank_account_delete.html'
    success_url = '/finances/bank_account'


class BankAccountListView(ListView):
    model = BankAccount
    template_name = "finances/bank_account_list.html"
    queryset = BankAccount.objects.all()


class ChequeRetrieveView(DetailView):
    model = Cheque
    template_name = "finances/cheque_retrieve.html"


class ChequeListView(ListView):
    model = Cheque
    template_name = "finances/cheque_list.html"
    queryset = Cheque.objects.all()


class CashRetrieveView(DetailView):
    model = Cash
    template_name = "finances/cash_retrieve.html"


class CashListView(ListView):
    model = Cash
    template_name = "finances/cash_list.html"
    queryset = Cash.objects.all()


class LydiaRetrieveView(DetailView):
    model = Lydia
    template_name = "finances/lydia_retrieve.html"


class LydiaListView(ListView):
    model = Lydia
    template_name = "finances/lydia_list.html"
    queryset = Lydia.objects.all()


class SaleRetrieveView(DetailView):
    model = Sale
    template_name = 'finances/sale_retrieve.html'

    def get(self, request, *args, **kwargs):

        # Recherche si l'user est lié à la sale
        is_linked = False
        sale = Sale.objects.get(pk=int(kwargs['pk']))
        if sale.operator == request.user or sale.sender == request.user or sale.recipient == request.user:
            is_linked = True

        if request.user.has_perm('finances.retrieve_sale') is False and is_linked is False:
            raise PermissionDenied

        return super(SaleRetrieveView, self).get(request, *args, **kwargs)


class SaleListView(ListView):
    model = Sale
    template_name = "finances/sale_list.html"
    queryset = Sale.objects.all()


class SaleListLightView(ListView):
    model = Sale
    template_name = "finances/sale_list_light.html"
    queryset = Sale.objects.all()


class SharedEventCreateView(FormView):
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

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(SharedEventCreateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


def shared_event_registration(request):
    try:
        se = SharedEvent.objects.get(pk=request.GET.get('se_pk'))
        user = User.objects.get(pk=request.GET.get('user_pk'))
        se.registered.add(user)
        se.save()
    except ObjectDoesNotExist:
        pass
    return redirect('/finances/shared_event/list')


class SharedEventUpdateView(FormView):
    form_class = SharedEventUpdateForm
    template_name = 'finances/shared_event_update.html'
    success_url = '/auth/login'

    def form_valid(self, form):

        se = SharedEvent.objects.get(pk=self.request.POST.get('pk'))

        lists = list_user_ponderation_errors_from_list(self.request.FILES['file'])

        # Ajout des participants avec leur pondération
        for u in lists[0]:
            se.participants.add(u)
        se.set_ponderation(lists[1])
        se.save()

        # Ajout des informations prix et factures
        se.price = form.cleaned_data['price']
        se.bills = form.cleaned_data['bills']
        se.save()

        # Paiement par les participants (et erreurs ou non)
        se.pay(self.request.user, User.objects.get(username='AE_ENSAM'), form.cleaned_data['managing_errors'], lists[2])

        return super(SharedEventUpdateView, self).form_valid(form)

    def get_initial(self):
        initial = super(SharedEventUpdateView, self).get_initial()
        se = SharedEvent.objects.get(pk=self.request.GET.get('pk', self.request.POST.get('pk')))
        if se.price is not None:
            initial['price'] = se.price
        if se.bills is not None:
            initial['bills'] = se.bills
        return initial

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, *args, **kwargs):
        context = super(SharedEventUpdateView, self).get_context_data(**kwargs)
        context['pk'] = self.request.GET.get('pk')
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


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


def shared_event_list(request):
    query_shared_event = SharedEvent.objects.filter(done=False).order_by('-date')
    return render(request, 'finances/shared_event_list.html', locals())


def list_token_ponderation_from_file(f):

    # Traitement sur le string pour le convertir en liste identifiable json
    initial = str(f.read())
    data_string = initial[2:len(initial)]
    data_string = data_string[0:len(data_string)-3]
    data_string = data_string.replace('\\n', '')

    # Conversion json
    data = json.loads(data_string)

    # Lecture json
    list_token = []
    list_ponderation = []
    for dual in data:
        list_token.append(dual[0])
        list_ponderation.append(dual[1])
    return list_token, list_ponderation


def list_user_ponderation_errors_from_list(f):
    list_token_ponderation = list_token_ponderation_from_file(f)

    list_user = []
    list_ponderation = []
    list_error = []

    for i, t in enumerate(list_token_ponderation[0]):
        try:
            list_user.append(User.objects.get(token_id=t))
            list_ponderation.append(list_token_ponderation[1][i])
        except ObjectDoesNotExist:
            list_error.append([t, list_token_ponderation[1][i]])

    return list_user, list_ponderation, list_error, list_token_ponderation
