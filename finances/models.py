import decimal

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.timezone import now

from notifications.models import notify
from users.models import User
from shops.models import Shop, Product

# TODO: harmonization of methods name of Cash, Lydia, Cheque.
# TODO: harmonization of attributes singular/plurial (especially in Payment).
# TODO: shared_event line in tables users, products/payments and function.
# TODO (by eyap) : make the class PaymentSolution overridable (See Abstract / Proxy ?) and implement type in children


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


class SharedEvent(models.Model):
    """
    Une évènement partagé et payé par plusieurs personnes (users)
    ex: un repas

    Remarque :
    les participants sont dans la relation m2m users.
    Cependant, cette liste n'est pas ordonnée et deux demande de query peuvent
    renvoyer deux querys ordonnés différement
    """
    description = models.CharField('Description', max_length=254)
    date = models.DateField('Date Evenement', default=now)
    datetime = models.DateTimeField('Date Paiement', default=now)
    price = models.DecimalField('Prix', decimal_places=2, max_digits=9,
                                null=True, blank=True,
                                validators=[MinValueValidator(decimal.Decimal(0))])
    bills = models.CharField('Facture(s)', max_length=254, null=True,
                             blank=True)
    done = models.BooleanField('Terminé', default=False)
    payment_by_ponderation = models.BooleanField(
        'Paiement par pondération', default=False)
    remark = models.CharField(
        'Remarque', max_length=254, null=True, blank=True)
    manager = models.ForeignKey(User, related_name='manager',
                                on_delete=models.CASCADE)
    users = models.ManyToManyField(User,
                                   through='WeightsUser')
    allow_self_registeration = models.BooleanField(
        'Autoriser la self-préinscription', default=True)
    date_end_registration = models.DateField(
        'Date de fin de self-préinscription', blank=True, null=True)

    class Meta:
        """
        Define Permissions for SharedEvent.

        :note:: Initial Django Permission (add, change, delete, view) are added.
        """
        permissions = (
            # CRUDL
            # add_sharedevent
            # change_sharedevent
            # delete_sharedevent
            # view_sharedevent
            ('self_register_sharedevent', 'Can self register to a shared event'),
            ('proceed_payment_sharedevent', 'Can proceed to payment for a shared event'),
        )

    def __str__(self):
        """
        Return the display name of the SharedEvent.

        :returns: Description and Date
        :rtype: string
        """
        return self.description + ' ' + str(self.date)

    def list_users_weight(self):
        """
        Forme une liste des users [[user1, weight_registration, weight_participation],...]
        à partir de la liste des users
        :return: liste_u_p [[user1, weight_registration, weight_participation],...]
        """
        list_u_all = []
        for user in self.users.all():
            e = self.weightsuser_set.get(user=user, shared_event=self)
            if isinstance(self.price, decimal.Decimal) and e.weights_participation > 0:
                list_u_all.append(
                    [user, e.weights_registeration, e.weights_participation, e.weights_participation * self.price])
            else:
                list_u_all.append(
                    [user, e.weights_registeration, e.weights_participation])
        return list_u_all

    def list_participants_weight(self):
        """
        Forme une liste des participants [[user, weight],...]
        à partir de la liste des users
        :return: liste_u_p [[user, weight],...]
        """
        list_u_p = []
        for user in self.users.all():
            e = self.weightsuser_set.get(user=user, shared_event=self)
            weight = e.weights_participation
            if weight > 0:
                if self.price:
                    list_u_p.append([user, weight, weight * self.price])
                else:
                    list_u_p.append([user, weight])
        return list_u_p

    def list_registrants_weight(self):
        """
        Forme une liste des participants [[user, weight],...]
        à partir de la liste des users
        :return: liste_u_p [[user, weight],...]
        """
        list_u_r = []
        for user in self.users.all():
            e = self.weightsuser_set.get(user=user, shared_event=self)
            weight = e.weights_registeration
            if weight > 0:
                list_u_r.append([user, weight])
        return list_u_r

    def remove_user(self, user):
        """
        Suppresion de l'utilisateur, purement et simplement, de l'événement.
        :param user: user à supprimer
        :return:
        """
        try:
            # Suppresion de l'user dans users.
            WeightsUser.objects.filter(user=user, shared_event=self).delete()
        except ObjectDoesNotExist:
            pass
        except ValueError:
            pass

    def add_weight(self, user, weight, isParticipant=True):
        """
        Ajout d'un nombre de weight à l'utilisateur.
        :param user: user associé
        :param weight: weight à ajouter
        :param isParticipant: est ce qu'on ajoute un participant ?
        :return:
        """

        # if the user doesn't exist in the event already
        if user not in self.users.all():
            if isParticipant:
                WeightsUser.objects.create(
                    user=user, shared_event=self, weights_participation=weight)
            else:
                WeightsUser.objects.create(
                    user=user, shared_event=self, weights_registeration=weight)
        else:
            e = self.weightsuser_set.get(user=user, shared_event=self)
            if isParticipant:
                e.weights_participation += weight
            else:
                e.weights_registeration += weight
            e.save()

    def change_weight(self, user, weight, isParticipant=True):
        """
        Changement du nombre de weight de l'utilisateur.
        :param user: user associé
        :param weight: weight à changer
        :param isParticipant: est ce qu'on ajoute un participant ?
        :return:
        """

        # if the user doesn't exist in the event already
        if not user in self.users.all():
            if weight != 0:
                if isParticipant:
                    WeightsUser.objects.create(
                        user=user, shared_event=self, weights_participation=weight)
                else:
                    WeightsUser.objects.create(
                        user=user, shared_event=self, weights_registeration=weight)
        else:
            e = self.weightsuser_set.get(user=user)

            if weight == 0 and ((isParticipant and e.weights_registeration == 0) or (not isParticipant and e.weights_participation == 0)):
                e.delete()
                # Deleted if both values are 0

            else:
                if isParticipant:
                    e.weights_participation = weight
                else:
                    e.weights_registeration = weight

                e.save()

    def get_weight_of_user(self, user, isParticipant=True):
        try:
            if isParticipant:
                return self.weightsuser_set.get(user=user).weights_participation
            else:
                return self.weightsuser_set.get(user=user).weights_registeration
        except (ObjectDoesNotExist, ValueError):
            return 0

    def get_price_of_user(self, user):
            # Calcul du prix par weight
        if isinstance(self.price, decimal.Decimal):
            weight_of_user = self.get_weight_of_user(user)
            if not self.payment_by_ponderation:
                total_weights_participants = self.get_total_weights_participants()
                try:
                    return round(self.price / total_weights_participants * weight_of_user, 2)
                except (ZeroDivisionError, decimal.DivisionUndefined, decimal.DivisionByZero):
                    return 0
            else:
                return self.price * weight_of_user
        else:
            return 0

    def pay_by_total(self, operator, recipient, total_price):
        """
        Procède au paiement de l'évenement par les participants.
        Une seule vente, un seul paiement mais plusieurs débits sur compte
        (un par participant)
        :param operator: user qui procède au paiement
        :param recipient: user qui recoit les paiements (AE_ENSAM)
        :return:
        """

        self.done = True
        self.save()

        # Calcul du prix par weight
        total_weight = self.get_total_weights_participants()
        try:
            final_price_per_weight = round(total_price / total_weight, 2)
        except (ZeroDivisionError, decimal.DivisionUndefined, decimal.DivisionByZero):
            return

        for e in self.weightsuser_set.all():
            user_price = final_price_per_weight * e.weights_participation
            e.user.debit(user_price)
            recipient.credit(user_price)
            if (e.user.balance < 0):
                            # If negative balance after event
                        # We notify
                notify(notification_class_name='negative_balance',
                       actor=operator,
                       recipient=e.user,
                       target_object=self
                       )

        self.price = total_price
        self.datetime = now()
        self.remark = 'Paiement par Borgia (Prix total : ' + \
            str(total_price) + ')'
        self.save()

    def pay_by_ponderation(self, operator, recipient, ponderation_price):
        """
        Procède au paiement de l'évenement par les participants.
        Une seule vente, un seul paiement mais plusieurs débits sur compte
        (un par participant)
        :param operator: user qui procède au paiement
        :param recipient: user qui recoit les paiements (AE_ENSAM)
        :param ponderation_price: price per ponderation for each participant
        :return:
        """

        self.done = True
        self.save()

        for e in self.weightsuser_set.all():
            weight = e.weights_participation
            if weight != 0:
                user_price = ponderation_price * weight
                e.user.debit(user_price)
                recipient.credit(user_price)
                if (e.user.balance < 0):
                            # If negative balance after event
                        # We notify
                    notify(notification_class_name='negative_balance',
                           actor=operator,
                           recipient=e.user,
                           target_object=self
                           )

        self.payment_by_ponderation = True
        self.price = ponderation_price
        self.datetime = now()
        self.remark = 'Paiement par Borgia (Prix par pondération: ' + \
            str(ponderation_price) + ')'
        self.save()

    def end_without_payment(self, remark):
        """
        Termine l'évènement sans effectuer de paiement
        :param remark: justification
        :return:
        """
        self.done = True
        self.price = decimal.Decimal('0.00')
        self.datetime = now()
        self.remark = 'Pas de paiement : ' + remark
        self.save()

    def wording(self):
        return 'Événement : ' + self.description + ', le ' + self.date.strftime('%d/%m')

    def get_total_weights_registrants(self):
        total = 0
        for e in self.weightsuser_set.all():
            total += e.weights_registeration
        return total

    def get_total_weights_participants(self):
        total = 0
        for e in self.weightsuser_set.all():
            total += e.weights_participation
        return total

    def get_number_registrants(self):
        total = 0
        for e in self.weightsuser_set.all():
            if e.weights_registeration != 0:
                total += 1
        return total

    def get_number_participants(self):
        total = 0
        for e in self.weightsuser_set.all():
            if e.weights_participation != 0:
                total += 1
        return total


class WeightsUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_event = models.ForeignKey(SharedEvent, on_delete=models.CASCADE)
    weights_registeration = models.IntegerField(default=0)
    weights_participation = models.IntegerField(default=0)

    class Meta:
        """
        Remove default permissions for WeightsUser
        """
        default_permissions = ()

    def __str__(self):
        return "%s possede %s parts dans l'événement %s" % (self.user, self.weights_participation, self.shared_event)
