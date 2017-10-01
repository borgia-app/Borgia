from django.db import models
from django.utils.timezone import now
from decimal import Decimal
import json

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation
    )
from django.contrib.contenttypes.models import ContentType

# TODO: harmonization of methods name of Cash, Lydia, Cheque.
# TODO: harmonization of attributes singular/plurial (especially in Payment).
# TODO: shared_event line in tables users, products/payments and function.


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


    """
    datetime = models.DateTimeField('Date', default=now)
    sender = models.ForeignKey('users.User', related_name='sender_sale',
    on_delete=models.CASCADE)
    recipient = models.ForeignKey('users.User', related_name='recipient_sale',
    on_delete=models.CASCADE)
    operator = models.ForeignKey('users.User', related_name='operator_sale',
    on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    module_id = models.PositiveIntegerField()
    module = GenericForeignKey('content_type', 'module_id')
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE)
    products = models.ManyToManyField('shops.Product', through='SaleProduct')

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

        :note:: Why do SharedEvents are excluded ?
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

    class Meta:
        """
        Define Permissions for Sale.
        """
        permissions = (
            ('retrieve_sale', 'Afficher une vente'),
            ('list_sale', 'Lister les ventes'),
            ('retrieve_recharging', 'Afficher un rechargement'),
            ('list_recharging', 'Lister les rechargements'),
            ('retrieve_transfert', 'Afficher un transfert'),
            ('list_transfert', 'Lister les transferts'),
            ('add_exceptionnal_movement',
             'Faire un mouvement exceptionnel'),
            ('retrieve_exceptionnal_movement',
             'Afficher un mouvement exceptionnel'),
            ('list_exceptionnal_movement',
             'Lister les mouvements exceptionnels')
        )


class SaleProduct(models.Model):
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE)
    product = models.ForeignKey('shops.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField('Prix', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])

    def __str__(self):
        if self.product.unit:
            return self.product.__str__() + ' x ' + str(self.quantity) + self.product.get_unit_display()
        else:
            if self.quantity > 1:
                return self.product.__str__() + ' x ' + str(self.quantity)
            else:
                return self.product.__str__()


class Recharging(models.Model):
    datetime = models.DateTimeField('Date', default=now)
    sender = models.ForeignKey('users.User', related_name='sender_recharging',
    on_delete=models.CASCADE)
    operator = models.ForeignKey('users.User', related_name='operator_recharging',
    on_delete=models.CASCADE)
    payment_solution = models.ForeignKey('PaymentSolution', on_delete=models.CASCADE)

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


class PaymentSolution(models.Model):
    sender = models.ForeignKey('users.User', related_name='payment_sender',
    on_delete=models.CASCADE)
    recipient = models.ForeignKey('users.User',
                                  related_name='payment_recipient',
                                  on_delete=models.CASCADE)
    amount = models.DecimalField('Montant', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])

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
        type = self.get_type()
        if type == 'cash':
            return 'espèces'
        if type == 'cheque':
            return 'chèque'
        if type == 'lydiafacetoface':
            return 'lydia face à face'
        if type == 'lydiaonline':
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

    def __str__(self):
        return 'Cheque n°' + self.cheque_number

    class Meta:
        """
        Define Permissions for Cheque.
        """
        permissions = (
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

    def __str__(self):
        return 'Payement Lydia n°' + self.id_from_lydia

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

    def __str__(self):
        return 'Payement Lydia n°' + self.id_from_lydia

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

    def wording(self):
        return 'Transfert de ' + self.sender.__str__() + ', ' + self.justification


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

    def wording(self):
        return 'Mouvement exceptionnel, ' + self.justification

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
    date = models.DateField('Date Evenement', default=now)
    datetime = models.DateTimeField('Date Paiement', default=now)
    price = models.DecimalField('Prix', decimal_places=2, max_digits=9,
                                null=True, blank=True,
                                validators=[MinValueValidator(Decimal(0))])
    bills = models.CharField('Facture(s)', max_length=254, null=True,
                             blank=True)
    done = models.BooleanField('Terminé', default=False)
    # remark = models.CharField('Remarque', max_length=254, null=True,
    #                       blank=True)
    manager = models.ForeignKey('users.User', related_name='manager',
        on_delete=models.CASCADE)

    # sale = models.ForeignKey('Sale', null=True, blank=True,
    #     on_delete=models.CASCADE)

    participants = models.ManyToManyField('users.User', blank=True,
                                          related_name='participants')
    registered = models.ManyToManyField('users.User', blank=True,
                                        related_name='registered')
    ponderation = models.CharField(
        'Liste ordonnée participants - pondérations',
        max_length=10000, default='[]')

    def __str__(self):
        """
        Return the display name of the SharedEvent.

        :returns: Description and Date
        :rtype: string
        """
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

        # NOT USED ANYMORE
        # sale = Sale.objects.create(datetime=now(),
        #                            sender=operator,
        #                            recipient=recipient,
        #                            operator=operator,
        #                            category='shared_event')
        #
        # # Liaison de l'événement commun
        # self.sale = sale
        # self.save()

        # Calcul du prix par ponderation
        total_ponderation = 0
        for e in self.list_of_participants_ponderation():
            total_ponderation += e[1]
        price_per_ponderation = round(self.price / total_ponderation, 2)

        # Créations paiements par compte foyer
        # payment = Payment.objects.create()

        # for u in self.list_of_participants_ponderation():
        #     d_b = DebitBalance.objects.create(
        #         amount=price_per_participant*u[1],
        #         date=now(),
        #         sender=u[0],
        #         recipient=sale.recipient)
        #     # Paiement
        #     payment.debit_balance.add(d_b)
        #     d_b.set_movement()

        for u in self.list_of_participants_ponderation():
            u[0].debit(price_per_ponderation*u[1])

        self.done = True
        self.datetime = now()
        self.save()



        # payment.save()
        # payment.maj_amount()
        #
        # sale.payment = payment
        # sale.maj_amount()
        # sale.save()
        #
        # self.done = True
        # self.remark = 'Paiement par Borgia'
        # self.save()

    def wording(self):
        return 'Evenement ' + self.description + ' ' + str(self.date)

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
