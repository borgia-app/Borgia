import decimal

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now

from users.models import User


class Event(models.Model):
    """
    A shared event, paid by many users

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
        Define Permissions for Event.

        :note:: Initial Django Permission (add, change, delete, view) are added.
        """
        permissions = (
            # CRUDL
            # add_event
            # change_event
            # delete_event
            # view_event
            ('self_register_event', 'Can self register to an event'),
            ('proceed_payment_event', 'Can proceed to payment for an event'),
        )

    def __str__(self):
        """
        Return the display name of the Event.

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
            weightsuser = self.weightsuser_set.get(user=user)
            if isinstance(self.price, decimal.Decimal) and weightsuser.weights_participation > 0:
                list_u_all.append(
                    [user, weightsuser.weights_registeration,
                     weightsuser.weights_participation,
                     weightsuser.weights_participation * self.price])
            else:
                list_u_all.append(
                    [user, weightsuser.weights_registeration,
                     weightsuser.weights_participation])
        return list_u_all

    def list_participants_weight(self):
        """
        Forme une liste des participants [[user, weight],...]
        à partir de la liste des users
        :return: liste_u_p [[user, weight],...]
        """
        list_u_p = []
        for user in self.users.all():
            weights = self.weightsuser_set.get(user=user, event=self)
            weight = weights.weights_participation
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
            weightsuser = self.weightsuser_set.get(user=user, event=self)
            weight = weightsuser.weights_registeration
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
            WeightsUser.objects.filter(user=user, event=self).delete()
        except ObjectDoesNotExist:
            pass
        except ValueError:
            pass

    def add_weight(self, user, weight, is_participant=True):
        """
        Ajout d'un nombre de weight à l'utilisateur.
        :param user: user associé
        :param weight: weight à ajouter
        :param is_participant: est ce qu'on ajoute un participant ?
        :return:
        """

        # if the user doesn't exist in the event already
        if user not in self.users.all():
            if is_participant:
                WeightsUser.objects.create(
                    user=user, event=self, weights_participation=weight)
            else:
                WeightsUser.objects.create(
                    user=user, event=self, weights_registeration=weight)
        else:
            weightsuser = self.weightsuser_set.get(user=user, event=self)
            if is_participant:
                weightsuser.weights_participation += weight
            else:
                weightsuser.weights_registeration += weight
            weightsuser.save()

    def change_weight(self, user, weight, is_participant=True):
        """
        Changement du nombre de weight de l'utilisateur.
        :param user: user associé
        :param weight: weight à changer
        :param is_participant: est ce qu'on ajoute un participant ?
        :return:
        """

        # if the user doesn't exist in the event already
        if not user in self.users.all():
            if weight != 0:
                if is_participant:
                    WeightsUser.objects.create(
                        user=user, event=self, weights_participation=weight)
                else:
                    WeightsUser.objects.create(
                        user=user, event=self, weights_registeration=weight)
        else:
            e = self.weightsuser_set.get(user=user)

            if weight == 0 and ((is_participant and e.weights_registeration == 0)
                or (not is_participant and e.weights_participation == 0)):
                e.delete()
                # Deleted if both values are 0

            else:
                if is_participant:
                    e.weights_participation = weight
                else:
                    e.weights_registeration = weight

                e.save()

    def get_weight_of_user(self, user, is_participant=True):
        try:
            if is_participant:
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

        for weights in self.weightsuser_set.all():
            weight = weights.weights_participation
            if weight != 0:
                user_price = ponderation_price * weight
                weights.user.debit(user_price)
                recipient.credit(user_price)

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
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    weights_registeration = models.IntegerField(default=0)
    weights_participation = models.IntegerField(default=0)

    class Meta:
        """
        Remove default permissions for WeightsUser
        """
        default_permissions = ()

    def __str__(self):
        return '{0} possede {1} parts dans l\'événement {3}'.format(
            self.user, self.weights_participation, self.event)
