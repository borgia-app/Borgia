from django.db import models
from django.utils.timezone import now
from datetime import datetime
from decimal import Decimal
import json

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator

from shops.models import SingleProduct, SingleProductFromContainer, Container

# TODO: harmonization of methods name of Cash, Lydia, Cheque.
# TODO: harmonization of attributes singular/plurial (especially in Payment).


class Sale(models.Model):
    """
    Define a Sale between two users.

    The transaction is managed by an operator (which can the the sender
    directly if the sell is direct). Most of sale are between an User and the
    association (represented by the special User with username 'AE ENSAM').

    :param amount: consolidated amount of the sale, mandatory.
    :param date: date of sell, mandatory.
    :param done: true if the sell is closed, mandatory.
    :param is_credit: true when the objective is to give money the sender,
    mandatory.
    :param category: category of the sale, mandatory.
    :param wording: description of the sale, mandatory.
    :param justification: justification in case of exceptionnal movement.
    :param sender: sender of the sale, mandatory.
    :param recipient: recipient of the sale, mandatory.
    :param operator: operator of the sale, mandatory.
    :param payment: payement used by the sender to conclude the sale.
    :type amount: float (Decimal), default 0
    :type date: date string, default now
    :type done: boolean, default False
    :type is_credit: boolean, default False
    :type category: string, must be in CATEGORY_CHOICES, default 'sale'
    :type wording: string, must be in a specific list (to be defined)
    :type justification: string
    :type sender: User object
    :type recipient: User object
    :type operator: User object
    :type payment: Payment object
                              === Table 1: USER ===
    +----------+------------------+----------------------+--------------------+
    |   Type   |     Sender       |       Recipient      |      Operator      |
    +==========+==================+======================+====================+
    | Direct   | Buyer            | Association          | Buyer              |
    | sale     |                  |                      |                    |
    +----------+------------------+----------------------+--------------------+
    | Sale w/  | Buyer            | Association          | An operator        |
    | operator |                  |                      |                    |
    +----------+------------------+----------------------+--------------------+
    | Online   | Buyer            | Association          | Buyer              |
    | sale     |                  |                      |                    |
    +----------+------------------+----------------------+--------------------+
    | Lydia    | User             | Association          | User               |
    | self     |                  |                      |                    |
    | recharge |                  |                      |                    |
    +----------+------------------+----------------------+--------------------+
    | Recharge | User             | Association          | An operator        |
    | with an  |                  |                      |                    |
    | operator |                  |                      |                    |
    +----------+------------------+----------------------+--------------------+
    | Except-  | User debited     | Association          | An operator        |
    | ionnal   |                  | WARNING              |                    |
    | debit    |                  |                      |                    |
    +----------+------------------+----------------------+--------------------+
    | Except-  | User credited    | Association          | An operator        |
    | ionnal   |                  | WARNING              |                    |
    | credit   |                  |                      |                    |
    +----------+------------------+----------------------+--------------------+
    |Transfert | User debited     | User credited        | User debited       |
    +----------+------------------+----------------------+--------------------+

                            === Table 2: CATEGORIES ===
    +----------+-----------+----------------+----------------+----------------+
    |   Type   | is_credit |    Category    |     Wording    |  Justification |
    +==========+===========+================+================+================+
    | Direct   | False     | 'sale'         | 'Vente '       |                |
    | sale     |           |                | + shop.name    |                |
    +----------+-----------+----------------+----------------+----------------+
    | Sale w/  | False     | 'sale'         | 'Vente '       |                |
    | operator |           |                |                |                |
    +----------+-----------+----------------+----------------+----------------+
    | Online   | False     | 'sale'         | 'Vente '       |                |
    | sale     |           |                |                |                |
    +----------+-----------+----------------+----------------+----------------+
    | Lydia    | True      | 'recharging'   | 'Rechargement  |                |
    | self     |           |                | automatique'   |                |
    | recharge |           |                |                |                |
    +----------+-----------+----------------+----------------+----------------+
    | Recharge | True      | 'recharging'   | 'Rechargement  |                |
    | with an  |           |                | manuel'        |                |
    | operator |           |                |                |                |
    +----------+-----------+----------------+----------------+----------------+
    | Except-  | False     | 'exceptionnal_ | 'Mouvement     | Justification  |
    | ionnal   |           |  movement'     | exceptionnel'  |                |
    | debit    |           |                |                |                |
    +----------+-----------+----------------+----------------+----------------+
    | Except-  | True      | 'exceptionnal_ | 'Mouvement     | Justification  |
    | ionnal   |           |  movement'     | exceptionnel'  |                |
    | credit   |           |                |                |                |
    +----------+-----------+----------------+----------------+----------------+
    |Transfert | False     | 'transfert'    | ''             | Justification  |
    +----------+-----------+----------------+----------------+----------------+

                       === Table 3: PRODUCTS & PAYMENTS ===
    :note:: SP = SingleProduct, SPFC = SingleProductFromContainer
    +----------+------------------------------+-------------------------------+
    |   Type   |           Products           |          Payments             |
    +==========+==============================+===============================+
    | Direct   | List of bought products      | DebitBalance                  |
    | sale     | SP or SPFC                   |                               |
    +----------+------------------------------+-------------------------------+
    | Sale w/  | List of bought products      | DebitBalance                  |
    | operator | SP or SPFC                   |                               |
    +----------+------------------------------+-------------------------------+
    | Online   | List of bought products      | DebitBalance                  |
    | sale     | SP or SPFC                   |                               |
    +----------+------------------------------+-------------------------------+
    | Lydia    | SPFC of money                | Lydia                         |
    | self     |                              |                               |
    | recharge |                              |                               |
    +----------+------------------------------+-------------------------------+
    | Recharge | SPFC of money                | Lydia, Cash or Cheque         |
    | with an  |                              |                               |
    | operator |                              |                               |
    +----------+------------------------------+-------------------------------+
    | Except-  | SPFC of money                | DebitBalance                  |
    | ionnal   |                              |                               |
    | debit    |                              |                               |
    +----------+------------------------------+-------------------------------+
    | Except-  | SPFC of money                | None, but still a Payment     |
    | ionnal   |                              | with manually set amount      |
    | credit   |                              |                               |
    +----------+------------------------------+-------------------------------+
    |Transfert | SPFC of money                | DebitBalance                  |
    +----------+------------------------------+-------------------------------+

                             === Table 4: FUNCTIONS ===
    :note:: To fill parameters of such functions, please refer to tables 1 to
    3.
    +----------+--------------------------------------------------------------+
    |   Type   |                         Function                             |
    +==========+==============================================================+
    | Direct   | sale_sale                                                    |
    | sale     |                                                              |
    +----------+--------------------------------------------------------------+
    | Sale w/  | sale_sale                                                    |
    | operator |                                                              |
    +----------+--------------------------------------------------------------+
    | Online   | sale_sale                                                    |
    | sale     |                                                              |
    +----------+--------------------------------------------------------------+
    | Lydia    | sale_recharging                                              |
    | self     |                                                              |
    | recharge |                                                              |
    +----------+--------------------------------------------------------------+
    | Recharge | sale_recharging                                              |
    | with an  |                                                              |
    | operator |                                                              |
    +----------+--------------------------------------------------------------+
    | Except-  | sale_exceptionnal_movement (sale_sale)                       |
    | ionnal   |                                                              |
    | debit    |                                                              |
    +----------+--------------------------------------------------------------+
    | Except-  | sale_exceptionnal_movement (sale_recharging)                 |
    | ionnal   |                                                              |
    | credit   |                                                              |
    +----------+--------------------------------------------------------------+
    |Transfert | sale_transfert                                               |
    +----------+--------------------------------------------------------------+
    """
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
    sender = models.ForeignKey('users.User', related_name='sender_sale')
    recipient = models.ForeignKey('users.User', related_name='recipient_sale')
    operator = models.ForeignKey('users.User', related_name='operator_sale')
    payment = models.ForeignKey('Payment', blank=True, null=True)

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

    class Meta:
        """
        Define Permissions for Sale.
        """
        permissions = (
            ('retrieve_sale', 'Afficher une vente'),
            ('list_sale', 'Lister les ventes'),
            ('add_transfert', 'Effectuer un transfert d\'argent')
        )


