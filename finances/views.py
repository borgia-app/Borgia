#-*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse, force_text
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView
from django.core import serializers
from datetime import datetime

from finances.forms import *
from finances.models import *
from shops.models import Container


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


def bank_account_from_user(request):
    data = serializers.serialize('xml',
                                 BankAccount.objects.filter(owner=User.objects.get(pk=request.GET.get('user_pk'))))
    return HttpResponse(data)


# Model BANKACCOUNT
# Creation d'un compte en banque - C
class BankAccountCreateView(CreateView):
    model = BankAccount
    fields = ['bank', 'account', 'owner']
    template_name = 'finances/bank_account_create.html'
    success_url = '/finances/bank_account'


# Update d'un compte en banque - U
class BankAccountUpdateView(UpdateView):
    model = BankAccount
    fields = ['bank', 'account', 'owner']
    template_name = 'finances/bank_account_update.html'
    success_url = '/finances/bank_account/'


# Suppression d'un compte en banque - D
class BankAccountDeleteView(DeleteView):
    model = BankAccount
    template_name = 'finances/bank_account_delete.html'
    success_url = '/finances/bank_account'


# Liste de compte en banque - List
class BankAccountListView(ListView):
    model = BankAccount
    template_name = "finances/bank_account_list.html"
    queryset = BankAccount.objects.all()


# Model CHEQUE
# Creation d'un cheque - C
class ChequeCreateView(CreateView):
    model = Cheque
    form_class = ChequeCreateForm
    template_name = 'finances/cheque_create.html'
    success_url = '/finances/cheque/'

    def get_initial(self):
        return {'recipient': User.objects.get(username='AE_ENSAM')}


# Affichage detaille d'un cheque - R
class ChequeRetrieveView(DetailView):
    model = Cheque
    template_name = "finances/cheque_retrieve.html"


# Update d'un cheque - U
class ChequeUpdateView(UpdateView):
    model = Cheque
    fields = ['amount', 'is_cashed', 'signature_date', 'cheque_number','sender', 'bank_account', 'recipient']
    template_name = 'finances/cheque_update.html'
    success_url = '/finances/cheque/'


# Suppression d'un cheque - D
class ChequeDeleteView(DeleteView):
    model = Cheque
    template_name = 'finances/cheque_delete.html'
    success_url = '/finances/cheque'


# Liste de cheques - List
class ChequeListView(ListView):
    model = Cheque
    template_name = "finances/cheque_list.html"
    queryset = Cheque.objects.all()


# Model CASH
# Creation d'especes - C
class CashCreateView(CreateView):
    model = Cash
    form_class = CreationCashForm
    template_name = 'finances/cash_create.html'
    success_url = '/finances/transaction/create'


# Affichage detaille d'especes - R
class CashRetrieveView(DetailView):
    model = Cash
    template_name = "finances/cash_retrieve.html"


# Update d'especes - U
class CashUpdateView(UpdateView):
    model = Cash
    fields = ['giver', 'amount', 'cashed']
    template_name = 'finances/cash_update.html'
    success_url = '/finances/cash/'


# Suppression d'especes - D
class CashDeleteView(DeleteView):
    model = Cash
    template_name = 'finances/cash_delete.html'
    success_url = '/finances/cash'


# Liste d'especes - List
class CashListView(ListView):
    model = Cash
    template_name = "finances/cash_list.html"
    queryset = Cash.objects.all()


# Model LYDIA
# Creation d'un virement Lydia - C
class LydiaCreateView(CreateView):
    model = Lydia
    form_class = CreationLydiaForm
    template_name = 'finances/lydia_create.html'
    success_url = '/finances/sale/'

    def get_initial(self):
        return {'receiver': self.request.user}


# Affichage detaille d'un virement Lydia - R
class LydiaRetrieveView(DetailView):
    model = Lydia
    template_name = "finances/lydia_retrieve.html"


# Update d'un virement Lydia - U
class LydiaUpdateView(UpdateView):
    model = Lydia
    fields = ['sender_user_id', 'recipient_user_id', 'date_operation', 'time_operation', 'amount', 'banked', 'date_banked','id_from_lydia',]
    template_name = 'finances/lydia_update.html'
    success_url = '/finances/lydia/'


# Suppression d'un virement Lydia - D
class LydiaDeleteView(DeleteView):
    model = Lydia
    template_name = 'finances/lydia_delete.html'
    success_url = '/finances/lydia'


# Liste virements Lydias - List
class LydiaListView(ListView):
    model = Lydia
    template_name = "finances/lydia_list.html"
    queryset = Lydia.objects.all()


# Model SALE

# Affichage detaille d'une vente - R
class SaleRetrieveView(DetailView):
    model = Sale
    template_name = 'finances/sale_retrieve.html'


# Liste des ventes - List
class SaleListView(ListView):
    model = Sale
    template_name = "finances/sale_list.html"
    queryset = Sale.objects.all()


class SaleListLightView(ListView):
    model = Sale
    template_name = "finances/sale_list_light.html"
    queryset = Sale.objects.all()
