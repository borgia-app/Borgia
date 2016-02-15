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

    # Méthodes


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