class Payment(models.Model):
    """
    Define a Payment used in a Sale.

    This class only regroups kinds of payment (Cash, Lydia, Cheque, Balance)
    in order to have only one foreign key in the Sale.

    :param amount: consolidated amount of money payed by the Payment,
    mandatory.
    :param cheques: list of Cheque objects used in this Payment.
    :param cashs: list of Cash objects used in this Payment.
    :param lydias: list of Lydia objects used in this Payment.
    :param debit_balance: list of DebitBalance objects used in this Payment.

    :note:: There is always only one Payment for a Sale. However, each sub
    objects (Lydia, Cash, ...) a related to a specific User and can be
    multiple.
    """
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    cheques = models.ManyToManyField('Cheque', blank=True)
    cashs = models.ManyToManyField('Cash', blank=True)
    lydias = models.ManyToManyField('Lydia', blank=True)
    debit_balance = models.ManyToManyField('DebitBalance', blank=True)

    def __str__(self):
        """
        Return the display name of the Payment.

        :returns: 'payement' and the pk
        :rtype: string
        """
        return 'payement n°' + str(self.pk)

    def list_cheque(self):
        """
        Return the list of Cheque objects used in this Payment.

        :returns: list of Cheque objects (index 0), total amount (index 1)
        :rtype: list of Cheque objects (index 0), float (Decimal) (index 1)
        """
        list_cheque = Cheque.objects.filter(payment__cheques__payment=self)
        total_cheque = 0
        for e in list_cheque:
            total_cheque += e.amount
        return list_cheque, total_cheque

    def list_lydia(self):
        """
        Return the list of Lydia objects used in this Payment.

        :returns: list of Lydia objects (index 0), total amount (index 1)
        :rtype: list of Lydia objects (index 0), float (Decimal) (index 1)
        """
        list_lydia = Lydia.objects.filter(payment__lydias__payment=self)
        total_lydia = 0
        for e in list_lydia:
            total_lydia += e.amount
        return list_lydia, total_lydia

    def list_cash(self):
        """
        Return the list of Cash objects used in this Payment.

        :returns: list of Cash objects (index 0), total amount (index 1)
        :rtype: list of Cash objects (index 0), float (Decimal) (index 1)
        """
        list_cash = Cash.objects.filter(payment__cashs__payment=self)
        total_cash = 0
        for e in list_cash:
            total_cash += e.amount
        return list_cash, total_cash

    def list_debit_balance(self):
        """
        Return the list of DebitBalance objects used in this Payment.

        :returns: list of DebitBalance objects (index 0), total amount
        (index 1)
        :rtype: list of DebitBalance objects (index 0), float (Decimal)
        (index 1)
        """
        list_debit_balance = DebitBalance.objects.filter(
            payment__debit_balance__payment=self).distinct()
        total_debit_balance = 0
        for e in list_debit_balance:
            total_debit_balance += e.amount
        return list_debit_balance, total_debit_balance

    def maj_amount(self):
        """
        Set the amount attribute of the Payment to the right amount regarding
        sub payment.

        This attribute is here only to compute once in order to consolidate
        the database.

        :note:: This attribute is the total amount of the Sale. This amount
        can be payed by several Users at the same time. To know what each User
        pays, please refer to the method price_for of related Sale or each
        models (Cash, Lydia, ...) related to a specific User directly.
        """
        self.amount = (self.list_cheque()[1]
                       + self.list_lydia()[1]
                       + self.list_cash()[1]
                       + self.list_debit_balance()[1])
        self.save()

    def payments_used(self):
        """
        Return a list of string for each type of payment used.

        :returns: list of string of used payment
        :rtype: list of string

        :example:: If there is a cheque and 2 cashs, this function returns:
        ['Cheque', 'Lydia']
        """
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
    """
    Define a type of payment by the account saved by the association.

    :note:: Related to a unique User.

    :param amount: amount of the payment, mandatory.
    :param date: date of the payment, mandatory.
    :param sender: sender of the payment, mandatory.
    :param recipient: recipient of the payment, mandatory.
    :type amount: float (Decimal), default 0
    :type date: date string, default now
    :type sender: User object
    :type recipient: User object
    """
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    date = models.DateTimeField('Date', default=now)
    sender = models.ForeignKey('users.User',
                               related_name='sender_debit_balance')
    recipient = models.ForeignKey('users.User',
                                  related_name='recipient_debit_balance')

    def __str__(self):
        """
        Return the display name of a DebitBalance.

        :returns: amount and date of the DebitBalance
        :rtype: string
        """
        return str(self.amount) + '€ ' + str(self.date)

    def set_movement(self):
        """
        Debit / credit the sender of the DebitBalance of the amount.

        :note:: In practics amount is always > 0 regarding the sender.

        :warning:: DANGEROUS FUNCTION. This function should be deprecated.

        :warning:: This function must be used only in specific cases !
        For the general cases, use User object method credit and debit.
        """
        self.sender.balance -= self.amount
        self.sender.save()

    class Meta:
        """
        Define Permissions for DebitBalance.
        """
        permissions = (
            ('retrieve_debitbalance', 'Afficher un débit sur compte foyer'),
            ('list_debitbalance', 'Lister les débits sur comptes foyers'),
        )


