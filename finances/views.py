import json
import time
import re
import csv
import xlsxwriter
import operator
import hashlib
import decimal
from django.shortcuts import render, HttpResponse, force_text, redirect
from django.shortcuts import Http404
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Permission
from django.db.models import Q
from datetime import timedelta
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView, View
from django.contrib.auth.models import Group
from django.conf import settings

from finances.forms import *
from finances.models import *
from shops.models import Container, ProductBase
from borgia.utils import *


class UserBankAccountCreate(GroupPermissionMixin, UserMixin, FormView,
                            GroupLateralMenuFormMixin):
    """
    View to create a bank account for a specific user.

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['user_pk']: pk of the specific user, mandatory
    :type kwargs['user_pk']: positif integer
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the user_pk doesn't match an user
    :raises: Http404 if the group doesn't have the permission to add account
    """
    template_name = 'finances/user_bankaccount_create.html'
    perm_codename = 'add_bankaccount'
    lm_active = None
    form_class = BankAccountCreateForm

    def form_valid(self, form):
        """
        Create a bank account for the user.
        """
        BankAccount.objects.create(
            bank=form.cleaned_data['bank'],
            account=form.cleaned_data['account'],
            owner=self.user
        )
        return super(UserBankAccountCreate, self).form_valid(form)


class SelfBankAccountCreate(GroupPermissionMixin, FormView,
                            GroupLateralMenuFormMixin):
    """
    View to create a bank account for the logged user.

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the logged user is not in the group
    """
    template_name = 'finances/self_bankaccount_create.html'
    perm_codename = None
    lm_active = None
    form_class = BankAccountCreateForm

    def form_valid(self, form):
        """
        Create a bank account for the logged user.
        """
        BankAccount.objects.create(
            bank=form.cleaned_data['bank'],
            account=form.cleaned_data['account'],
            owner=self.request.user
        )
        self.success_url = reverse(
            'url_self_user_update',
            kwargs={'group_name': self.group.name}
        )
        return super(SelfBankAccountCreate, self).form_valid(form)


