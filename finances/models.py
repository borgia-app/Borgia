#-*- coding: utf-8 -*-
from django.db import models
from shops.models import SingleProduct, SingleProductFromContainer
from django.utils.timezone import now


class Sale(models.Model):
    """Une transaction.

    Défini un échange entre deux personnes,
    entre deux membres, entre un membre et l'association, ...

    """

    # Attributs
    amount = models.FloatField(default=0)
    date = models.DateTimeField(default=now)
    done = models.BooleanField(default=False)

    # Relations
    # Avec users
    sender = models.ForeignKey('users.User', related_name='sender_sale')
    recipient = models.ForeignKey('users.User', related_name='recipient_sale')
    # Avec shops

    # Avec finances
    payment = models.ForeignKey('Payment', blank=True, null=True)

    # Méthodes
    def __str__(self):
        return 'Achat n°' + str(self.id)

    def list_single_products(self):
        list_single_product = SingleProduct.objects.filter(sale=self)
        total_sale_price = 0
        for e in list_single_product:
            total_sale_price += e.sale_price
        return list_single_product, total_sale_price

    def list_single_products_from_container(self):
        list_single_product_from_container = SingleProductFromContainer.objects.filter(sale=self)
        total_sale_price = 0
        for e in list_single_product_from_container:
            total_sale_price += e.sale_price
        return list_single_product_from_container, total_sale_price

    def maj_amount(self):
        self.amount = self.list_single_products()[1] + self.list_single_products_from_container()[1]
        self.save()


class Payment(models.Model):
    """Un paiement.

    Regroupe les différents moyens de paiements utilisés pour une sale

    """

    # Attributs
    amount = models.FloatField(default=0)

    # Relations
    cheques = models.ManyToManyField('Cheque', blank=True)
    cashs = models.ManyToManyField('Cash', blank=True)
    lydias = models.ManyToManyField('Lydia', blank=True)
    debit_balance = models.ManyToManyField('DebitBalance', blank=True)

    # Méthodes
    def list_cheque(self):
        list_cheque = Cheque.objects.filter(payment__cheques__payment=self)
        total_cheque = 0
        for e in list_cheque:
            total_cheque += e.amount
        return list_cheque, total_cheque

    def list_lydia(self):
        list_lydia = Lydia.objects.filter(payment__lydias__payment=self)
        total_lydia = 0
        for e in list_lydia:
            total_lydia += e.amount
        return list_lydia, total_lydia

    def list_cash(self):
        list_cash = Cheque.objects.filter(payment__cashs__payment=self)
        total_cash = 0
        for e in list_cash:
            total_cash += e.amount
        return list_cash, total_cash

    def list_debit_balance(self):
        list_debit_balance = DebitBalance.objects.filter(payment__debit_balance__payment=self)
        total_debit_balance = 0
        for e in list_debit_balance:
            total_debit_balance += e.amount
        return list_debit_balance, total_debit_balance

    def maj_amount(self):
        self.amount = self.list_cheque()[1] + self.list_lydia()[1]\
                      + self.list_cash()[1] + self.list_debit_balance()[1]
        self.save()

    def payments_used(self):
        payments_used = []
        if self.list_cheque()[1] != 0:
            payments_used.append('Cheque')
        if self.list_cash()[1] != 0:
            payments_used.append('Espèces')
        if self.list_lydia()[1] != 0:
            payments_used.append('Lydia')
        if self.list_debit_balance()[1] != 0:
            payments_used.append('Compte foyer')
        return payments_used


class DebitBalance(models.Model):

    # Attributs
    amount = models.FloatField(default=0)
    date = models.DateTimeField(default=now)
    # Relations
    sender = models.ForeignKey('users.User', related_name='sender_debit_balance')
    recipient = models.ForeignKey('users.User', related_name='recipient_debit_balance')

    # Méthodes
    def __str__(self):
        return str(self.amount) + ' ' + str(self.date)


class Cheque(models.Model):

    # Attributs
    amount = models.FloatField(default=0)
    is_cashed = models.BooleanField(default=False)
    signature_date = models.DateField(default=now)
    cheque_number = models.CharField(max_length=7)

    # Relations
    sender = models.ForeignKey('users.User', related_name='cheque_sender')
    recipient = models.ForeignKey('users.User', related_name='cheque_recipient')
    bank_account = models.ForeignKey('BankAccount', related_name='cheque_bank_account')

    # Méthodes
    def __str__(self):
        return self.sender.last_name+' '+self.sender.first_name+' '+str(self.amount)+'€ n°'+self.cheque_number

    def list_payments(self):
        return Payment.objects.filter(cheques__payment__cheques=self)

    def list_sale(self):
        return Sale.objects.filter(payment__cheques=self)


class BankAccount(models.Model):

    # Attributs
    bank = models.CharField(max_length=255)
    account = models.CharField(max_length=255)

    # Relations
    owner = models.ForeignKey('users.User', related_name='owner_bank_account')

    # Méthodes
    def __str__(self):
        return self.bank + self.account


# TODO: a modifier
class Cash(models.Model):
    # Information sur l'identite des especes
    amount = models.FloatField()
    giver = models.ForeignKey('users.User', related_name='cash_giver')

    # Information de comptabilite
    cashed = models.BooleanField(default=False)
    date_cash = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.giver.last_name+' '+self.giver.first_name+' '+str(self.amount)+'€'

    def list_transaction(self):
        return Transaction.objects.filter(cashs__transaction__cashs=self)


# TODO: a modifier
class Lydia(models.Model):
    # Information sur l'identite du virement lydia
    date_operation = models.DateField(default=now)
    time_operation = models.TimeField(default=now)
    amount = models.FloatField()
    # numero unique ?
    giver = models.ForeignKey('users.User', related_name='lydia_giver')
    recipient = models.ForeignKey('users.User', related_name='lydia_recipient')

    # Information de comptabilite
    cashed = models.BooleanField(default=False)
    date_cash = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.giver.last_name+' '+self.giver.first_name+' '+str(self.amount)+'€'

    def list_transaction(self):
        return Transaction.objects.filter(lydias__transaction__lydias=self)