class Cheque(models.Model):
    """
    Define a type of payment made by a bank cheque.

    :note:: Related to a unique User.

    :param amount: amount of the cheque (written on the paper), mandatory.
    :param is_cashed: true if the cheque is cashed by treasurers, mandatory.
    :param signature_date: signature date of the cheque (written on the paper),
    mandatory.
    :param cheque_number: number of the cheque (written on the paper),
    mandatory.
    :param sender: sender of the cheque (written on the paper), mandatory.
    :param recipient: recipient of the cheque (written on the paper),
    mandatory.
    :param bank_account: bank account of the cheque (written on the paper),
    mandatory.
    :type amount: float (Decimal), default 0
    :type is_cashed: boolean, default False
    :type signature_date: date string, default now
    :type cheque_number: string, must match ^[0-9]{7}$
    :type sender: User object
    :type recipient: User object
    :type bank_account: BankAccount object
    """
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    is_cashed = models.BooleanField('Est encaissé', default=False)
    signature_date = models.DateField('Date de signature', default=now)
    cheque_number = models.CharField('Numéro de chèque', max_length=7,
                                     validators=[
                                         RegexValidator('^[0-9]{7}$',
                                                        '''Numéro de chèque
                                                        invalide''')])
    sender = models.ForeignKey('users.User', related_name='cheque_sender')
    recipient = models.ForeignKey('users.User',
                                  related_name='cheque_recipient')
    bank_account = models.ForeignKey('BankAccount',
                                     related_name='cheque_bank_account')

    def __str__(self):
        """
        Return the display name of the Cheque.

        :returns: last and first name of the sender, amount and cheque number
        :rtype: string
        """
        return (self.sender.last_name
                + ' '
                + self.sender.first_name
                + ' '
                + str(self.amount)
                + '€ n°'
                + self.cheque_number)

    def list_payments(self):
        """
        Return the list of the Payment where this cheque is used.

        :note:: Theorically, a cheque can be used in several Payment. However,
        at time where these lines are written, it's not the case.

        :returns: list of Payment objects related to this cheque.
        :rtype: list of Payment objects
        """
        return Payment.objects.filter(cheques__payment__cheques=self)

    def list_sale(self):
        """
        Return the list of the Sale where this cheque is used, by Payment.

        :note:: Theorically, a cheque can be used in several Payment, thus in
        several Sale objects. However, at time where these lines are written,
        it's not the case.

        :returns: list of Sale objects related to this cheque.
        :rtype: list of Sale objects
        """
        return Sale.objects.filter(payment__cheques=self)

    class Meta:
        """
        Define Permissions for Cheque.
        """
        permissions = (
            ('retrieve_cheque', 'Afficher un cheque'),
            ('list_cheque', 'Lister les chèques'),
        )


