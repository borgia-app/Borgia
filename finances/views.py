from django.shortcuts import HttpResponseRedirect, force_text, render, render_to_response
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth import authenticate

from finances.forms import *
from finances.models import *
from shops.forms import *


# Model TRANSACTION
# Creation d'une transaction - C
class TransactionCreateView(FormView):
    template_name = 'finances/transaction_create.html'
    form_class = CreationTransactionForm

    def get_initial(self):
        # L'opérateur est celui qui est connecté
        return {'operator': self.request.user}

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        # Sauvegarde de la transaction (avant validation ...)
        self.object = form.save()
        # Redirection vers la validation
        return HttpResponseRedirect(self.get_success_url(pk=self.object.id))

    def get_success_url(self, **kwargs):
        """
        Returns the supplied success URL.
        """
        # Construction de l'url de validation
        return '/finances/transaction/validation/'+str(kwargs.get('pk'))


class TransactionChequeFastCreateView(FormView):
    """"
    Vue de création rapide d'une transaction, associée à un seul et unique chèque
    """""
    template_name = 'finances/transaction_cheque_fast_create.html'
    form_class = CreationTransactionChequeFastForm
    success_url = '/auth/login'

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        # Procédure d'authentification
        user = authenticate(username=form.cleaned_data['operator'].username, password=form.cleaned_data['password'])
        if user:  # Opérateur identifié
            # Création du chèque et de la transaction
            cheque = Cheque(number=form.cleaned_data['number'], signatory=form.cleaned_data['client'],
                            recipient=User.objects.get(username='AE_ENSAM'),
                            amount=form.cleaned_data['amount'])
            cheque.save()
            transaction = Transaction(operator=user, client=form.cleaned_data['client'],
                                      validated=True)
            transaction.save()
            transaction.cheques.add(cheque)
            transaction.save()

            # Crédit du compte
            credit = transaction.client.credit(transaction.total())
            if credit == transaction.total():
                transaction.error_credit = False
                transaction.client.save()
                transaction.save()

            return HttpResponseRedirect(self.get_success_url())

        else:
            return HttpResponseRedirect(force_text('/finances/transaction/create_cheque_fast/'))


class TransactionCashFastCreateView(FormView):
    """"
    Vue de création rapide d'une transaction, associée à un seul et unique chèque
    """""
    template_name = 'finances/transaction_cash_fast_create.html'
    form_class = CreationTransactionPaymentFast
    success_url = '/auth/login'

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        # Procédure d'authentification
        user = authenticate(username=form.cleaned_data['operator'].username, password=form.cleaned_data['password'])
        if user:  # Opérateur identifié
            # Création du cash et de la transaction
            cash = Cash(giver=form.cleaned_data['client'], amount=form.cleaned_data['amount'])
            cash.save()
            transaction = Transaction(operator=user, client=form.cleaned_data['client'],
                                      validated=True)
            transaction.save()
            transaction.cashs.add(cash)
            transaction.save()

            # Crédit du compte
            credit = transaction.client.credit(transaction.total())
            if credit == transaction.total():
                transaction.error_credit = False
                transaction.client.save()
                transaction.save()

            return HttpResponseRedirect(self.get_success_url())

        else:
            return HttpResponseRedirect(force_text('/finances/transaction/create_cash_fast/'))


class TransactionLydiaFastCreateView(FormView):
    """"
    Vue de création rapide d'une transaction, associée à un seul et unique chèque
    """""
    template_name = 'finances/transaction_lydia_fast_create.html'
    form_class = CreationTransactionLydiaFastForm
    success_url = '/auth/login'

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        # Procédure d'authentification
        user = authenticate(username=form.cleaned_data['operator'].username, password=form.cleaned_data['password'])
        if user:  # Opérateur identifié
            # Création du virement lydia et de la transaction
            lydia = Lydia(giver=form.cleaned_data['client'], recipient=user, amount=form.cleaned_data['amount'],
                          time_operation=form.cleaned_data['time_operation'])
            lydia.save()
            transaction = Transaction(operator=user, client=form.cleaned_data['client'],
                                      validated=True)
            transaction.save()
            transaction.lydias.add(lydia)
            transaction.save()

            # Crédit du compte
            credit = transaction.client.credit(transaction.total())
            if credit == transaction.total():
                transaction.error_credit = False
                transaction.client.save()
                transaction.save()

            return HttpResponseRedirect(self.get_success_url())

        else:
            return HttpResponseRedirect(force_text('/finances/transaction/create_lydia_fast/'))


