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
    sender = models.ForeignKey('users.User', related_name='sender')
    recipient = models.ForeignKey('users.User', related_name='recipient')
    # Avec shops

    # Avec finances
    payment = models.ForeignKey('Payment')

    # Méthodes
    def __str__(self):
        return 'Achat n°' + str(self.id)

    def use_cheque(self):
        if len(self.list_cheques()) == 0:
            return False
        else:
            return True

    def use_lydia(self):
        if len(self.list_lydias()) == 0:
            return False
        else:
            return True

    def use_cash(self):
        if len(self.list_cashs()) == 0:
            return False
        else:
            return True

    def use_foyer(self):
        if self.foyer == 0:
            return False
        else:
            return True

    def list_cheques(self):
        return Cheque.objects.filter(purchase__cheques__purchase=self)

    def sub_total_cheques(self):
        u_c = 0
        for e in self.list_cheques():
            u_c = u_c + e.amount
        return u_c

    def list_cashs(self):
            return Cash.objects.filter(purchase__cashs__purchase=self)

    def sub_total_cashs(self):
        u_ca = 0
        for e in self.list_cashs():
            u_ca = u_ca + e.amount
        return u_ca

    def list_lydias(self):
            return Lydia.objects.filter(purchase__lydias__purchase=self)

    def sub_total_lydias(self):
        u_l = 0
        for e in self.list_lydias():
            u_l = u_l + e.amount
        return u_l

    def total(self):
        return self.sub_total_cashs()+self.sub_total_cheques()+self.sub_total_lydias()

    def list_single_products(self):
        return SingleProduct.objects.filter(purchase=self)

    def sub_total_single_products(self):
        u_sp = 0
        for e in self.list_single_products():
            u_sp = u_sp + e.price
        return u_sp

    def list_single_products_from_container(self):
        return SingleProductFromContainer.objects.filter(purchase=self)

    def sub_total_single_products_from_container(self):
        u_spfc = 0
        for e in self.list_single_products_from_container():
            u_spfc = u_spfc + e.price
        return u_spfc

    def total_product(self):
        return self.sub_total_single_products() + self.sub_total_single_products_from_container()


class Cheque(models.Model):
    # Informations sur l'identite du cheque
    number = models.CharField(max_length=7)
    signatory = models.ForeignKey('users.User', related_name='cheque_signatory')
    date_sign = models.DateField(default=now)
    recipient = models.ForeignKey('users.User', related_name='cheque_recipient')
    amount = models.FloatField()

    # Information de comptabilite
    date_cash = models.DateField(blank=True, null=True)
    cashed = models.BooleanField(default=False)

    def __str__(self):
        return self.signatory.last_name+' '+self.signatory.first_name+' '+str(self.amount)+'€ n°'+self.number

    def list_transaction(self):
        return Transaction.objects.filter(cheques__transaction__cheques=self)


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



