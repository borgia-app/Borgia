from django.db import models
from users.models import User
from django.utils.timezone import now


class Transaction(models.Model):
    # Informations générales
    operator = models.ForeignKey(User, related_name='transaction_operator')
    client = models.ForeignKey(User, related_name='transaction_client')
    date = models.DateField(default=now)
    time = models.TimeField(default=now)

    # Liste des moyens de payement
    cheques = models.ManyToManyField('Cheque', blank=True)
    cashs = models.ManyToManyField('Cash', blank=True)
    lydias = models.ManyToManyField('Lydia', blank=True)

    # Validation
    validated = models.BooleanField(default=False)
    error_credit = models.BooleanField(default=True)

    def __str__(self):
        return 'Transaction n°' + str(self.id)

    def list_cheques(self):
        return Cheque.objects.filter(transaction__cheques__transaction=self)

    def sub_total_cheques(self):
        u_c = 0
        for e in self.list_cheques():
            u_c = u_c + e.amount
        return u_c

    def list_cashs(self):
            return Cash.objects.filter(transaction__cashs__transaction=self)

    def sub_total_cashs(self):
        u_ca = 0
        for e in self.list_cashs():
            u_ca = u_ca + e.amount
        return u_ca

    def list_lydias(self):
            return Lydia.objects.filter(transaction__lydias__transaction=self)

    def sub_total_lydias(self):
        u_l = 0
        for e in self.list_lydias():
            u_ca = u_l + e.amount
        return u_l

    def total(self):
        return self.sub_total_cashs()+self.sub_total_cheques()+self.sub_total_lydias()


class Cheque(models.Model):
    # Informations sur l'identité du chèque
    number = models.CharField(max_length=7)
    signatory = models.ForeignKey(User, related_name='cheque_signatory')
    date_sign = models.DateField(default=now)
    recipient = models.ForeignKey(User, related_name='cheque_recipient')
    amount = models.FloatField()

    # Information de comptabilité
    date_cash = models.DateField(blank=True, null=True)
    cashed = models.BooleanField(default=False)

    def __str__(self):
        return self.signatory.last_name+' '+self.signatory.first_name+' '+str(self.amount)+'€ n°'+self.number

    def list_transaction(self):
        return Transaction.objects.filter(cheques__transaction__cheques=self)


class Cash(models.Model):
    # Information sur l'identité des espèces
    amount = models.FloatField()
    giver = models.ForeignKey(User, related_name='cash_giver')

    # Information de comptabilité
    cashed = models.BooleanField(default=False)
    date_cash = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.giver.last_name+' '+self.giver.first_name+' '+str(self.amount)+'€'

    def list_transaction(self):
        return Transaction.objects.filter(cashs__transaction__cashs=self)


class Lydia(models.Model):
    # Information sur l'identité du virement lydia
    date_operation = models.DateField(default=now)
    time_operation = models.TimeField(default=now)
    amount = models.FloatField()
    # numéro unique ?
    giver = models.ForeignKey(User, related_name='lydia_giver')
    recipient = models.ForeignKey(User, related_name='lydia_recipient')

    # Information de comptabilité
    cashed = models.BooleanField(default=False)
    date_cash = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.giver.last_name+' '+self.giver.first_name+' '+str(self.amount)+'€'

    def list_transaction(self):
        return Transaction.objects.filter(lydias__transaction__lydias=self)