class UserBankAccountUpdate(GroupPermissionMixin, UserMixin, FormView,
                            GroupLateralMenuFormMixin):
    """
    View to update a bank account for a specific user.

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['user_pk']: pk of the specific user, mandatory
    :param kwargs['pk']: pk of the bankaccount, mandatory
    :type kwargs['user_pk']: positif integer
    :type kwargs['group_name']: string
    :type kwargs['pk']: positiv integer
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the user_pk doesn't match an user
    :raises: Http404 if the group doesn't have the permission to update account
    :raises: Http404 if the pk doesn't match a bank account
    :raises: PermissionDenied if the bank account is not owned by the user
    """
    template_name = 'finances/user_bankaccount_update.html'
    perm_codename = 'change_bankaccount'
    lm_active = None
    form_class = BankAccountUpdateForm

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the bank account is owned by the user.

        :raises: PermissionDenied if not.
        """
        try:
            self.object = BankAccount.objects.get(pk=kwargs['pk'])
            self.user = User.objects.get(pk=kwargs['user_pk'])
        except ObjectDoesNotExist:
            raise Http404
        if self.object.owner != self.user:
            raise PermissionDenied
        return super(UserBankAccountUpdate, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserBankAccountUpdate, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def get_initial(self):
        initial = super(UserBankAccountUpdate, self).get_initial()
        initial['bank'] = self.object.bank
        initial['account'] = self.object.account
        return initial

    def form_valid(self, form):
        self.object.bank = form.cleaned_data['bank']
        self.object.account = form.cleaned_data['account']
        self.object.save()
        return super(UserBankAccountUpdate, self).form_valid(form)


class SelfBankAccountUpdate(GroupPermissionMixin, FormView,
                            GroupLateralMenuFormMixin):
    """
    View to update a bank account for the logged user.

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['pk']: pk of the bankaccount, mandatory
    :type kwargs['group_name']: string
    :type kwargs['pk']: positiv integer
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the pk doesn't match a bank account
    :raises: PermissionDenied if the bank account is not owned by the user
    """
    template_name = 'finances/self_bankaccount_update.html'
    perm_codename = None
    lm_active = None
    form_class = BankAccountUpdateForm

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the bank account is owned by the logged user.

        :raises: PermissionDenied if not.
        """
        try:
            self.object = BankAccount.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        if self.object.owner != request.user:
            raise PermissionDenied
        return super(SelfBankAccountUpdate, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SelfBankAccountUpdate, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def get_initial(self):
        initial = super(SelfBankAccountUpdate, self).get_initial()
        initial['bank'] = self.object.bank
        initial['account'] = self.object.account
        return initial

    def form_valid(self, form):
        self.object.bank = form.cleaned_data['bank']
        self.object.account = form.cleaned_data['account']
        self.object.save()
        self.success_url = reverse(
            'url_self_user_update',
            kwargs={'group_name': self.group.name}
        )
        return super(SelfBankAccountUpdate, self).form_valid(form)


class UserBankAccountDelete(GroupPermissionMixin, UserMixin, View,
                            GroupLateralMenuMixin):
    """
    View to delete a bank account for a specific user.

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['user_pk']: pk of the specific user, mandatory
    :param kwargs['pk']: pk of the bankaccount, mandatory
    :type kwargs['user_pk']: positif integer
    :type kwargs['group_name']: string
    :type kwargs['pk']: positiv integer
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the user_pk doesn't match an user
    :raises: Http404 if the group doesn't have the permission to delete account
    :raises: Http404 if the pk doesn't match a bank account
    :raises: PermissionDenied if the bank account is not owned by the user
    """
    template_name = 'finances/user_bankaccount_delete.html'
    perm_codename = 'delete_bankaccount'
    lm_active = None

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the bank account is owned by the user.

        :raises: PermissionDenied if not.
        """
        try:
            self.object = BankAccount.objects.get(pk=kwargs['pk'])
            self.user = User.objects.get(pk=kwargs['user_pk'])
        except ObjectDoesNotExist:
            raise Http404
        if self.object.owner != self.user:
            raise PermissionDenied
        return super(UserBankAccountDelete, self).dispatch(
            request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        self.object.delete()
        return redirect(force_text(self.success_url))


class SelfBankAccountDelete(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    View to delete a bank account for the logged user.

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['pk']: pk of the bankaccount, mandatory
    :type kwargs['group_name']: string
    :type kwargs['pk']: positiv integer
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the pk doesn't match a bank account
    :raises: PermissionDenied if the bank account is not owned by the logged
    user
    """
    template_name = 'finances/self_bankaccount_delete.html'
    perm_codename = None
    lm_active = None

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the bank account is owned by the logged user.

        :raises: PermissionDenied if not.
        """
        try:
            self.object = BankAccount.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        if self.object.owner != request.user:
            raise PermissionDenied
        return super(SelfBankAccountDelete, self).dispatch(
            request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        self.object.delete()
        return redirect(reverse(
            'url_self_user_update',
            kwargs={'group_name': self.group.name}))


class SaleList(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    """
    View to list sales.

    If the group derived from a shop, only sales from this shop are listed.
    Else (presidents, treasurers or vice-presidents-internal) all sales are
    listed with this view. The view handle request of the form to filter
    sales.
    :note:: only sales are listed here. Sales come from a shop, for other
    types of transactions, please refer to other classes (RechargingList,
    TransfertList and ExceptionnalMovementList).

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the group doesn't have the permission to list sales
    """
    template_name = 'finances/sale_shop_list.html'
    perm_codename = 'list_sale'
    lm_active = 'lm_sale_list'
    form_class = GenericListSearchDateForm

    query_shop = None
    search = None
    date_begin = None
    date_end = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.group = Group.objects.get(name=kwargs['group_name'])
        except ObjectDoesNotExist:
            raise Http404

        try:
            self.shop = shop_from_group(self.group)
        except ValueError:
            self.template_name = 'finances/sale_list.html'
            self.form_class = SaleListSearchDateForm

        return super(SaleList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SaleList, self).get_context_data(**kwargs)

        try:
            context['sale_list'] = Sale.objects.filter(
                category='sale',
                wording='Vente '+self.shop.name
            ).order_by('-date')
        except AttributeError:
            context['sale_list'] = Sale.objects.filter(
                category='sale'
            ).order_by('-date')

        context['sale_list'] = self.form_query(context['sale_list'])[:100]

        return context

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(operator__last_name__contains=self.search)
                | Q(operator__first_name__contains=self.search)
                | Q(operator__surname__contains=self.search)
                | Q(recipient__last_name__contains=self.search)
                | Q(recipient__first_name__contains=self.search)
                | Q(recipient__surname__contains=self.search)
                | Q(sender__last_name__contains=self.search)
                | Q(sender__first_name__contains=self.search)
                | Q(sender__surname__contains=self.search)
            )

        if self.date_begin:
            query = query.filter(
                date__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                date__lte=self.date_end)

        if self.query_shop:
            query = query.filter(
                wording='Vente '+self.query_shop.name
            )

        return query

    def form_valid(self, form):
        if form.cleaned_data['search']:
            self.search = form.cleaned_data['search']

        if form.cleaned_data['date_begin']:
            self.date_begin = form.cleaned_data['date_begin']

        if form.cleaned_data['date_end']:
            self.date_end = form.cleaned_data['date_end']
        try:
            if form.cleaned_data['shop']:
                self.query_shop = form.cleaned_data['shop']
        except KeyError:
            pass
        context = self.get_context_data()
        return self.get(self.request, self.args, self.kwargs)


class SaleRetrieve(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    Retrieve a sale.

    A sale comes from a shop, for other type of transaction, please refer to
    other classes (RechargingRetrieve, TransfertRetrieve,
    ExceptionnalMovementRetrieve).

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['pk']: pk of the sale, mandatory
    :type kwargs['group_name']: string
    :type kwargs['pk']: positiv integer
    :raises: Http404 if group_name doesn't match a group
    :raises: Http404 if the pk doesn't match a sale
    :raises: Http404 if the sale is not from a shop
    :raises: Http404 if the sale is not from the shop derived from the group
    :raises: Http404 if the group doesn't have the permission to retrieve sale
    """
    template_name = 'finances/sale_retrieve.html'
    perm_codename = 'retrieve_sale'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = Sale.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404

        try:
            self.group = Group.objects.get(name=kwargs['group_name'])
        except ObjectDoesNotExist:
            raise Http404

        if self.object.from_shop() is None:
            raise Http404

        try:
            self.shop = shop_from_group(self.group)
            if self.object.from_shop() != self.shop:
                raise Http404
        except ValueError:
            pass

        return super(SaleRetrieve, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)


class RechargingList(GroupPermissionMixin, FormView,
                     GroupLateralMenuFormMixin):
    """
    View to list recharging sales.

    The view handle request of the form to filter recharging sales.
    :note:: only recharging sales are listed here. For other types of
    transactions, please refer to other classes (SaleList, TransfertList and
    ExceptionnalMovementList).

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the group doesn't have the permission to list
    recharging sales
    """
    template_name = 'finances/recharging_list.html'
    perm_codename = 'list_recharging'
    lm_active = 'lm_recharging_list'
    form_class = GenericListSearchDateForm

    search = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super(RechargingList, self).get_context_data(**kwargs)

        context['recharging_list'] = Sale.objects.filter(
            category='recharging'
        ).order_by('-date')

        context['recharging_list'] = self.form_query(
            context['recharging_list'])[:100]

        return context

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(operator__last_name__contains=self.search)
                | Q(operator__first_name__contains=self.search)
                | Q(operator__surname__contains=self.search)
                | Q(recipient__last_name__contains=self.search)
                | Q(recipient__first_name__contains=self.search)
                | Q(recipient__surname__contains=self.search)
                | Q(sender__last_name__contains=self.search)
                | Q(sender__first_name__contains=self.search)
                | Q(sender__surname__contains=self.search)
            )

        if self.date_begin:
            query = query.filter(
                date__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                date__lte=self.date_end)

        return query

    def form_valid(self, form):
        if form.cleaned_data['search'] != '':
            self.search = form.cleaned_data['search']

        if form.cleaned_data['date_begin'] != '':
            self.date_begin = form.cleaned_data['date_begin']

        if form.cleaned_data['date_end'] != '':
            self.date_end = form.cleaned_data['date_end']

        context = self.get_context_data()
        return self.get(self.request, self.args, self.kwargs)