class BankAccount(models.Model):
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
    owner = models.ForeignKey('users.User', related_name='owner_bank_account')

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
            ('add_own_bankaccount', 'Ajouter un compte en banque personnel'),
            ('list_bankaccount', 'Lister les comptes en banque'),
        )


class Cash(models.Model):
    """
    Define a type of payment made by a phycial money (cash).

    :note:: Related to a unique User.

    :param amount: amount of cash.
    :param sender: sender of cash.
    :param recipient: recipient of the cheque (written on the paper).
    :type amount: float (Decimal), default 0
    :type sender: User object
    :type recipient: User object
    """
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    sender = models.ForeignKey('users.User', related_name='cash_sender')
    recipient = models.ForeignKey('users.User', related_name='cash_recipient')

    def __str__(self):
        """
        Return the display name of a Cash.

        :returns: sender's last and first name and amount
        :rtype: string
        """
        return (self.sender.last_name
                + ' '
                + self.sender.first_name
                + ' '
                + str(self.amount)
                + '€')

    def list_sale(self):
        """
        Return the list of the Sale where this Cash is used, by Payment.

        :note:: Theorically, a cash can be used in several Payment, thus in
        several Sale objects. However, at time where these lines are written,
        it's not the case.

        :returns: list of Sale objects related to this cash.
        :rtype: list of Sale objects
        """
        return Sale.objects.filter(payment__cashs=self)

    def list_payment(self):
        """
        Return the list of the Payment where this Cash is used.

        :note:: Theorically, a cash can be used in several Payment. However,
        at time where these lines are written, it's not the case.

        :returns: list of Payment objects related to this cash.
        :rtype: list of Payment objects
        """
        return Payment.objects.filter(cashs__payment__cashs=self)

    class Meta:
        """
        Define Permissions for Cash.
        """
        permissions = (
            ('retrieve_cash', 'Afficher des espèces'),
            ('list_cash', 'Lister les espèces'),
        )


