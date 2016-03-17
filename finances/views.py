#-*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse, force_text
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView
from django.core import serializers
from django.core.exceptions import PermissionDenied
from datetime import datetime
import json, time

from finances.forms import *
from finances.models import *
from shops.models import Container


def electrovanne_request1(request):
    data = []
    try:
        # Variables
        user = User.objects.get(pk=request.GET.get('user_pk'))
        container = Container.objects.get(place='tireuse %s' % request.GET.get('tireuse_pk'))
        id = request.GET.get('id')

        # Quantité max possible
        if user.balance <= 0:
            max_quantity = 0
        else:
            max_quantity = round(float((container.product_base.quantity * user.balance) / container.product_base.calculated_price), 0)

        # Ecriture de la liste
        data.append(request.GET.get('user_pk'))
        data.append(request.GET.get('tireuse_pk'))
        data.append(id)
        data.append(max_quantity)

    except ObjectDoesNotExist:
        data.append('error0')

    return HttpResponse(json.dumps(data))


def electrovanne_request2(request):
    return


def electrovanne_date(request):
    data = [time.time()]
    return HttpResponse(json.dumps(data))


def workboard_treasury(request):

    return render(request, 'finances/workboard_tresury.html', locals())


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
class SupplyChequeView(FormView):
    form_class = SupplyChequeForm
    template_name = 'finances/supply_cheque.html'
    success_url = '/auth/login'

    def form_valid(self, form):

        # Identification du gestionnaire
        # Le cas d'échec d'authentification est géré dans le form.clean()
        operator = authenticate(username=form.cleaned_data['operator_username'],
                                password=form.cleaned_data['operator_password'])

        # Création du chèque
        cheque = Cheque(amount=form.cleaned_data['amount'],
                        signature_date=form.cleaned_data['signature_date'],
                        cheque_number=form.cleaned_data['cheque_number'],
                        sender=form.cleaned_data['sender'],
                        recipient=User.objects.get(username='AE_ENSAM'),
                        bank_account=form.cleaned_data['bank_account'])
        cheque.save()

        # Création du paiement
        payment = Payment()
        payment.save()
        payment.cheques.add(cheque)
        payment.maj_amount()
        payment.save()

        # Création de la vente
        sale = Sale(date=datetime.now(),
                    sender=form.cleaned_data['sender'],
                    operator=operator,
                    recipient=User.objects.get(username='AE_ENSAM'),
                    payment=payment)
        sale.save()

        # Création d'un spfc d'argent fictif
        spfc = SingleProductFromContainer(container=Container.objects.get(
            product_base__product_unit__name='Argent fictif'), quantity=payment.amount*100,
            sale_price=payment.amount, sale=sale)
        spfc.save()

        # Mise à jour du compte foyer du client
        sale.maj_amount()
        sale.save()
        sender = form.cleaned_data['sender']
        sender.credit(sale.amount)

        return super(SupplyChequeView, self).form_valid(form)

    def get_initial(self):
        initial = super(SupplyChequeView, self).get_initial()
        initial['signature_date'] = now
        return initial

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(SupplyChequeView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


class SupplyCashView(FormView):
    form_class = SupplyCashForm
    template_name = 'finances/supply_cash.html'
    success_url = '/auth/login'

    def form_valid(self, form):

        # Identification du gestionnaire
        # Le cas d'échec d'authentification est géré dans le form.clean()
        operator = authenticate(username=form.cleaned_data['operator_username'],
                                password=form.cleaned_data['operator_password'])

        # Création du cash
        cash = Cash(sender=form.cleaned_data['sender'],
                    recipient=User.objects.get(username='AE_ENSAM'),
                    amount=form.cleaned_data['amount'])
        cash.save()

        # Création du paiement
        payment = Payment()
        payment.save()
        payment.cashs.add(cash)
        payment.maj_amount()
        payment.save()

        # Création de la vente
        sale = Sale(date=datetime.now(),
                    sender=form.cleaned_data['sender'],
                    operator=operator,
                    recipient=User.objects.get(username='AE_ENSAM'),
                    payment=payment)
        sale.save()

        # Création d'un spfc d'argent fictif
        spfc = SingleProductFromContainer(container=Container.objects.get(
            product_base__product_unit__name='Argent fictif'), quantity=payment.amount*100,
            sale_price=payment.amount, sale=sale)
        spfc.save()

        # Mise à jour du compte foyer du client
        sale.maj_amount()
        sale.save()
        sender = form.cleaned_data['sender']
        sender.credit(sale.amount)

        return super(SupplyCashView, self).form_valid(form)

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(SupplyCashView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


class SupplyLydiaView(FormView):
    form_class = SupplyLydiaForm
    template_name = 'finances/supply_lydia.html'
    success_url = '/auth/login'

    def form_valid(self, form):

        # Identification du gestionnaire
        # Le cas d'échec d'authentification est géré dans le form.clean()
        operator = authenticate(username=form.cleaned_data['operator_username'],
                                password=form.cleaned_data['operator_password'])

        # Création du cash
        lydia = Lydia(time_operation=form.cleaned_data['time_operation'],
                      id_from_lydia=form.cleaned_data['id_from_lydia'],
                      sender_user_id=form.cleaned_data['sender'],
                      recipient_user_id=User.objects.get(username='AE_ENSAM'),
                      amount=form.cleaned_data['amount'])
        lydia.save()

        # Création du paiement
        payment = Payment()
        payment.save()
        payment.lydias.add(lydia)
        payment.maj_amount()
        payment.save()

        # Création de la vente
        sale = Sale(date=datetime.now(),
                    sender=form.cleaned_data['sender'],
                    operator=operator,
                    recipient=User.objects.get(username='AE_ENSAM'),
                    payment=payment)
        sale.save()

        # Création d'un spfc d'argent fictif
        spfc = SingleProductFromContainer(container=Container.objects.get(
            product_base__product_unit__name='Argent fictif'), quantity=payment.amount*100,
            sale_price=payment.amount, sale=sale)
        spfc.save()

        # Mise à jour du compte foyer du client
        sale.maj_amount()
        sale.save()
        sender = form.cleaned_data['sender']
        sender.credit(sale.amount)

        return super(SupplyLydiaView, self).form_valid(form)

    def get_initial(self):
        initial = super(SupplyLydiaView, self).get_initial()
        initial['time_operation'] = datetime.now()
        return initial

    def get_success_url(self):
        return force_text(self.request.POST.get('next', self.success_url))

    def get_context_data(self, **kwargs):
        context = super(SupplyLydiaView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.success_url)
        return context


def bank_account_from_user(request):
    data = serializers.serialize('xml',
                                 BankAccount.objects.filter(owner=User.objects.get(pk=request.GET.get('user_pk'))))
    return HttpResponse(data)


# Models
class BankAccountCreateView(CreateView):
    model = BankAccount
    fields = ['bank', 'account', 'owner']
    template_name = 'finances/bank_account_create.html'
    success_url = '/finances/bank_account'


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
