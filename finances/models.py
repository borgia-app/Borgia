#-*- coding: utf-8 -*-
from django.db import models
from django.utils.timezone import now
from datetime import datetime
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.validators import MinValueValidator, RegexValidator
import json

from shops.models import SingleProduct, SingleProductFromContainer, Container


class Sale(models.Model):
    """Une transaction.

    Défini un échange entre deux personnes,
    entre deux membres, entre un membre et l'association, ...

    """

    CATEGORY_CHOICES = (('transfert', 'Transfert'), ('recharging', 'Rechargement'), ('sale', 'Vente'),
                        ('exceptionnal_movement', 'Mouvement exceptionnel'),
                        ('shared_event', 'Evénement'))

    # Attributs
    amount = models.DecimalField('Montant', default=0, decimal_places=2, max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    date = models.DateTimeField('Date', default=now)
    done = models.BooleanField('Terminée', default=False)
    is_credit = models.BooleanField('Est un crédit', default=False)
    category = models.CharField('Catégorie', choices=CATEGORY_CHOICES, default='sale', max_length=50)
    wording = models.CharField('Libellé', default='', max_length=254)
    justification = models.TextField('Justification', null=True, blank=True)

    # Relations
    # Avec users
    sender = models.ForeignKey('users.User', related_name='sender_sale')
    recipient = models.ForeignKey('users.User', related_name='recipient_sale')
    operator = models.ForeignKey('users.User', related_name='operator_sale')

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

    def list_shared_events(self):
        list_shared_event = SharedEvent.objects.filter(sale=self)
        total_sale_price = 0
        for e in list_shared_event:
            total_sale_price += e.price
        return list_shared_event, total_sale_price

    def maj_amount(self):
        self.amount = self.list_single_products()[1] + self.list_single_products_from_container()[1] \
                      + self.list_shared_events()[1]
        self.save()

    def price_for(self, user):
        price_for = 0
        # Cas des crédits
        if self.is_credit is True or self.recipient == user:
            price_for = self.amount
        # Cas des débit
        else:
            for e in self.payment.list_lydia()[0]:
                if e.sender == user:
                    price_for += e.amount
            for e in self.payment.list_cash()[0]:
                if e.sender == user:
                    price_for += e.amount
            for e in self.payment.list_cheque()[0]:
                if e.sender == user:
                    price_for += e.amount
            for e in self.payment.list_debit_balance()[0]:
                if e.sender == user:
                    price_for += e.amount
            price_for = -price_for
        return price_for

    def string_products(self):
        string = ''
        for p in self.list_single_products()[0]:
            string += p.__str__() + ', '
        for p in self.list_single_products_from_container()[0]:
            string += p.__str__() + ', '
        string = string[0: len(string)-2]
        return string

    class Meta:
        permissions = (
            ('retrieve_sale', 'Afficher une vente'),
            ('list_sale', 'Lister les ventes'),
            ('add_transfert', 'Effectuer un transfert d\'argent')
        )


class Payment(models.Model):
    """Un paiement.

    Regroupe les différents moyens de paiements utilisés pour une sale

    """

    # Attributs
    amount = models.DecimalField('Montant', default=0, decimal_places=2, max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])

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
        list_cash = Cash.objects.filter(payment__cashs__payment=self)
        total_cash = 0
        for e in list_cash:
            total_cash += e.amount
        return list_cash, total_cash

    def list_debit_balance(self):
        list_debit_balance = DebitBalance.objects.filter(payment__debit_balance__payment=self).distinct()
        total_debit_balance = 0
        for e in list_debit_balance:
            total_debit_balance += e.amount
        return list_debit_balance, total_debit_balance

    def maj_amount(self):
        self.amount = self.list_cheque()[1] + self.list_lydia()[1] \
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
    amount = models.DecimalField('Montant', default=0, decimal_places=2, max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    date = models.DateTimeField('Date', default=now)
    # Relations
    sender = models.ForeignKey('users.User', related_name='sender_debit_balance')
    recipient = models.ForeignKey('users.User', related_name='recipient_debit_balance')

    # Méthodes
    def __str__(self):
        return str(self.amount) + ' ' + str(self.date)

    def set_movement(self):
        # On se place du point de vue de l'association AE ENSAM
        # amount(recu) > 0 : debit du client
        # amount(recu) < 0 : crédit du client
        self.sender.balance -= self.amount
        self.sender.save()

    class Meta:
        permissions = (
            ('retrieve_debitbalance', 'Afficher un débit sur compte foyer'),
            ('list_debitbalance', 'Lister les débits sur comptes foyers'),
        )


class Cheque(models.Model):

    # Attributs
    amount = models.DecimalField('Montant', default=0, decimal_places=2, max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    is_cashed = models.BooleanField('Est encaissé', default=False)
    signature_date = models.DateField('Date de signature', default=now)
    cheque_number = models.CharField('Numéro de chèque', max_length=7,
                                     validators=[RegexValidator('^[0-9]{7}$', 'Numéro de chèque invalide')])

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

    class Meta:
        permissions = (
            ('retrieve_cheque', 'Afficher un cheque'),
            ('list_cheque', 'Lister les chèques'),
        )


class BankAccount(models.Model):

    # Attributs
    bank = models.CharField('Banque', max_length=255)
    account = models.CharField('Numéro de compte', max_length=255)

    # Relations
    owner = models.ForeignKey('users.User', related_name='owner_bank_account')

    # Méthodes
    def __str__(self):
        return self.bank + self.account

    class Meta:
        permissions = (
            ('retrieve_bankaccount', 'Afficher un compte en banque'),
            ('add_own_bankaccount', 'Ajouter un compte en banque personnel'),
            ('list_bankaccount', 'Lister les comptes en banque'),
        )


class Cash(models.Model):

    # Attributs
    amount = models.DecimalField('Montant', default=0, decimal_places=2, max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])

    # Relations
    sender = models.ForeignKey('users.User', related_name='cash_sender')
    recipient = models.ForeignKey('users.User', related_name='cash_recipient')

    # Méthodes
    def __str__(self):
        return self.sender.last_name+' '+self.sender.first_name+' '+str(self.amount)+'€'

    def list_sale(self):
        return Sale.objects.filter(payment__cashs=self)

    def list_payment(self):
        return Payment.objects.filter(cashs__payment__cashs=self)

    class Meta:
        permissions = (
            ('retrieve_cash', 'Afficher des espèces'),
            ('list_cash', 'Lister les espèces'),
        )


class Lydia(models.Model):
    # Information sur l'identite du virement lydia
    date_operation = models.DateField('Date', default=now)
    amount = models.DecimalField('Montant', default=0, decimal_places=2, max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    # numero unique du virement lydia
    id_from_lydia = models.CharField('Numéro unique', max_length=255)
    sender = models.ForeignKey('users.User', related_name='lydia_sender')
    recipient = models.ForeignKey('users.User', related_name='lydia_recipient')

    # Information de comptabilite
    banked = models.BooleanField('Est encaissé', default=False)
    date_banked = models.DateField('Date encaissement', blank=True, null=True)

    def __str__(self):
        return self.sender.last_name+' '+self.sender.first_name+' '+str(self.amount)+'€'

    def list_transaction(self):
        return Sale.objects.filter(payment__lydias=self)

    class Meta:
        permissions = (
            ('retrieve_lydia', 'Afficher un virement Lydia'),
            ('list_lydia', 'Lister les virements Lydias'),
        )


class SharedEvent(models.Model):
    """
    Une évènement partagé et payé par plusieurs personnes
    ex: un repas

    Remarque :
    les participants sont dans la relation m2m participants.
    Cependant, cette liste n'est pas ordonnée et deux demande de query peuvent renvoyer deux querys ordonnés différement
    Du coup on stocke le duo [participant_pk, ponderation] dans une liste dumpé JSON dans le string "ponderation"
    Je garde le m2m participants pour avoir quand même un lien plus simple (pour les recherches etc.)
    Lors de la suppression / ajout il faut utiliser les méthodes add_participant et remove_participant pour faire ca
    proprement.
    """

    # Attributs
    description = models.CharField('Description', max_length=254)
    date = models.DateField('Date', default=now)
    price = models.DecimalField('Prix', decimal_places=2, max_digits=9, null=True, blank=True,
                                validators=[MinValueValidator(Decimal(0))])
    bills = models.CharField('Facture(s)', max_length=254, null=True, blank=True)
    done = models.BooleanField('Terminé', default=False)

    # Relations
    manager = models.ForeignKey('users.User', related_name='manager')
    sale = models.ForeignKey('Sale', null=True, blank=True)
    participants = models.ManyToManyField('users.User', blank=True, related_name='participants')
    registered = models.ManyToManyField('users.User', blank=True, related_name='registered')
    ponderation = models.CharField('Liste ordonnée participants - pondérations', max_length=10000, default='[]')

    # Méthodes
    def __str__(self):
        return self.description + ' ' + str(self.date)

    def set_ponderation(self, x):
        """
        Transforme la liste x en string JSON qui est stocké dans ponderation
        :param x: liste [[user_pk, ponderation], [user_pk, ponderation], ...]
        :return:
        """
        self.ponderation = json.dumps(x)
        if self.ponderation == 'null':
            self.ponderation = '[]'
        self.save()

    def get_ponderation(self):
        """
        Transforme le string JSON ponderation en une liste
        :return: liste ponderation [[user_pk, ponderation], [user_pk, ponderation], ...]
        """
        list_ponderation = []
        for e in json.loads(self.ponderation):
            list_ponderation.append(e)
        return list_ponderation

    def remove_participant(self, user):
        """
        Suppresion propre d'un participant (m2m participants et ponderation)
        :param user: user à supprimer
        :return:
        """
        # Suppresion de l'user dans participants
        self.participants.remove(user)
        self.save()

        # Suppresion du premier élément de pondération qui correspond à l'user_pk
        for e in self.get_ponderation():
            if e[0] == user.pk:
                new_ponderation = self.get_ponderation()
                new_ponderation.remove(e)
                self.set_ponderation(new_ponderation)
                break

    def add_participant(self, user, ponderation):
        """
        Ajout propre d'un participant (m2m participant et ponderation)
        :param user: user à ajouter
        :param ponderation: ponderation liée à user
        :return:
        """

        # Enregistrement dans une nouvelle liste (le traitement direct sur get_ponderation() ne semble pas fonctionner)
        old_ponderation = self.get_ponderation()
        new_ponderation = []

        # Si l'user est déjà dans la liste, on ne l'ajoute pas
        in_list = False
        for e in old_ponderation:
            new_ponderation.append(e)
            if e[0] == user.pk:
                in_list = True

        # Si pas dans la liste, on l'ajoute
        if in_list is False:
            new_ponderation.append([user.pk, ponderation])
            self.participants.add(user)
            self.set_ponderation(new_ponderation)

    def list_of_participants_ponderation(self):
        """
        Forme une liste des participants [[user, ponderation], [user, ponderation]] à partir de la liste ponderation
        :return: liste_u_p [[user, ponderation], [user, ponderation]]
        """
        list_u_p = []
        for e in self.get_ponderation():
            list_u_p.append([get_user_model().objects.get(pk=e[0]), e[1]])
        return list_u_p

    def list_of_registered_ponderation(self):
        """
        Forme une liste des inscrits [[user, 1], [user, 1]] à partir des inscrits
        La pondération d'un inscrit est toujours de 1
        :return: liste_u_p [[user, 1], [user, 1]]
        """
        list_u_p = []
        for u in self.registered.all():
            list_u_p.append([u, 1])
        return list_u_p

    def pay(self, operator, recipient):
        """
        Procède au paiement de l'évenement par les participants.
        Une seule vente, un seul paiement mais plusieurs débits sur compte (un par participant)
        :param operator: user qui procède au paiement
        :param recipient: user qui recoit les paiements (AE_ENSAM)
        :return:
        """

        # Création Sale
        sale = Sale.objects.create(date=now(),
                                   sender=operator,
                                   recipient=recipient,
                                   operator=operator,
                                   category='shared_event',
                                   wording=self.description)

        # Liaison de l'événement commun
        self.sale = sale
        self.save()

        # Calcul du prix par
        total_ponderation = 0
        for e in self.list_of_participants_ponderation():
            total_ponderation += e[1]
        price_per_participant = round(self.price / total_ponderation, 2)

        # Créations paiements par compte foyer
        payment = Payment.objects.create()

        for u in self.list_of_participants_ponderation():
            d_b = DebitBalance.objects.create(amount=price_per_participant*u[1],
                                              date=now(),
                                              sender=u[0],
                                              recipient=sale.recipient)
            # Paiement
            payment.debit_balance.add(d_b)
            d_b.set_movement()

        payment.save()
        payment.maj_amount()

        sale.payment = payment
        sale.maj_amount()
        sale.save()

        self.done = True
        self.save()

    class Meta:
        permissions = (
            ('register_sharedevent', 'S\'inscrire à un événement commun'),
            ('list_sharedevent', 'Lister les événements communs'),
            ('manage_sharedevent', 'Gérer les événements communs'),
            ('proceed_payment_sharedevent', 'Procéder au paiement des événements communs'),
        )


def supply_self_lydia(user, recipient, amount, transaction_identifier):

    container = Container.objects.get(pk=1)

    # Sale
    sale = Sale.objects.create(date=datetime.now(),
                               sender=user,
                               recipient=recipient,
                               operator=user,
                               is_credit=True,
                               category='recharging',
                               wording='Rechargement automatique')
    # Spfc
    SingleProductFromContainer.objects.create(container=container,
                                              sale=sale,
                                              quantity=amount*100,
                                              sale_price=amount)
    sale.maj_amount()

    # Lydia
    lydia = Lydia.objects.create(date_operation=datetime.now(),
                                 amount=amount,
                                 id_from_lydia=transaction_identifier,
                                 sender=user,
                                 recipient=recipient)
    # Payement
    payment = Payment.objects.create()
    payment.lydias.add(lydia)
    payment.save()
    payment.maj_amount()

    sale.payment = payment
    sale.save()

    # Cr  dit
    user.credit(amount)


def sale_transfert(sender, recipient, amount, date, justification):
    """
    Création d'une vente avec ses dérivées basée sur un transfert
    """

    # Passage par le compte foyer
    d_b = DebitBalance.objects.create(amount=amount, sender=sender, recipient=recipient)

    # Payement
    p = Payment.objects.create()
    p.debit_balance.add(d_b)
    p.save()
    p.maj_amount()

    # Sale
    s = Sale.objects.create(date=date, sender=sender, operator=sender, recipient=recipient, payment=p,
                            category='transfert', justification=justification)

    # Produit vendu
    SingleProductFromContainer.objects.create(container=Container.objects.get(pk=1), quantity=amount*100,
                                              sale_price=amount, sale=s)

    s.maj_amount()

    # Débit / crédit
    sender.debit(s.amount)
    recipient.credit(s.amount)


def sale_recharging(sender, operator, date, wording, category='recharging', justification=None,
                    payments_list=None, amount=None):
    """
    Création d'une vente avec ses dérivées basée sur un rechargement
    Si payments_list=None, il faut renseigner amount. C'est le cas d'un rechargement sans produit
    """
    from users.models import User
    # Payement
    p = Payment.objects.create()

    if payments_list is None:
        # Pas de payement physique
        p.amount = amount
    else:
        # Passage par les payments listés dans payments_list
        for payment in payments_list:
            if isinstance(payment, Cash):
                p.cashs.add(payment)
            if isinstance(payment, Cheque):
                p.cheques.add(payment)
            if isinstance(payment, Lydia):
                p.lydias.add(payment)
        p.save()
        p.maj_amount()

    # Sale
    s = Sale.objects.create(date=date, sender=sender, operator=operator,
                            recipient=User.objects.get(username='AE_ENSAM'), payment=p, is_credit=True,
                            category=category, wording=wording, justification=justification)

    # Produit vendu
    SingleProductFromContainer.objects.create(container=Container.objects.get(pk=1), quantity=p.amount * 100,
                                              sale_price=p.amount, sale=s)

    s.maj_amount()

    # Débit / crédit
    sender.credit(s.amount)


def sale_sale(sender, operator, date, wording, category='sale', justification=None,
              payments_list=None, products_list=None, amount=None, to_return=None):
    """
    Création d'une vente avec ses dérivées basée sur une vente physique
    Lorsque payments_list=None, c'est que le payement se fait totalement par le compte foyer
    Si products_list = None, c'est qu'il n'y a pas de produit physique -> débit exceptionnel
    """
    from users.models import User

    # Payement
    p = Payment.objects.create()

    db = None
    if payments_list is None:
        # Pas de payement physique, tout est payé par le foyer
        db = DebitBalance.objects.create(sender=sender, recipient=User.objects.get(username='AE_ENSAM'))
        p.debit_balance.add(db)
        p.save()
    else:
        # Passage par les payments listés dans payments_list
        for payment in payments_list:
            if isinstance(payment, Cash):
                p.cashs.add(payment)
            if isinstance(payment, Cheque):
                p.cheques.add(payment)
            if isinstance(payment, Lydia):
                p.lydias.add(payment)
        p.save()
        p.maj_amount()

    # Sale
    s = Sale.objects.create(date=date, sender=sender, operator=operator,
                            recipient=User.objects.get(username='AE_ENSAM'), payment=p,
                            category=category, wording=wording, justification=justification)

    # Produits vendus
    if products_list is None:
        SingleProductFromContainer.objects.create(container=Container.objects.get(pk=1), quantity=amount * 100,
                                                  sale_price=amount, sale=s)
        s.maj_amount()
    else:
        for product in products_list:
            product.sale = s
            product.save()
        s.maj_amount()

    # Cas du payement total par compte foyer
    if payments_list is None:
        db.amount = s.amount
        db.save()
        p.maj_amount()

    # Débit / crédit
    sender.debit(s.amount)

    # Retour de la vente si besoin
    if to_return is True:
        return s


def sale_exceptionnal_movement(operator, affected, is_credit, amount, date, justification):
    """
    Création d'une vente avec ses dérivées basée sur un crédit / débit exceptionnel
    """
    if is_credit is True:
        sale_recharging(sender=affected, operator=operator, date=date, amount=amount,
                        category='exceptionnal_movement', wording='Mouvement exceptionnel', justification=justification)
    else:
        sale_sale(sender=affected, operator=operator, date=date, amount=amount,
                  category='exceptionnal_movement', wording='Mouvement exceptionnel', justification=justification)