class RechargingRetrieve(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    Retrieve a recharging sale.

    For other type of transaction, please refer to other classes (SaleRetrieve,
    TransfertRetrieve, ExceptionnalMovementRetrieve).

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['pk']: pk of the sale, mandatory
    :type kwargs['group_name']: string
    :type kwargs['pk']: positiv integer
    :raises: Http404 if group_name doesn't match a group
    :raises: Http404 if the pk doesn't match a sale
    :raises: Http404 if the sale is not a recharging sale
    :raises: Http404 if the group doesn't have the permission to retrieve
    recharging sale
    """
    template_name = 'finances/recharging_retrieve.html'
    perm_codename = 'retrieve_recharging'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = Sale.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404

        if self.object.category != 'recharging':
            raise Http404

        return super(RechargingRetrieve, self).dispatch(request, *args,
                                                        **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)


class TransfertList(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    """
    View to list transfert sales.

    The view handle request of the form to filter transfert sales.
    :note:: only transfert sales are listed here. For other types of
    transactions, please refer to other classes (SaleList, RechargingList and
    ExceptionnalMovementList).

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the group doesn't have the permission to list transfert
    sales
    """
    template_name = 'finances/transfert_list.html'
    perm_codename = 'list_transfert'
    lm_active = 'lm_transfert_list'
    form_class = GenericListSearchDateForm

    search = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super(TransfertList, self).get_context_data(**kwargs)

        context['transfert_list'] = Sale.objects.filter(
            category='transfert'
        ).order_by('-date')

        context['transfert_list'] = self.form_query(
            context['transfert_list'])[:100]

        return context

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(operator__last_name__contains=self.search)
                | Q(operator__first_name__contains=self.search)
                | Q(operator__surname__contains=self.search)
                | Q(recipient__last_name__contains=self.search)
                | Q(recipient__first_name__contains=self.search)
                | Q(recipient__surname__contains=self.search)
                | Q(sender__last_name__contains=self.search)
                | Q(sender__first_name__contains=self.search)
                | Q(sender__surname__contains=self.search)
            )

        if self.date_begin:
            query = query.filter(
                date__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                date__lte=self.date_end)

        return query

    def form_valid(self, form):
        if form.cleaned_data['search'] != '':
            self.search = form.cleaned_data['search']

        if form.cleaned_data['date_begin'] != '':
            self.date_begin = form.cleaned_data['date_begin']

        if form.cleaned_data['date_end'] != '':
            self.date_end = form.cleaned_data['date_end']

        context = self.get_context_data()
        return self.get(self.request, self.args, self.kwargs)


class TransfertRetrieve(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    Retrieve a transfert sale.

    For other type of transaction, please refer to other classes (SaleRetrieve,
    RechargingRetrieve, ExceptionnalMovementRetrieve).

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['pk']: pk of the sale, mandatory
    :type kwargs['group_name']: string
    :type kwargs['pk']: positiv integer
    :raises: Http404 if group_name doesn't match a group
    :raises: Http404 if the pk doesn't match a sale
    :raises: Http404 if the sale is not a transfert sale
    :raises: Http404 if the group doesn't have the permission to retrieve
    transfert sale
    """
    template_name = 'finances/transfert_retrieve.html'
    perm_codename = 'retrieve_transfert'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = Sale.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404

        if self.object.category != 'transfert':
            raise Http404

        return super(TransfertRetrieve, self).dispatch(request, *args,
                                                       **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)


class SelfTransfertCreate(GroupPermissionMixin, FormView,
                          GroupLateralMenuFormMixin):
    template_name = 'finances/self_transfert_create.html'
    perm_codename = 'add_transfert'
    lm_active = None
    form_class = SelfTransfertCreate

    def get_form_kwargs(self, **kwargs):
        kwargs = super(SelfTransfertCreate, self).get_form_kwargs(**kwargs)
        kwargs['sender'] = self.request.user
        return kwargs

    def form_valid(self, form):
        sale_transfert(
            sender=self.request.user,
            recipient=form.cleaned_data['recipient'],
            amount=form.cleaned_data['amount'],
            date=now(),
            justification=form.cleaned_data['justification'])
        return super(SelfTransfertCreate, self).form_valid(form)


class ExceptionnalMovementList(GroupPermissionMixin, FormView,
                               GroupLateralMenuFormMixin):
    """
    View to list exceptionnal movement sales.

    The view handle request of the form to filter recharging exceptionnal
    movement.
    :note:: only exceptionnal movement sales are listed here. For other types
    of transactions, please refer to other classes (SaleList, TransfertList and
    SaleList).

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the group doesn't have the permission to list
    exceptionnal movement sales
    """
    template_name = 'finances/exceptionnalmovement_list.html'
    perm_codename = 'list_exceptionnal_movement'
    lm_active = 'lm_exceptionnalmovement_list'
    form_class = GenericListSearchDateForm

    search = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super(ExceptionnalMovementList, self).get_context_data(
            **kwargs)

        context['exceptionnalmovement_list'] = Sale.objects.filter(
            category='exceptionnal_movement'
        ).order_by('-date')

        context['exceptionnalmovement_list'] = self.form_query(
            context['exceptionnalmovement_list'])[:100]

        return context

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(operator__last_name__contains=self.search)
                | Q(operator__first_name__contains=self.search)
                | Q(operator__surname__contains=self.search)
                | Q(recipient__last_name__contains=self.search)
                | Q(recipient__first_name__contains=self.search)
                | Q(recipient__surname__contains=self.search)
                | Q(sender__last_name__contains=self.search)
                | Q(sender__first_name__contains=self.search)
                | Q(sender__surname__contains=self.search)
            )

        if self.date_begin:
            query = query.filter(
                date__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                date__lte=self.date_end)

        return query

    def form_valid(self, form):
        if form.cleaned_data['search'] != '':
            self.search = form.cleaned_data['search']

        if form.cleaned_data['date_begin'] != '':
            self.date_begin = form.cleaned_data['date_begin']

        if form.cleaned_data['date_end'] != '':
            self.date_end = form.cleaned_data['date_end']

        context = self.get_context_data()
        return self.get(self.request, self.args, self.kwargs)


