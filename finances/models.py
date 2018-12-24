import decimal

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.timezone import now

from shops.models import Product, Shop
from users.models import User

# TODO: harmonization of methods name of Cash, Lydia, Cheque.
# TODO: harmonization of attributes singular/plurial (especially in Payment).
# TODO: event line in tables users, products/payments and function.
# TODO (by eyap) : make the class PaymentSolution overridable (See Abstract) and implement type in children


class Sale(models.Model):
    """
    Define a Sale between two users.

    The transaction is managed by an operator (which can the the sender
    directly if the sell is direct). Most of sale are between an User and the
    association (represented by the special User with username 'AE ENSAM').

    :param datetime: date of sell, mandatory.
    :param sender: sender of the sale, mandatory.
    :param recipient: recipient of the sale, mandatory.
    :param operator: operator of the sale, mandatory.

    NEW IMPLMENTATION
    :param content_type:
    :param module_id:
    :param module:
    :param shop:
    :param products:


    :type datetime: date string, default now
    :type sender: User object
    :type recipient: User object
    :type operator: User object

    NEW IMPLMENTATION
    :type content_type:
    :type module_id:
    :type module:
    :type shop: Shop object
    :type products: Product object

    :note:: Initial Django Permission (add, change, delete, view) are added.
    """
    datetime = models.DateTimeField('Date', default=now)
    sender = models.ForeignKey(User, related_name='sender_sale',
                               on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='recipient_sale',
                                  on_delete=models.CASCADE)
    operator = models.ForeignKey(User, related_name='operator_sale',
                                 on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    module_id = models.PositiveIntegerField()
    module = GenericForeignKey('content_type', 'module_id')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='SaleProduct')

    def __str__(self):
        """
        Return the display name of the Sale.

        :returns: pk of sale
        :rtype: string
        """
        return 'Achat n°' + str(self.pk)

    def pay(self):
        self.sender.debit(self.amount())

    def wording(self):
        return 'Achat ' + self.shop.__str__() + ', ' + self.string_products()

    def string_products(self):
        """
        Return a formated string concerning all products in this Sale.

        :returns: each __str__ of products, separated by a comma.
        :rtype: string

        :note:: Why do Events are excluded ?
        """
        string = ''
        for sp in self.saleproduct_set.all():
            string += sp.__str__() + ', '
        string = string[0: len(string)-2]
        return string

    def from_shop(self):
        try:
            return self.module.shop
        except ObjectDoesNotExist:
            return None
        except IndexError:
            return None

    def amount(self):
        amount = 0
        for sp in self.saleproduct_set.all():
            amount += sp.price
        return amount


class SaleProduct(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField('Prix', default=0, decimal_places=2,
                                max_digits=9,
                                validators=[MinValueValidator(decimal.Decimal(0))])

    class Meta:
        """
        Remove default permissions for StockEntryProduct
        """
        default_permissions = ()

    def __str__(self):
        if self.product.unit:
            return self.product.__str__() + ' x ' + str(self.quantity) + self.product.get_unit_display()
        else:
            if self.quantity > 1:
                return self.product.__str__() + ' x ' + str(self.quantity)
            else:
                return self.product.__str__()


class PaymentSolution(models.Model):
    sender = models.ForeignKey(User, related_name='payment_sender',
                               on_delete=models.CASCADE)
    recipient = models.ForeignKey(User,
                                  related_name='payment_recipient',
                                  on_delete=models.CASCADE)
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(decimal.Decimal(0))])

    class Meta:
        """
        Remove default permissions for PaymentSolution
        """
        default_permissions = ()

    def get_type(self):
        try:
            self.cash
            return 'cash'
        except ObjectDoesNotExist:
            try:
                self.cheque
                return 'cheque'
            except ObjectDoesNotExist:
                try:
                    self.lydiafacetoface
                    return 'lydiafacetoface'
                except ObjectDoesNotExist:
                    try:
                        self.lydiaonline
                        return 'lydiaonline'
                    except ObjectDoesNotExist:
                        return None

    def get_display_type(self):
        payment_type = self.get_type()
        if payment_type == 'cash':
            return 'espèces'
        if payment_type == 'cheque':
            return 'chèque'
        if payment_type == 'lydiafacetoface':
            return 'lydia face à face'
        if payment_type == 'lydiaonline':
            return 'lydia en ligne'
        return None


