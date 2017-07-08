from django.db import models
from django.utils.timezone import now
from decimal import Decimal
import json

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ObjectDoesNotExist

from shops.models import (SingleProduct, SingleProductFromContainer, Container,
                          Shop)

from notifications.models import notify

# TODO: harmonization of methods name of Cash, Lydia, Cheque.
# TODO: harmonization of attributes singular/plurial (especially in Payment).
# TODO: shared_event line in tables users, products/payments and function.


class Sale(models.Model):
    # TODO: define the list of possible wordings.

    CATEGORY_CHOICES = (('transfert', 'Transfert'),
                        ('recharging', 'Rechargement'), ('sale', 'Vente'),
                        ('exceptionnal_movement', 'Mouvement exceptionnel'),
                        ('shared_event', 'Evénement'))
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    date = models.DateTimeField('Date', default=now)
    done = models.BooleanField('Terminée', default=False)
    is_credit = models.BooleanField('Est un crédit', default=False)
    category = models.CharField('Catégorie', choices=CATEGORY_CHOICES,
                                default='sale', max_length=50)
    wording = models.CharField('Libellé', default='', max_length=254)
    justification = models.TextField('Justification', null=True, blank=True)
    sender = models.ForeignKey('users.User', related_name='sender_sale',
    on_delete=models.CASCADE)
    recipient = models.ForeignKey('users.User', related_name='recipient_sale',
    on_delete=models.CASCADE)
    operator = models.ForeignKey('users.User', related_name='operator_sale',
    on_delete=models.CASCADE)
    payment = models.ForeignKey('Payment', blank=True, null=True,
    on_delete=models.CASCADE)

    def __str__(self):
        """
        Return the display name of the Sale.

        :returns: pk of sale
        :rtype: string
        """
        return 'Achat n°' + str(self.pk)

    def list_single_products(self):
        """
        Return the list of SingleProduct objects bought in this Sale.

        :returns: List of SingleProduct objects (index 0) and total price of
        these products (index 1)
        :rtype: List of SingleProduct objects (index 0), float (Decimal)
        (index 1)
        """
        list_single_product = SingleProduct.objects.filter(sale=self)
        total_sale_price = 0
        for e in list_single_product:
            total_sale_price += e.sale_price
        return list_single_product, total_sale_price

    def list_single_products_from_container(self):
        """
        Return the list of SingleProductFromContainer objects bought in this
        Sale.

        :returns: List of SingleProductFromContainer objects (index 0) and
        total price of these products (index 1)
        :rtype: List of SingleProductFromContainer objects (index 0), float
        (Decimal) (index 1)
        """
        list_single_product_from_container = (
            SingleProductFromContainer.objects.filter(sale=self))
        total_sale_price = 0
        for e in list_single_product_from_container:
            total_sale_price += e.sale_price
        return list_single_product_from_container, total_sale_price

    def list_shared_events(self):
        """
        Return the list of SharedEvent objects bought in this Sale.

        :returns: List of SharedEvent objects (index 0) and total price of
        these products (index 1)
        :rtype: List of SharedEvent objects (index 0), float (Decimal)
        (index 1)
        """
        list_shared_event = SharedEvent.objects.filter(sale=self)
        total_sale_price = 0
        for e in list_shared_event:
            total_sale_price += e.price
        return list_shared_event, total_sale_price

    def maj_amount(self):
        """
        Set the amount attribute of the Sale to the right amount regarding
        bought products.

        This attribute is here only to compute once in order to consolidate
        the database.

        :note:: This attribute is the total amount of the Sale. This amount
        can be payed by several Users at the same time. To know what each User
        pays, please refer to the method price_for.
        """
        self.amount = (self.list_single_products()[1]
                       + self.list_single_products_from_container()[1]
                       + self.list_shared_events()[1])
        self.save()

    def price_for(self, user):
        """
        Return the sale price for an User.

        In several cases, multiply users can be related to the same Sale. This
        is the case for SharedEvent by definition. Thus this function let you
        know the amount payed by a specific User, which is different of the
        amount attrite of the Sale. It's based on Payement objects managed by
        the User.

        :returns: the price the User payed for this Sale.
        :rtype: float (Decimal)

        :note:: In the case of debit of the User, the returned amount is
        negativ, positiv in the case of credit.
        """
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
        """
        Return a formated string concerning all products in this Sale.

        :returns: each __str__ of products, separated by a comma.
        :rtype: string

        :note:: Why do SharedEvents are excluded ?
        """
        string = ''
        for p in self.list_single_products()[0]:
            string += p.__str__() + ', '
        for p in self.list_single_products_from_container()[0]:
            string += p.__str__() + ', '
        string = string[0: len(string)-2]
        return string

    def from_shop(self):
        try:
            return Shop.objects.get(name=self.wording.split(' ')[1])
        except ObjectDoesNotExist:
            return None
        except IndexError:
            return None

    class Meta:
        """
        Define Permissions for Sale.
        """
        permissions = (
            ('retrieve_sale', 'Afficher une vente'),
            ('list_sale', 'Lister les ventes'),
            ('retrieve_recharging', 'Afficher un rechargement'),
            ('list_recharging', 'Lister les rechargements'),
            ('add_transfert', 'Effectuer un transfert d\'argent'),
            ('retrieve_transfert', 'Afficher un transfert'),
            ('list_transfert', 'Lister les transferts'),
            ('add_exceptionnal_movement',
             'Faire un mouvement exceptionnel'),
            ('retrieve_exceptionnal_movement',
             'Afficher un mouvement exceptionnel'),
            ('list_exceptionnal_movement',
             'Lister les mouvements exceptionnels')
        )


