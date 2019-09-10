import datetime
import decimal
import itertools

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from borgia.utils import (PRESIDENTS_GROUP_NAME, VICE_PRESIDENTS_GROUP_NAME, TREASURERS_GROUP_NAME,
                          INTERNALS_GROUP_NAME, EXTERNALS_GROUP_NAME)


class User(AbstractUser):
    """
    Extend the AbstractUser class from Django to define a common User class.

    note:: All attributes refer to the user state. For its group for instance
    (honnor member for example) please refer to the class Group (Django Auth
    app).

    Attributes:
    :param id: auto generated Django id for db, from AbstractUser, auto
    :param username: username of the user, from AbstractUser, mandatory
    :param last_name: last name of the user, from AbstractUser
    :param first_name: first name of the user, from AbstractUser
    :param password: hashed password of the user, from AbstractUser
    :param email: e-mail of the user, from AbstractUser
    :param surname: Gadz'Art surname of the user (ie. bucque)
    :param family: Gadz'Art family of the user (ie. fam'ss)
    :param balance: hard consolidated balance for the user account
    :param year: Gadz'Art promotion of the user (ie. prom'ss)
    :param campus: Gadz'Art centre of the user (ie. tabagn'ss)
    :param phone: phone number of the user (currently not used)
    :param avatar: image of the user
    :param theme: preference of css for the user
    :type id: integer superior to 0
    :type username: string only alpha numeric warning:: must be unique
    :type last_name: string
    :type first_name: string
    :type password: string note:: for more info about password management
    refer to Django doc _passwords:
    https://docs.djangoproject.com/en/1.10/topics/auth/passwords/
    :type email: string must match standard email regex
    :type surname: string
    :type family: string
    :type balance float
    :type year: string must be in YEAR_CHOICES
    :type campus: string must be in CAMPUS_CHOICES
    :type phone: string must match standard phone number in France ^0[0-9]{9}$
    :type avatar: string path of the image in statics
    :type theme: string must be in THEME_CHOICES

    """

    CAMPUS_CHOICES = (
        ('ME', 'Me'),
        ('AN', 'An'),
        ('CH', 'Ch'),
        ('BO', 'Bo'),
        ('LI', 'Li'),
        ('CL', 'Cl'),
        ('KA', 'Ka'),
        ('KIN', 'Kin')
    )
    YEAR_CHOICES = []
    for i in range(1953, datetime.datetime.now().year + 1):
        YEAR_CHOICES.append((i, i))

    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('birse', 'Birse')
    )

    surname = models.CharField('Bucque', max_length=255, blank=True, null=True)
    family = models.CharField('Fam\'ss', max_length=255, blank=True, null=True)
    balance = models.DecimalField('Solde', default=0, max_digits=9,
                                  decimal_places=2)
    virtual_balance = models.DecimalField('Solde prévisionnel', default=0, max_digits=9,
                                          decimal_places=2)
    year = models.IntegerField('Prom\'ss', choices=YEAR_CHOICES, blank=True,
                               null=True)
    campus = models.CharField('Tabagn\'ss', choices=CAMPUS_CHOICES,
                              max_length=3, blank=True, null=True)
    phone = models.CharField('Numéro de téléphone', max_length=255,
                             blank=True, null=True,
                             validators=[RegexValidator('^0[0-9]{9}$',
                                                        """Le numéro doit être
                                                        du type
                                                        0123456789""")])
    avatar = models.ImageField('Avatar', upload_to='img/avatars/',
                               default=None, blank=True, null=True)
    theme = models.CharField('Préférence de theme graphique', choices=THEME_CHOICES,
                             max_length=15, blank=True, null=True)

    jwt_iat = models.DateTimeField('Jwt iat', default=timezone.now)

    class Meta:
        """
        Define Permissions for User.

        :note:: Initial Django Permission (add, change, delete, view) are added.
        """
        permissions = (
            # Group management
            ("manage_" + PRESIDENTS_GROUP_NAME + \
             "_group", 'Can manage presidents group'),
            ("manage_" + VICE_PRESIDENTS_GROUP_NAME + \
             "_group", 'Can manage vice presidents group'),
            ("manage_" + TREASURERS_GROUP_NAME + \
             "_group", 'Can manage treasurers group'),
            ("manage_" + INTERNALS_GROUP_NAME + "_group", 'Can manage members group'),
            ("manage_" + EXTERNALS_GROUP_NAME + \
             "_group", 'Can manage externals group'),

            # User management
            # add_user
            # change_user
            # delete_user
            # view_user
            ('advanced_view_user', "Can view advanced data on user"),
        )

    def __str__(self):
        """
        Return the common string representing an instance of the class User.

        Returns the first name followed by the last name of the user.
        example:: Alexandre Palo
        If the first name or the last name is missing, return the username.

        :returns: string, undefined if no last or first name (not mandatory)
        """

        if not self.first_name or not self.last_name:
            return self.username
        else:
            return self.first_name + ' ' + self.last_name

    def get_full_name(self):
        """
        Return the name displayed in the navbar

        """
        if not self.first_name or not self.last_name:
            return self.username
        try:
            if not self.surname or not self.family:
                return self.first_name + ' ' + self.last_name
            else:
                return self.surname + ' ' + self.family + self.campus + self.year_pg()
        except AttributeError:
            return self.username

    def year_pg(self):
        """
        Return the promotion's year of the user, under the Gadz'Art standard.

        For ABCD year, this function returns ACD. The attribute year is not
        mandatory, the function will raise an error if there is no year.
        example:: 2014 -> 214

        :returns:  string
        :raises: AttributeError when no year

        """
        if self.year is not None:
            year = str(self.year)
            return year[:1] + year[-2:]
        else:
            return ""

    def forecast_balance(self):
        """
        Get all undone shared events where user is involved as participant

        TODO : Strongly dependent of events, should be moved there.
        """
        events = self.event_set.filter(done=False)
        solde_prev = 0
        for se in events:
            solde_prev += se.get_price_of_user(self)
        self.virtual_balance = self.balance - solde_prev
        self.save()

    def credit(self, amount):
        """
        Credit the user of a certain amount of money.

        note:: In both credit and debit cases, the amount must be positiv.
        There is no function allowed to credit or debit a negativ amount.

        :param amount: float or integer amount of money in euro, max 2 decimal
        places, must be superior to 0
        :returns: nothing
        :raise: ValueError if the amount is negative or null or if not a float
        or int
        """
        if (not isinstance(amount, int)) and (not isinstance(amount, float)) and (not isinstance(amount, decimal.Decimal)):
            raise ValueError('The amount is not a number')
        if amount <= 0:
            raise ValueError('The amount must be positive')

        self.balance += amount
        self.save()

    def debit(self, amount):
        """
        Debit the user of a certain amount of money.

        note:: In both credit and debit cases, the amount must be positive.
        There is no function allowed to credit or debit a negative amount.

        :param amount: float or integer amount of money in euro, max 2 decimal
        places, must be superior to 0
        :returns: nothing
        :raise: ValueError if the amount is negative or null or if not a float
        or int
        """
        if (not isinstance(amount, int)) and (not isinstance(amount, float)) and (not isinstance(amount, decimal.Decimal)):
            raise ValueError('The amount is not a number')
        if amount <= 0:
            raise ValueError('The amount must be strictly positive')

        self.balance -= amount
        self.save()

    def list_transaction(self):
        """
        Return the list of sales concerning the user.

        :returns: list of objects
        """

        sales = self.sender_sale.all()
        transferts = self.recipient_transfert.union(
            self.sender_transfert.all())
        rechargings = self.sender_recharging.all()
        exceptionnal_movements = self.recipient_exceptionnal_movement.all()
        events = self.event_set.filter(done=True)
        for event in events:
            event.amount = event.get_price_of_user(self)

        list_transaction = sorted(
            list(itertools.chain(sales, transferts, rechargings,
                                 exceptionnal_movements, events)),
            key=lambda instance: instance.datetime, reverse=True
        )

        return list_transaction


def get_list_year():
    """
    Return the list of current used years in all the users.

    :returns: list of integer years used by users, by decreasing dates.
    """
    list_year = []
    # For each user except admin
    for user in User.objects.filter(is_active=True).exclude(pk=1):
        if user.year not in list_year:
            if user.year is not None:  # year is not mandatory
                list_year.append(user.year)
    return sorted(list_year, reverse=True)
