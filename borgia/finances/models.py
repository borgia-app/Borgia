import decimal

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.timezone import now

from users.models import User

# TODO: harmonization of methods name of Cash, Lydia, Cheque.
# TODO: harmonization of attributes singular/plurial (especially in Payment).
# TODO: event line in tables users, products/payments and function.


class Recharging(models.Model):
    """
    Allow an operator to recharge (supply money) the balance of a sender
    """
    datetime = models.DateTimeField('Date', default=now)
    sender = models.ForeignKey(User, related_name='sender_recharging',
                               on_delete=models.CASCADE)
    operator = models.ForeignKey(User, related_name='operator_recharging',
                                 on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    solution_id = models.PositiveIntegerField()
    content_solution = GenericForeignKey('content_type', 'solution_id')

    class Meta:
        """
        Define Permissions for Recharging.

        :note:: Initial Django Permission (add, view) are added.
        """
        default_permissions = ('add', 'view',)

    def __str__(self):
        return 'Rechargement de ' + str(self.amount()) + '€.'

    def amount(self):
        return self.content_solution.amount

    def pay(self):
        self.sender.credit(self.amount())


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

    def __str__(self):
        return 'Transfert de ' + self.sender.__str__() + ' à ' + self.recipient.__str__() +', ' + self.justification

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

    def __str__(self):
        return 'Mouvement exceptionnel de ' + str(self.amount) + '€, ' + self.justification

    def pay(self):
        '''
        Add/Remove money from recipient
        '''
        if self.is_credit:
            self.recipient.credit(self.amount)
        else:
            self.recipient.debit(self.amount)


class BaseRechargingSolution(models.Model):
    """
    Base model for recharging solutions.
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(decimal.Decimal(0))])

    class Meta:
        """
        Remove default permissions for base and children.
        """
        abstract = True
        default_permissions = ()


class Cheque(BaseRechargingSolution):
    """
    Define a type of recharging made by a bank cheque.

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

    def __str__(self):
        return 'Cheque de ' + str(self.amount) + '€, n°' + self.cheque_number


class Cash(BaseRechargingSolution):
    """
    Define a type of payment made by a phycial money (cash).

    :note:: Related to a unique User.
    """

    def __str__(self):
        return 'Cash de ' + str(self.amount) + '€'


class Lydia(BaseRechargingSolution):
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
    is_online = models.BooleanField('Paiement en ligne', default=True)
    fee = models.DecimalField('Frais lydia', default=0, decimal_places=2,
                              max_digits=9,
                              validators=[MinValueValidator(decimal.Decimal(0))])

    def __str__(self):
        return 'Lydia de ' + str(self.amount) + '€, n°' + self.id_from_lydia