class Recharging(models.Model):
    datetime = models.DateTimeField('Date', default=now)
    sender = models.ForeignKey('users.User', related_name='sender_recharging',
    on_delete=models.CASCADE)
    operator = models.ForeignKey('users.User', related_name='operator_recharging',
    on_delete=models.CASCADE)
    payment_solution = models.ForeignKey('PaymentSolution', on_delete=models.CASCADE)

    def pay(self):
        self.sender.credit(self.payment_solution.amount)


class PaymentSolution(models.Model):
    sender = models.ForeignKey('users.User', related_name='payment_sender',
    on_delete=models.CASCADE)
    recipient = models.ForeignKey('users.User',
                                  related_name='payment_recipient',
                                  on_delete=models.CASCADE)
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])


class Cheque(PaymentSolution):
    """
    Define a type of payment made by a bank cheque.

    :note:: Related to a unique User.

    :param is_cashed: true if the cheque is cashed by treasurers, mandatory.
    :param signature_date: signature date of the cheque (written on the paper),
    mandatory.
    :param cheque_number: number of the cheque (written on the paper),
    mandatory.
    :param bank_account: bank account of the cheque (written on the paper),
    mandatory.
    :type is_cashed: boolean, default False
    :type signature_date: date string, default now
    :type cheque_number: string, must match ^[0-9]{7}$
    :type bank_account: BankAccount object
    """
    is_cashed = models.BooleanField('Est encaissé', default=False)
    signature_date = models.DateField('Date de signature', default=now)
    cheque_number = models.CharField('Numéro de chèque', max_length=7,
                                     validators=[
                                         RegexValidator('^[0-9]{7}$',
                                                        '''Numéro de chèque
                                                        invalide''')])
    bank_account = models.ForeignKey('BankAccount',
                                     related_name='cheque_bank_account',
                                     on_delete=models.CASCADE)
    class Meta:
        """
        Define Permissions for Cheque.
        """
        permissions = (
        )


class BankAccount(PaymentSolution):
    """
    Define a bank account owned by an User.

    Such information are used in order to identify in an unique way a Cheque
    (BankAccount + cheque number).

    :param bank: name of the bank, mandatory.
    :param account: account number, mandatory.
    :param owner: owner of the account, mandatory.
    :type bank: string
    :type account: string
    :type owner: User object
    """
    bank = models.CharField('Banque', max_length=255)
    account = models.CharField('Numéro de compte', max_length=255)
    owner = models.ForeignKey('users.User', related_name='owner_bank_account',
    on_delete=models.CASCADE)

    def __str__(self):
        """
        Return the display name of a BankAccount.

        :returns: bank name and account number
        :rtype: string
        """
        return (self.bank
                + ' '
                + self.account)

    class Meta:
        """
        Define Permissions for BankAccount.
        """
        permissions = (
            ('retrieve_bankaccount', 'Afficher un compte en banque'),
            ('list_bankaccount', 'Lister les comptes en banque'),
        )


class Cash(PaymentSolution):
    """
    Define a type of payment made by a phycial money (cash).

    :note:: Related to a unique User.

    """
    pass

    class Meta:
        """
        Define Permissions for Cash.
        """
        permissions = (
        )


