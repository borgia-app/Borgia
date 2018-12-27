#-*- coding: utf-8 -*-
import decimal

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.timezone import now

from users.models import User

# TODO: harmonization of methods name of Cash, Lydia, Cheque.
# TODO: harmonization of attributes singular/plurial (especially in Payment).
# TODO: event line in tables users, products/payments and function.
# TODO (by eyap) : make the class PaymentSolution overridable (See Abstract) and implement type in children


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
    payment_solution = models.ForeignKey(
        PaymentSolution, on_delete=models.CASCADE)

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