class Lydia(models.Model):
    """
    Define a transaction by the provider Lydia.

    :note:: Related to an unique User.

    :param date_operation: date of transaction, mandatory.
    :param amount: money in transaction, mandatory.
    :param id_from_lydia: unique number given by the provider for each
    transaction, mandatory. Must be unique.
    :param sender: sender of the money, mandatory.
    :param recipient: recipient of the money, mandatory.
    :param banked: true if the money was banked by treasurer, mandatory.
    :param date_banked: only if banked is true.
    :type date_operation: date string, default now
    :type amount: float (Decimal), default 0
    :type id_from_lydia: string
    :type sender: User object
    :type recipient: user object
    :type banked: boolean, default False
    :type date_banked: fate string
    """
    date_operation = models.DateField('Date', default=now)
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])
    id_from_lydia = models.CharField('Numéro unique', max_length=255,
                                     unique=True)
    sender = models.ForeignKey('users.User', related_name='lydia_sender')
    recipient = models.ForeignKey('users.User', related_name='lydia_recipient')
    banked = models.BooleanField('Est encaissé', default=False)
    date_banked = models.DateField('Date encaissement', blank=True, null=True)

    def __str__(self):
        """
        Return the display name of a Lydia transaction.

        :returns: sender's last name, first name and amount.
        :rtype: string
        """
        return (self.sender.last_name
                + ' '
                + self.sender.first_name
                + ' '
                + str(self.amount)
                + '€')

    def list_transaction(self):
        """
        Return the list of the Sale where this Lydia is used, by Payment.

        :note:: Theorically, a cheque can be used in several Payment, thus in
        several Sale objects. However, at time where these lines are written,
        it's not the case.

        :returns: list of Sale objects related to this Lydia.
        :rtype: list of Sale objects

        :note:: Should be named list_sale as in Cash and Cheque model.
        """
        return Sale.objects.filter(payment__lydias=self)

    class Meta:
        """
        Define Permissions for Lydia.
        """
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
    manager = models.ForeignKey('users.User', related_name='manager')
    sale = models.ForeignKey('Sale', null=True, blank=True)
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


# No longer used
def supply_self_lydia(user, recipient, amount, transaction_identifier):
    """
    Supply a user by a Lydia self transaction with the Lydia Application.

    This function is used in the module Lydia Self Supply which let an User
    supply himself money to his account by debit card or directly with money
    on his Lydia account.

    :note:: This function is longer used ! Please refer to sale_recharging.

    :param user: user supplied, mandatory.
    :param recipient: recipient, mandatory.
    :param amount: amount of money supplied by Lydia, mandatory.
    :param transaction_identifier: id for Lydia transaction, mandatory.
    :type user: User object
    :type recipient: User object
    :type amount: float (Decimal)
    :type transaction_identifier: string

    This function creates a Lydia payment. It links it to a new Payment object,
    and finally links it to a new Sale object. The user is credited of the
    amount of money.

    :note:: We should debit the association user.
    """
    container = Container.objects.get(pk=1)

    sale = Sale.objects.create(date=datetime.now(),
                               sender=user,
                               recipient=recipient,
                               operator=user,
                               is_credit=True,
                               category='recharging',
                               wording='Rechargement automatique')

    SingleProductFromContainer.objects.create(container=container,
                                              sale=sale,
                                              quantity=amount*100,
                                              sale_price=amount)
    sale.maj_amount()

    lydia = Lydia.objects.create(date_operation=datetime.now(),
                                 amount=amount,
                                 id_from_lydia=transaction_identifier,
                                 sender=user,
                                 recipient=recipient)

    payment = Payment.objects.create()
    payment.lydias.add(lydia)
    payment.save()
    payment.maj_amount()

    sale.payment = payment
    sale.save()

    user.credit(amount)