# Vue de validation de la transaction
class TransactionValidationView(UpdateView):
    model = Transaction
    fields = ['validated']
    template_name = 'finances/transaction_validation.html'
    success_url = '/finances/transaction/create'

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # Crédit du client
        credit = self.object.client.credit(self.object.total())
        # Vérification
        if credit == self.object.total():
            self.object.error_credit = False
            form.save()
            self.object.client.save()

        return super(ModelFormMixin, self).form_valid(form)


# Affichage détaillé d'une transaction - R
class TransactionRetrieveView(DetailView):
    model = Transaction
    template_name = "finances/transaction_retrieve.html"


# Update d'une transaction - U
class TransactionUpdateView(UpdateView):
    model = Transaction
    fields = ['date', 'time', 'validated', 'cheques', 'cashs', 'lydias']
    template_name = 'finances/transaction_update.html'
    success_url = '/finances/transaction/'


# Suppression d'une transaction - D
class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'finances/transaction_delete.html'
    success_url = '/finances/transaction'


# Liste de transactions - List
class TransactionListView(ListView):
    model = Transaction
    template_name = "finances/transaction_list.html"
    queryset = Transaction.objects.all()


# Model CHEQUE
# Création d'un chèque - C
class ChequeCreateView(CreateView):
    model = Cheque
    form_class = CreationChequeForm
    template_name = 'finances/cheque_create.html'
    success_url = '/finances/transaction/create'

    def get_initial(self):
        return {'recipient': User.objects.get(username='AE_ENSAM')}


# Affichage détaillé d'un chèque - R
class ChequeRetrieveView(DetailView):
    model = Cheque
    template_name = "finances/cheque_retrieve.html"


# Update d'un chèque - U
class ChequeUpdateView(UpdateView):
    model = Cheque
    fields = ['giver', 'receiver', 'number', 'date_cash', 'date_sign', 'date_received', 'amount', 'cashed']
    template_name = 'finances/cheque_update.html'
    success_url = '/finances/cheque/'


# Suppression d'un chèque - D
class ChequeDeleteView(DeleteView):
    model = Cheque
    template_name = 'finances/cheque_delete.html'
    success_url = '/finances/cheque'


# Liste de chéques - List
class ChequeListView(ListView):
    model = Cheque
    template_name = "finances/cheque_list.html"
    queryset = Cheque.objects.all()


# Model CASH
# Création d'espèces - C
class CashCreateView(CreateView):
    model = Cash
    form_class = CreationCashForm
    template_name = 'finances/cash_create.html'
    success_url = '/finances/transaction/create'


# Affichage détaillé d'espèces - R
class CashRetrieveView(DetailView):
    model = Cash
    template_name = "finances/cash_retrieve.html"


# Update d'espèces - U
class CashUpdateView(UpdateView):
    model = Cash
    fields = ['giver', 'amount', 'cashed']
    template_name = 'finances/cash_update.html'
    success_url = '/finances/cash/'


# Suppression d'espèces - D
class CashDeleteView(DeleteView):
    model = Cash
    template_name = 'finances/cash_delete.html'
    success_url = '/finances/cash'


# Liste d'espèces - List
class CashListView(ListView):
    model = Cash
    template_name = "finances/cash_list.html"
    queryset = Cash.objects.all()


# Model LYDIA
# Création d'un virement Lydia - C
class LydiaCreateView(CreateView):
    model = Lydia
    form_class = CreationLydiaForm
    template_name = 'finances/lydia_create.html'
    success_url = '/finances/transaction/create'

    def get_initial(self):
        return {'receiver': self.request.user}


# Affichage détaillé d'un virement Lydia - R
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


# Model PURCHASE
# Création d'un achat - C

# Affichage détaillé d'un achat - R
class PurchaseRetrieveView(DetailView):
    model = Purchase
    template_name = 'finances/purchase_retrieve.html'


# Update d'un virement Lydia - U
class PurchaseUpdateView(UpdateView):
    model = Purchase
    fields = []
    template_name = 'finances/purchase_update.html'
    success_url = '/finances/purchase/'


# Suppression d'un virement Lydia - D
class PurchaseDeleteView(DeleteView):
    model = Purchase
    template_name = 'finances/purchase_delete.html'
    success_url = '/finances/purchase'


# Liste virements Lydias - List
class PurchaseListView(ListView):
    model = Purchase
    template_name = "finances/purchase_list.html"
    queryset = Purchase.objects.all().order_by('-time')