class ExceptionnalMovementRetrieve(GroupPermissionMixin, View,
                                   GroupLateralMenuMixin):
    """
    Retrieve an exceptionnal movement sale.

    For other type of transaction, please refer to other classes (SaleRetrieve,
    TransfertRetrieve, RechargingRetrieve).

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['pk']: pk of the sale, mandatory
    :type kwargs['group_name']: string
    :type kwargs['pk']: positiv integer
    :raises: Http404 if group_name doesn't match a group
    :raises: Http404 if the pk doesn't match a sale
    :raises: Http404 if the sale is not an exceptionnal movement sale
    :raises: Http404 if the group doesn't have the permission to retrieve
    exceptionnal movement sale
    """
    template_name = 'finances/exceptionnalmovement_retrieve.html'
    perm_codename = 'retrieve_exceptionnal_movement'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = Sale.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404

        if self.object.category != 'exceptionnal_movement':
            raise Http404

        return super(ExceptionnalMovementRetrieve, self).dispatch(
            request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)


class SelfTransactionList(GroupPermissionMixin, FormView,
                          GroupLateralMenuFormMixin):
    """
    View to list transactions of the logged user.

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    """
    template_name = 'finances/self_transaction_list.html'
    perm_codename = None
    lm_active = None
    form_class = GenericListSearchDateForm

    search = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super(SelfTransactionList, self).get_context_data(**kwargs)

        context['transaction_list'] = self.form_query(
            self.request.user.list_sale())[:100]
        return context

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(wording__contains=self.search)
                | Q(category__contains=self.search)
            )

        if self.date_begin:
            query = query.filter(
                date__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                date__lte=self.date_end)

        return query

    def form_valid(self, form):
        if form.cleaned_data['search']:
            self.search = form.cleaned_data['search']
        if form.cleaned_data['date_begin']:
            self.date_begin = form.cleaned_data['date_begin']

        if form.cleaned_data['date_end']:
            self.date_end = form.cleaned_data['date_end']
        try:
            if form.cleaned_data['shop']:
                self.query_shop = form.cleaned_data['shop']
        except KeyError:
            pass
        context = self.get_context_data()
        return self.get(self.request, self.args, self.kwargs)