class Cheque(PaymentSolution):
    """
    Define a type of payment made by a bank cheque.

    :note:: Related to a unique User.

    :param is_cashed: true if the cheque is cashed by treasurers, mandatory.
    :param signature_date: signature date of the cheque (written on the paper),
    mandatory.
    :param cheque_number: number of the cheque (written on the paper),
    mandatory.
    :type is_cashed: boolean, default False
    :type signature_date: date string, default now
    :type cheque_number: string, must match ^[0-9]{7}$
    """
    is_cashed = models.BooleanField('Est encaissé', default=False)
    signature_date = models.DateField('Date de signature', default=now)
    cheque_number = models.CharField('Numéro de chèque', max_length=7,
                                     validators=[
                                         RegexValidator('^[0-9]{7}$',
                                                        '''Numéro de chèque
                                                        invalide''')])

    class Meta:
        """
        Remove default permissions for Cheque
        """
        default_permissions = ()

    def __str__(self):
        return 'Cheque n°' + self.cheque_number


class Cash(PaymentSolution):
    """
    Define a type of payment made by a phycial money (cash).

    :note:: Related to a unique User.
    """

    class Meta:
        """
        Remove default permissions for Cash
        """
        default_permissions = ()


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
        Remove default permissions for LydiaFaceToFace
        """
        default_permissions = ()

    def __str__(self):
        return 'Payement Lydia n°' + self.id_from_lydia


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
        Remove default permissions for LydiaOnline
        """
        default_permissions = ()

    def __str__(self):
        return 'Payement Lydia n°' + self.id_from_lydia


class Recharging(models.Model):
    """
    Allow a operator to recharge (supply money) the balance of a sender
    """
    datetime = models.DateTimeField('Date', default=now)
    sender = models.ForeignKey(User, related_name='sender_recharging',
                               on_delete=models.CASCADE)
    operator = models.ForeignKey(User, related_name='operator_recharging',
                                 on_delete=models.CASCADE)
    payment_solution = models.ForeignKey(PaymentSolution, on_delete=models.CASCADE)

    class Meta:
        """
        Define Permissions for Recharging.

        :note:: Initial Django Permission (add, view) are added.
        """
        default_permissions = ('add', 'view',)

    def wording(self):
        if self.payment_solution.get_type() == 'cash':
            return 'Rechargement par espèces'
        if self.payment_solution.get_type() == 'cheque':
            return 'Rechargement par chèque'
        if self.payment_solution.get_type() == 'lydiafacetoface':
            return 'Rechargement par Lydia en face à face'
        if self.payment_solution.get_type() == 'lydiaonline':
            return 'Rechargement par Lydia en ligne'

    def amount(self):
        return self.payment_solution.amount

    def pay(self):
        self.sender.credit(self.payment_solution.amount)


class Transfert(models.Model):
    datetime = models.DateTimeField('Date', default=now)
    justification = models.TextField('Justification', null=True, blank=True)
    sender = models.ForeignKey(User, related_name='sender_transfert',
                               on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='recipient_transfert',
                                  on_delete=models.CASCADE)
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(decimal.Decimal(0))])

    class Meta:
        """
        Define Permissions for Recharging.

        :note:: Initial Django Permission (add, view) are added.
        """
        default_permissions = ('add', 'view',)

    def wording(self):
        return 'Transfert de ' + self.sender.__str__() + ', ' + self.justification

    def pay(self):
        if self.sender.debit != self.recipient.credit:
            self.sender.debit(self.amount)
            self.recipient.credit(self.amount)


class ExceptionnalMovement(models.Model):
    datetime = models.DateTimeField('Date', default=now)
    justification = models.TextField('Justification', null=True, blank=True)
    operator = models.ForeignKey(User, related_name='sender_exceptionnal_movement',
                                 on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='recipient_exceptionnal_movement',
                                  on_delete=models.CASCADE)
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(decimal.Decimal(0))])
    is_credit = models.BooleanField(default=False)

    class Meta:
        """
        Define Permissions for Recharging.

        :note:: Initial Django Permission (add, view) are added.
        """
        default_permissions = ('add', 'view',)

    def wording(self):
        return 'Mouvement exceptionnel, ' + self.justification

    def pay(self):
        if self.is_credit:
            self.recipient.credit(self.amount)
        else:
            self.recipient.debit(self.amount)