def sale_transfert(sender, recipient, amount, date, justification):
    """
    Create a Sale object for a transfert from an account to another account.

    This function is used for transferts only. Refer to other sale functions
    for other cases.

    :param sender: sender of the transfert, the debited user. Mandatory.
    :param recipient: recipient of the transfert, the credited user.
    Mandatory.
    :param amount: amount of the transfert, mandatory.
    :param date: date of the transfert, mandatory.
    :param justification: description of the transfert, mandatory.
    :type sender: User object
    :type recipient: User object
    :type amount: float (Decimal)
    :type date: date string
    :type justification: string

    This function creates a DebitBalance object, links it to a new Payment and
    links it to a new Sale object. The sender is debited of amount and the
    recipient credited of the amount.
    """

    d_b = DebitBalance.objects.create(amount=amount, sender=sender,
                                      recipient=recipient)

    p = Payment.objects.create()
    p.debit_balance.add(d_b)
    p.save()
    p.maj_amount()

    s = Sale.objects.create(date=date, sender=sender, operator=sender,
                            recipient=recipient, payment=p,
                            category='transfert', justification=justification)

    SingleProductFromContainer.objects.create(
        container=Container.objects.get(pk=1),
        quantity=amount*100,
        sale_price=amount,
        sale=s)

    s.maj_amount()

    sender.debit(s.amount)
    recipient.credit(s.amount)

    s.done = True
    s.save()


def sale_recharging(sender, operator, date, wording, category='recharging',
                    justification=None,
                    payments_list=None, amount=None):
    """
    Create a Sale for recharging an User.

    This function can be used to supply money to an User object when it give
    money to the association (it is then just a trade, the account of the user
    is supplied). In this case payment methods (Cash, Lydia, Cheque) must be
    defined before calling the application and list them in payments_list. This
    function will create a Payment object, grouping all payment.
    Moreover this function can be used to supply an User object for an
    exceptionnal movement, for instance to repay someone after an error. Then,
    no money is given to the association and payments_list is None.

    :param sender: user who want to be recharged, mandatory. In both case, it's
    the user who is recharged, even if the proper sender is not himself for
    the case of exceptionnal movement for instance.
    :param operator: user who supply money by the account of the association,
    mandatory.
    :param date: date of the recharge, mandatory.
    :param wording: subtype of the recharge, mandatory.
    :param category: category of the recharge. Could be 'exceptionnal_movement'
    :param justification: justification in the case of exceptionnal movement.
    :param payments_list: list of payment objects in the case of regular
    recharge (Cash, Lydia or Cheque).
    :param amount: amount of the recharge, only for exceptionnal movement. If
    not the amount is calculated from payment objects.
    :type sender: User object
    :type operator: User object
    :type date: date string
    :type wording: string
    :type category: string, default 'recharging'
    :type justification: string, default None
    :type payments_list: list of Cash, Lydia or Cheque objects, default None
    :type amount: amount of the exceptionnal movement, default None

    :note:: We should debit the association.
    """
    from users.models import User

    p = Payment.objects.create()

    if payments_list is None:
        p.amount = amount
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
                            payment=p, is_credit=True,
                            category=category, wording=wording,
                            justification=justification)

    SingleProductFromContainer.objects.create(
        container=Container.objects.get(pk=1),
        quantity=p.amount * 100,
        sale_price=p.amount, sale=s)
    s.maj_amount()

    sender.credit(s.amount)

    s.done = True
    s.save()


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


def sale_exceptionnal_movement(operator, affected, is_credit, amount, date,
                               justification):
    """
    Create a Sale for an exceptionnal credit or debit.

    :param operator: manager of the exceptionnal movement, mandatory.
    :param affected: user who is debited or credited, mandatory.
    :param is_credit: true if the user if credited, mandatory.
    :param amount: amount of the credit / debit, mandatory. Must be always
    strictly positiv. Is_credit define it it's a credit or not.
    :param date: date of the movement, mandatory.
    :param justification: justification to use an exceptionnal movement,
    mandatory.
    :type operator: User object
    :type affected: User object
    :type is_credit: boolean
    :type amount: float (Decimal), strictly positiv.
    :type date: date string
    :type justification: string

    :note:: In the case of credit, this function uses the function
    sale_recharging. In the case of debit, it uses a regular sale, function
    sale_sale.
    """
    if is_credit is True:
        sale_recharging(sender=affected, operator=operator, date=date,
                        amount=amount, category='exceptionnal_movement',
                        wording='Mouvement exceptionnel',
                        justification=justification)
    else:
        sale_sale(sender=affected, operator=operator, date=date, amount=amount,
                  category='exceptionnal_movement',
                  wording='Mouvement exceptionnel',
                  justification=justification)