class UserExceptionnalMovementCreate(GroupPermissionMixin, UserMixin, FormView,
                                     GroupLateralMenuFormMixin):
    """
    View to create an exceptionnal movement (debit or credit) for a specific
    user.

    :param kwargs['group_name']: name of the group, mandatory
    :param kwargs['user_pk']: pk of the specific user, mandatory
    :type kwargs['user_pk']: positif integer
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    :raises: Http404 if the user_pk doesn't match an user
    :raises: Http404 if the group doesn't have the permission to add an
    exceptionnal movement
    """
    template_name = 'finances/user_exceptionnalmovement_create.html'
    perm_codename = 'add_exceptionnal_movement'
    lm_active = None
    form_class = ExceptionnalMovementForm

    def form_valid(self, form):
        """
        :note:: The form is assumed clean, then the couple username/password
        for the operator is right.
        """
        operator = authenticate(
            username=form.cleaned_data['operator_username'],
            password=form.cleaned_data['operator_password'])
        amount = form.cleaned_data['amount']
        is_credit = False

        if form.cleaned_data['type_movement'] == 'credit':
            is_credit = True

        sale_exceptionnal_movement(
            operator=operator, affected=self.user,
            is_credit=is_credit, amount=amount,
            date=now(),
            justification=form.cleaned_data['justification'])

        return super(UserExceptionnalMovementCreate, self).form_valid(form)

    def get_initial(self):
        """
        Populate the form with the current login user for the operator (only
        username of course).
        """
        initial = super(UserExceptionnalMovementCreate, self).get_initial()
        initial['operator_username'] = self.request.user.username
        return initial


