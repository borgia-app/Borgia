from datetime import datetime
from decimal import Decimal
import re
from itertools import chain

from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.utils import timezone

from django.contrib.auth.models import AbstractUser, Permission
from finances.models import Sale, BankAccount, SharedEvent, Transfert, Recharging, ExceptionnalMovement


class ExtendedPermission(Permission):

    class Meta:
        proxy = True
        default_permissions = ()

    def __str__(self):
        from borgia.utils import human_permission_name
        return human_permission_name(
            self.codename.replace('_', ' ').capitalize())


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
    :param token_id: id of the linked token to the user
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
    :type token_id: string must match ^[0-9A-Z]{12}$
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
    for i in range(1953, datetime.now().year + 1):
        YEAR_CHOICES.append((i, i))

    THEME_CHOICES = (
        ('light','Light'),
        ('dark','Dark'),
        ('birse','Birse')
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
    token_id = models.CharField('Numéro de jeton lié', max_length=12,
                                blank=True, null=True,
                                validators=[RegexValidator('^[0-9A-Z]{12}$',
                                                           """Mauvaise forme de
                                                           numéro de jeton, il
                                                           ne doit contenir que
                                                           sixchiffres et/ou
                                                           lettres
                                                           majuscules""")])
    avatar = models.ImageField('Avatar', upload_to='img/avatars/',
                               default=None, blank=True, null=True)
    theme = models.CharField('Préférence de theme graphique', choices=THEME_CHOICES,
                                max_length=15, blank=True, null=True)

    jwt_iat = models.DateTimeField('Jwt iat', default=timezone.now)


    def __str__(self):
        """
        Return the common string representing an instance of the class User.

        Returns the first name followed by the last name of the user.
        example:: Alexandre Palo

        :returns: string, undefined if no last or first name (not mandatory)
        """
        if not self.first_name or not self.last_name:
            return 'undefined'
        return self.first_name + ' ' + self.last_name

    def choice_string(self):
        """
        """
        if not self.first_name or not self.last_name:
            return 'undefined'
        try:
            return self.family + self.campus + str(self.year_pg()) + ' ' + self.first_name + ' ' + self.last_name
        except TypeError:
            return 'undefined'
        except AttributeError:
            return 'undefined'

    def display_name_navbar(self):
      """
      Return the name displayed in the navbar

      """
      if not self.first_name or not self.last_name:
         return 'undefined'
      try:
         if not self.surname or not self.family:
           return self.first_name + ' ' + self.last_name
         else:
           return self.surname + ' ' + self.family+self.campus+str(self.year_pg())
      except AttributeError:
         return 'undefined'

    def forecast_balance(self):
      # Get all undone shared events where user is involved as participant
      shared_events = SharedEvent.objects.filter(users__username__contains= self.username, done=False)
      solde_prev = 0
      for se in shared_events:
        solde_prev += se.get_price_of_user(self)
      self.virtual_balance = self.balance - solde_prev
	  #TODO: notify if forecast balance is negative
      self.save()

    def year_pg(self):
        """
        Return the promotion's year of the user, under the Gadz'Art standard.

        For ABCD year, this function returns ACD. The attribute year is not
        mandatory, the function will raise an error if there is no year.
        example:: 2014 -> 214

        :returns:  integer formatted year
        :raises: AttributeError when no year

        """
        if self.year is not None:
            return int(str(self.year)[:1] + str(self.year)[-2:])
        else:
            raise AttributeError("""The user does not have a defined year
                                 attribute""")

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
        if (not isinstance(amount, int)) and (not isinstance(amount, float)) and (not isinstance(amount, Decimal)):
            raise ValueError('The amount is not a number')
        if amount <= 0:
            raise ValueError('The amount must be positive')

        self.balance += amount
        self.save()

    def debit(self, amount):
        """
        Debit the user of a certain amount of money. If the balance is negative, a notification is created.

        note:: In both credit and debit cases, the amount must be positive.
        There is no function allowed to credit or debit a negative amount.

        :param amount: float or integer amount of money in euro, max 2 decimal
        places, must be superior to 0
        :returns: nothing
        :raise: ValueError if the amount is negative or null or if not a float
        or int
        """
        if (not isinstance(amount, int)) and (not isinstance(amount, float)) and (not isinstance(amount, Decimal)):
            raise ValueError('The amount is not a number')
        if amount <= 0:
            raise ValueError('The amount must be positive')

        self.balance -= amount
        self.save()


    def list_transaction(self):
        """
        Return the list of sales concerning the user.

        :returns: list of objects
        """

        sales = Sale.objects.filter(sender=self)
        transferts = Transfert.objects.filter(Q(sender=self) | Q(recipient=self))
        rechargings = Recharging.objects.filter(sender=self)
        exceptionnal_movements = ExceptionnalMovement.objects.filter(recipient=self)
        shared_events = SharedEvent.objects.filter(done=True, users=self)
        for e in shared_events:
            e.amount = e.get_price_of_user(self)

        list_transaction = sorted(
            list(chain(sales, transferts, rechargings, exceptionnal_movements, shared_events)),
            key=lambda instance: instance.datetime, reverse=True
        )

        return list_transaction

    def list_bank_account(self):
        """
        Return the list of bank accounts concerning the user.

        :returns: list of BankAccount objects.
        """
        return BankAccount.objects.filter(owner=self)

    class Meta:
        """
        Permission imposed or not to an instance of User.

        note:: All permission concerning a user in Borgia are defined here.
        However, please note that Django creates byhimself 3 permissions for
        the class User : the ability of creating, deleting and editing a User.
        note:: Permission strings are written in french because they are needed
        to be understood by every user of Borgia and tend to be directly
        displayed in the UI. Moreover theses permissions tend to be created by
        the UI himself, when generating groups or shops. They are going to be
        deprecated in further versions.
        """
        permissions = (
            # Group management
            ('manage_group_presidents', 'Gérer le groupe des présidents'),
            ('manage_group_vice-presidents-internal',
             '''Gérer le groupe des vices présidents délégués à la vie
             interne'''),
            ('manage_group_treasurers', 'Gérer le groupe des trésoriers'),
            ('manage_group_gadzarts', 'Gérer le groupe des Gadz\'Arts'),
            ('manage_group_honnored', '''Gérer le groupe des membres
             d\'honneurs'''),
            ('manage_group_specials', '''Gérer le groupe des membres
             spéciaux'''),

            # CRUDL
            # add_user
            # change_user
            # delete_user
            ('list_user', 'Lister les users'),
            ('retrieve_user', 'Afficher les users'),
            ('retrieve_more_user_info', "Afficher plus d'info sur les users"),

            # Miscellaneous
            ('supply_money_user', 'Ajouter de l\'argent à un utilisateur'),
            ('link_token_user', 'Lier un jeton à un utilisateur')
        )


def list_year():
    """
    Return the list of current used years in all the users.

    :returns: list of integer years used by users, sorted the decreasing dates.
    """
    list_year = []
    for u in User.objects.all().exclude(groups=6).exclude(pk=1): # Parmis tout les users moins les gadz d'honn'ss et l'admin
        if u.year not in list_year:
            if u.year is not None:  # year is not mandatory
                list_year.append(u.year)
    return sorted(list_year, reverse=True)


def user_from_token_tap(token_tap):
    """
    Return the user corresponding to a token id.

    The function does not use the format of token id defined in the related
    attribute of User. Instead, it uses another format given by several used
    RFID readers.
    note:: If the format of the token correspond to the format defined in the
    attribute of User (ie. ^[0-9A-Z]{6}$), one can just get the corresponding
    User with User.object.get('token_id'=token).

    :returns: User object
    :raise: ValueError if the original format is not ^[0-9]{26}$
    :raise: ObjectDoesNotExist if there is not corresponding User
    """
    return User.objects.get(token_id=token_tap_to_token_id(token_tap))


def token_tap_to_token_id(token_tap):
    """
    Return a token in the format ^[0-9A-Z]{6}$ from one in the format
    ^[0-9]{26}$.

    The format ^[0-9]{26}$ might be the result of some RFID reader. However,
    the format saved in the database is ^[0-9A-Z]{6}$.
    example:: 25166484851706966556857503 -> 3FEB7D and
    25166484852565553687068573 -> 4875DF

    :param token_tap: token in the original format
    :type token_tap: string ^[0-9]{26}$
    :returns: string ^[0-9A-Z]{6}$ token format used in the database
    :raise: ValueError if the original format is not ^[0-9]{26}$
    """
    if not re.match('^[0-9]{26}$', token_tap):
        raise ValueError('The input token must match ^[0-9]{26}$')

    token = ''
    for dual in re.findall(r"[0-9]{2}", token_tap[1:len(token_tap) - 5]):
        token += chr(int(dual))
    token = token[4:]
    return token