class LydiaFaceToFace(PaymentSolution):
    """
    Define a transaction by the provider Lydia.

    :note:: Related to an unique User.

    :param date_operation: date of transaction, mandatory.
    :param id_from_lydia: unique number given by the provider for each
    transaction, mandatory. Must be unique.
    :param banked: true if the money was banked by treasurer, mandatory.
    :param date_banked: only if banked is true.
    :type date_operation: date string, default now
    :type id_from_lydia: string
    :type banked: boolean, default False
    :type date_banked: fate string
    """
    date_operation = models.DateField('Date', default=now)
    id_from_lydia = models.CharField('Numéro unique', max_length=255)
    banked = models.BooleanField('Est encaissé', default=False)
    date_banked = models.DateField('Date encaissement', blank=True, null=True)

    class Meta:
        """
        Define Permissions for Lydia.
        """
        permissions = (
        )


class LydiaOnline(PaymentSolution):
    """
    Define a transaction by the provider Lydia, online.

    :note:: Related to an unique User.

    :param date_operation: date of transaction, mandatory.
    :param id_from_lydia: unique number given by the provider for each
    transaction, mandatory. Must be unique.
    :param banked: true if the money was banked by treasurer, mandatory.
    :param date_banked: only if banked is true.
    :type date_operation: date string, default now
    :type id_from_lydia: string
    :type banked: boolean, default False
    :type date_banked: fate string
    """
    date_operation = models.DateField('Date', default=now)
    id_from_lydia = models.CharField('Numéro unique', max_length=255)
    banked = models.BooleanField('Est encaissé', default=False)
    date_banked = models.DateField('Date encaissement', blank=True, null=True)

    class Meta:
        """
        Define Permissions for Lydia.
        """
        permissions = (
        )


class Transfert(models.Model):
    datetime = models.DateTimeField('Date', default=now)
    justification = models.TextField('Justification', null=True, blank=True)
    sender = models.ForeignKey('users.User', related_name='sender_transfert',
    on_delete=models.CASCADE)
    recipient = models.ForeignKey('users.User', related_name='recipient_transfert',
    on_delete=models.CASCADE)
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])

    def pay(self):
        self.sender.debit(self.amount)
        self.recipient.credit(self.amount)


class ExceptionnalMovement(models.Model):
    datetime = models.DateTimeField('Date', default=now)
    justification = models.TextField('Justification', null=True, blank=True)
    operator = models.ForeignKey('users.User', related_name='sender_exceptionnal_movement',
    on_delete=models.CASCADE)
    recipient = models.ForeignKey('users.User', related_name='recipient_exceptionnal_movement',
    on_delete=models.CASCADE)
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    is_credit = models.BooleanField(default=False)

    def pay(self):
        if self.is_credit:
            self.recipient.credit(self.amount)
        else:
            self.recipient.debit(self.amount)