class UserSupplyMoney(GroupPermissionMixin, UserMixin, FormView,
                      GroupLateralMenuFormMixin):
    template_name = 'finances/user_supplymoney.html'
    perm_codename = 'supply_money_user'
    lm_active = None
    form_class = UserSupplyMoneyForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(UserSupplyMoney, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        """
        :note:: The form is assumed clean, then the couple username/password
        for the operator is right.
        """
        operator = authenticate(
            username=form.cleaned_data['operator_username'],
            password=form.cleaned_data['operator_password'])
        sender = self.user
        payment = []
        if form.cleaned_data['type'] == 'cheque':
            cheque = Cheque.objects.create(
                amount=form.cleaned_data['amount'],
                signature_date=form.cleaned_data['signature_date'],
                cheque_number=form.cleaned_data['unique_number'],
                sender=sender,
                recipient=User.objects.get(username='AE_ENSAM'),
                bank_account=form.cleaned_data['bank_account'])
            payment.append(cheque)

        elif form.cleaned_data['type'] == 'cash':
            cash = Cash.objects.create(
                sender=sender,
                recipient=User.objects.get(username='AE_ENSAM'),
                amount=form.cleaned_data['amount'])
            payment.append(cash)

        elif form.cleaned_data['type'] == 'lydia':
            lydia = Lydia.objects.create(
                date_operation=form.cleaned_data['signature_date'],
                id_from_lydia=form.cleaned_data['unique_number'],
                sender=sender,
                recipient=User.objects.get(username='AE_ENSAM'),
                amount=form.cleaned_data['amount'])
            payment.append(lydia)

        sale_recharging(sender=sender, operator=operator,
                        payments_list=payment, date=now(),
                        wording='Rechargement manuel')

        return super(UserSupplyMoney, self).form_valid(form)

    def get_initial(self):
        """
        Populate the form with the current login user for the operator (only
        username of course).
        """
        initial = super(UserSupplyMoney, self).get_initial()
        initial['signature_date'] = now
        initial['operator_username'] = self.request.user.username
        return initial


class SupplyLydiaSelfView(FormView):
    form_class = SupplyLydiaSelfForm
    template_name = 'finances/lydia_self.html'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Rechargement Lydia auto')
        return super(SupplyLydiaSelfView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SupplyLydiaSelfView, self).get_form_kwargs()
        try:
            kwargs['min_value'] = Setting.objects.get(
                name='LYDIA_MIN_PRICE').get_value()
        except ObjectDoesNotExist:
            kwargs['min_value'] = 0
        try:
            kwargs['max_value'] = Setting.objects.get(
                name='LYDIA_MAX_PRICE').get_value()
        except ObjectDoesNotExist:
            kwargs['max_value'] = 1000
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        if user.phone is None:
            user.phone = form.cleaned_data['tel_number']
            user.save()
        return get_button_lydia(self.request,
                                form.cleaned_data['amount'],
                                form.cleaned_data['tel_number'])

    def get_initial(self):
        initial = super(SupplyLydiaSelfView, self).get_initial()
        initial['tel_number'] = self.request.user.phone
        return initial


def get_button_lydia(request, amount, tel_number):

    vendor_token = settings.LYDIA_VENDOR_TOKEN
    confirm_url = settings.LYDIA_CONFIRM_URL
    callback_url = settings.LYDIA_CALLBACK_URL

    amount = amount
    tel_number = tel_number
    message = (
        "Ajout d'argent compte de"
        + request.user.__str__()
        + "Borgia AE ENSAM")
    return render(request, 'finances/lydia_self_button.html', locals())


class SupplyLydiaSelfConfirmView(View):
    def get(self, request, *args, **kwargs):
        transaction = self.request.GET.get('transaction')
        order = self.request.GET.get('order_ref')
        return render(request, 'finances/lydia_self_confirm.html', locals())


@csrf_exempt
def supply_lydia_self_callback(request):
    """
    Fonction qui permet de catch le callback de Lydia après un paiement
    automatique par carte bancaire.
    Crée une vente entre celui qui a envoyé un paiement et l'AE ENSAM.
    C'est une vente de la catégorie 'rechargement'
    avec comme wording 'rechargement automatique', l'opérateur est l'émetteur
    du paiement lui-même.
    :param user_pk: en GET. Pk correspondant à l'utilisateur qui a envoyé le
    paiement.
    :param currency: en POST. Sigle représentant la monnaie utilisée, ex :
    EUR
    :param request_id: en POST. Id de requete chez Lydia.
    :param amount: en POST. Montant du paiement, dans la monnaie "currency"
    :param signed: en POST. ?
    :param transaction_identifier: en POST. Id de transaction chez Lydia.
    :param vendor_token: en POST. Token de l'AE ENSAM publique.
    :param sig: en POST. Signature générée par Lydia avec l'algorithme Lydia
    :type user_pk: integer strictement positif
    :type currency: chaîne de caractère
    :type request_id: chaîne de caractère
    :type amount: en POST. Montant du paiement, dans la monnaie "currency"
    :type signed: booleen
    :type transaction_identifier: chaîne de caractère
    :type vendor_token: chaîne de caractère
    :type sig: chaîne de caractère

    Remarque : même si certains paramètres ne sont pas utilisés
    (signed, request_id), ils ne sont pas pour autant optionnels. Ils sont en
    effet utilisés pour vérifié la signature.

    :return:
     Erreur 403 si la signature n'est pas la bonne.
     300 si l'utilisateur n'existe pas dans notre base ou s'il manque un
     paramètre.
     200 si tout s'est bien passé : la signature est identifiée, la vente
     créée et l'utilisateur crédité.
    """
    params_dict = {
        "currency": request.POST.get("currency"),
        "request_id": request.POST.get("request_id"),
        "amount": request.POST.get("amount"),
        "signed": request.POST.get("signed"),
        "transaction_identifier": request.POST.get("transaction_identifier"),
        "vendor_token": request.POST.get("vendor_token"),
        "sig": request.POST.get("sig")
    }

    # Verification du token
    if verify_token_algo_lydia(params_dict, settings.LYDIA_API_TOKEN) is True:

        try:
            sale_recharging(
                sender=User.objects.get(pk=request.GET.get('user_pk')),
                operator=User.objects.get(pk=request.GET.get('user_pk')),
                date=now(),
                wording='Rechargement automatique',
                payments_list=[Lydia.objects.create(
                    date_operation=now(),
                    amount=decimal.Decimal(params_dict['amount']),
                    id_from_lydia=params_dict['transaction_identifier'],
                    sender=User.objects.get(pk=request.GET.get('user_pk')),
                    recipient=User.objects.get(username='AE_ENSAM'))])

        except KeyError or ObjectDoesNotExist:
            return HttpResponse('300')

        return HttpResponse('200')

    else:
        raise PermissionDenied


def verify_token_algo_lydia(params, token):
    """
    Fonction qui renvoie Vrai si la requete est valide, c'est à dire si
    l'algorithme vérifie que la signature est valide
    C'est qu'elle est basé sur le bon algorithme, et le bon token
    :param params: dictionnaire des param  tres avec sig dedans
    :param token: token à comparer
    """
    # FONCTION TESTEE ET VALIDEE AVEC REQUESTBIN
    try:
        # G  n  ration de l'hypoth  tique signature
        sig = params['sig']
        del params['sig']
        h_sig_table = []
        # Trie par ordre alphab  tique des noms de param  tres
        sorted_params = sorted(params.items(), key=operator.itemgetter(0))
        # Concat  nation des param  tres et des valeurs
        for p in sorted_params:
            h_sig_table.append(p[0] + '=' + p[1])
        h_sig = '&'.join(h_sig_table)
        # Ajout du token api
        h_sig += '&' + token  # Ce token est priv
        # Hash md5
        h_sig_hash = hashlib.md5(h_sig.encode())
        return h_sig_hash.hexdigest() == sig

    except KeyError:
        return False
