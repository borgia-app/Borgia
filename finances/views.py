#-*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.core import serializers

from finances.forms import *
from finances.models import *


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
    success_url = '/finances/transaction/create'

    def get_initial(self):
        return {'receiver': self.request.user}


# Affichage detaille d'un virement Lydia - R
class LydiaRetrieveView(DetailView):
    model = Lydia
    template_name = "finances/lydia_retrieve.html"


# Update d'un virement Lydia - U
class LydiaUpdateView(UpdateView):
    model = Lydia
    fields = ['giver', 'receiver', 'date_received', 'amount', 'cashed']
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