class SharedEvent(models.Model):
    """
    Une évènement partagé et payé par plusieurs personnes
    ex: un repas

    Remarque :
    les participants sont dans la relation m2m participants.
    Cependant, cette liste n'est pas ordonnée et deux demande de query peuvent
    renvoyer deux querys ordonnés différement
    Du coup on stocke le duo [participant_pk, ponderation] dans une liste
    dumpé
    JSON dans le string "ponderation"
    Je garde le m2m participants pour avoir quand même un lien plus simple
    (pour les recherches etc.)
    Lors de la suppression / ajout il faut utiliser les méthodes
    add_participant et remove_participant pour faire ca
    proprement.
    """
    description = models.CharField('Description', max_length=254)
    date = models.DateField('Date', default=now)
    price = models.DecimalField('Prix', decimal_places=2, max_digits=9,
                                null=True, blank=True,
                                validators=[MinValueValidator(Decimal(0))])
    bills = models.CharField('Facture(s)', max_length=254, null=True,
                             blank=True)
    done = models.BooleanField('Terminé', default=False)
    remark = models.CharField('Remarque', max_length=254, null=True,
                             blank=True)
    manager = models.ForeignKey('users.User', related_name='manager',
        on_delete=models.CASCADE)
    sale = models.ForeignKey('Sale', null=True, blank=True,
        on_delete=models.CASCADE)
    participants = models.ManyToManyField('users.User', blank=True,
                                          related_name='participants')
    registered = models.ManyToManyField('users.User', blank=True,
                                        related_name='registered')
    ponderation = models.CharField(
        'Liste ordonnée participants - pondérations',
        max_length=10000, default='[]')

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
        :return: liste ponderation [[user_pk, ponderation], [user_pk,
        ponderation], ...]
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

        # Suppresion du premier élément de pondération qui correspond à
        # l'user_pk
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

        # Enregistrement dans une nouvelle liste (le traitement direct sur
        # get_ponderation() ne semble pas fonctionner)
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
        Forme une liste des participants [[user, ponderation],
        [user, ponderation]] à partir de la liste ponderation
        :return: liste_u_p [[user, ponderation], [user, ponderation]]
        """
        list_u_p = []
        for e in self.get_ponderation():
            list_u_p.append([get_user_model().objects.get(pk=e[0]), e[1]])
        return list_u_p

    def list_of_registered_ponderation(self):
        """
        Forme une liste des inscrits [[user, 1], [user, 1]] à partir des
        inscrits. La pondération d'un inscrit est toujours de 1
        :return: liste_u_p [[user, 1], [user, 1]]
        """
        list_u_p = []
        for u in self.registered.all():
            list_u_p.append([u, 1])
        return list_u_p

    def pay(self, operator, recipient):
        """
        Procède au paiement de l'évenement par les participants.
        Une seule vente, un seul paiement mais plusieurs débits sur compte
        (un par participant)
        :param operator: user qui procède au paiement
        :param recipient: user qui recoit les paiements (AE_ENSAM)
        :return:
        """
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
            d_b = DebitBalance.objects.create(
                amount=price_per_participant*u[1],
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
        self.remark = 'Paiement par Borgia'
        self.save()

    class Meta:
        """
        Define Permissions for SharedEvent.
        """
        permissions = (
            ('register_sharedevent', 'S\'inscrire à un événement commun'),
            ('list_sharedevent', 'Lister les événements communs'),
            ('manage_sharedevent', 'Gérer les événements communs'),
            ('proceed_payment_sharedevent',
             'Procéder au paiement des événements communs'),
        )


def sale_sale(sender, operator, date, wording, category='sale',
              justification=None, payments_list=None, products_list=None,
              amount=None, to_return=None):
    """
    Create a Sale for a regular sale between a member and the association.

    This function is used when the association sells something to a member.
    Moreover it could be used for an exceptionnal debit (please refer to
    sale_recharging for exceptionnal credit). This case is considered to be
    a sale of an object not in the database.

    :param sender: user who buy something, mandatory. For exceptionnal debit
    it is the user who is debited.
    :param operator: user who manage the sell. Some modules let the buyer
    manage himself the sell (direct sell for instance). Mandatory.
    :param date: date of the sale, mandatory.
    :param wording: subtype of the sell, mandatory.
    :param category: category of the sell. Could be 'exceptionnal_movement'.
    :param justification: justification in the case of exceptionnal movement.
    :param payments_list: list of payment objects used (Cash, Lydia or Cheque).
    If not it indicates that the user want to pay with DebitBalance.
    :param products_list: list of products bought by the user. If None it's an
    exceptionnal movement.
    :param amount: amount of the sale, only for exceptionnal movement. If
    not the amount is calculated from products objects.
    :param to_return: if true the function return the created Sale.
    :type sender: User object
    :type operator: User object
    :type date: date string
    :type wording: string
    :type category: string, default 'sale'
    :type justification: string, default None
    :type payments_list: list of payment objects (Cash, Lydia or Cheque),
    default None
    :type products_list: list of products objects (SingleProduct or
    SingleProductFromContainer)
    :type amount: float (Decimal), default None
    :type to_return: boolean, default False

    :returns: the created Sale if to_return is True only, nothing instead.
    :type: Sale object if to_return is True only, nothing instead.

    :note:: We should debit the association.
    :note:: Product must be sent without sale but with a sale_price. For
    SingleProduct is_sold should be True.
    :note:: Setting attributes such as sale_price and is_sold should be made
    inside this function directly. Thus, products sent are clean.
    """
    from users.models import User

    p = Payment.objects.create()

    db = None
    if payments_list is None:
        db = DebitBalance.objects.create(sender=sender,
                                         recipient=User.objects.get(
                                             username='AE_ENSAM'))
        p.debit_balance.add(db)
        p.save()
    else:
        for payment in payments_list:
            if isinstance(payment, Cash):
                p.cashs.add(payment)
            if isinstance(payment, Cheque):
                p.cheques.add(payment)
            if isinstance(payment, Lydia):
                p.lydias.add(payment)
        p.save()
        p.maj_amount()

    s = Sale.objects.create(date=date, sender=sender, operator=operator,
                            recipient=User.objects.get(username='AE_ENSAM'),
                            payment=p, category=category, wording=wording,
                            justification=justification)

    if products_list is None:
        SingleProductFromContainer.objects.create(
            container=Container.objects.get(pk=1),
            quantity=amount * 100,
            sale_price=amount,
            sale=s)
        s.maj_amount()
    else:
        for product in products_list:
            product.sale = s
            product.is_sold = True
            product.save()
        s.maj_amount()

    if payments_list is None:
        db.amount = s.amount
        db.save()
        p.maj_amount()

    sender.debit(s.amount)

    s.done = True
    s.save()

    if to_return is True:
        return s
