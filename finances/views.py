import json
import operator
import hashlib
import decimal
from datetime import timedelta

from django.shortcuts import render, HttpResponse, force_text, redirect
from django.shortcuts import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from datetime import timedelta
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import FormView, View
from django.contrib.auth.models import Group
from django.conf import settings

from finances.forms import *
from finances.models import *
from borgia.utils import *
from settings_data.models import Setting
from finances.utils import *
from users.models import list_year
from notifications.models import notify


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
        bank_account = BankAccount.objects.create(
            bank=form.cleaned_data['bank'],
            account=form.cleaned_data['account'],
            owner=self.user
        )
        # We notify
        notify(notification_class_name='user_bank_account_creation',
               actor=self.request.user,
               recipient=bank_account.owner,
               target_object=bank_account
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
        # We notify
        notify(notification_class_name='user_bank_account_update',
               actor=self.request.user,
               recipient=self.object.owner,
               target_object=self.object
               )
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
        sales_tab_header = []
        seen = set(sales_tab_header)
        page = self.request.POST.get('page', 1)

        try:
            context['sale_list'] = Sale.objects.filter(shop=self.shop).order_by('-datetime')
        except AttributeError:
            context['sale_list'] = Sale.objects.all().order_by('-datetime')

        # The sale_list is paginated by passing the filtered QuerySet to Paginator
        paginator = Paginator(self.form_query(context['sale_list']), 50)
        try:
            # The requested page is grabbed
            sales = paginator.page(page)
        except PageNotAnInteger:
            # If the requested page is not an integer
            sales = paginator.page(1)
        except EmptyPage:
            # If the requested page is out of range, the last page is grabbed
            sales = paginator.page(paginator.num_pages)

        context['sale_list'] = sales

        for sale in context['sale_list']:
            if sale.from_shop() not in seen:
                seen.add(sale.from_shop())
                sales_tab_header.append(sale.from_shop())

        context['sales_tab_header'] = sales_tab_header

        return context

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(operator__last_name__icontains=self.search)
                | Q(operator__first_name__icontains=self.search)
                | Q(operator__surname__icontains=self.search)
                | Q(operator__username__icontains=self.search)
                | Q(recipient__last_name__icontains=self.search)
                | Q(recipient__first_name__icontains=self.search)
                | Q(recipient__surname__icontains=self.search)
                | Q(recipient__username__icontains=self.search)
                | Q(sender__last_name__icontains=self.search)
                | Q(sender__first_name__icontains=self.search)
                | Q(sender__surname__icontains=self.search)
                | Q(sender__username__icontains=self.search)
            )

        if self.date_begin:
            query = query.filter(
                datetime__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                datetime__lte=self.date_end)

        if self.query_shop:
            query = query.filter(shop=self.query_shop)

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
    form_class = RechargingListForm

    search = None
    date_end = now() + timedelta(days=1)
    date_begin = now() - timedelta(days=7)
    operators = None

    def get_context_data(self, **kwargs):
        context = super(RechargingList, self).get_context_data(**kwargs)

        context['recharging_list'] = Recharging.objects.all().order_by('-datetime')

        context['recharging_list'] = self.form_query(
            context['recharging_list'])[:100]

        context['info'] = self.info(context['recharging_list'])
        return context

    def get_initial(self, **kwargs):
        initial = super(RechargingList, self).get_initial(**kwargs)
        initial['date_begin'] = self.date_begin
        initial['date_end'] = self.date_end
        return initial

    def info(self, query):
        info = {
            'cash': {
                'total': 0,
                'nb': 0
            },
            'cheque': {
                'total': 0,
                'nb': 0,
                'ids': Cheque.objects.none()
            },
            'lydia_face2face': {
                'total': 0,
                'nb': 0,
                'ids': LydiaFaceToFace.objects.none()
            },
            'lydia_online': {
                'total': 0,
                'nb': 0,
                'ids': LydiaOnline.objects.none()
            },
            'total': {
                'total': 0,
                'nb': 0
            }
        }

        for r in query:
            if r.payment_solution.get_type() == 'cash':
                info['cash']['total'] += r.payment_solution.amount
                info['cash']['nb'] += 1
            if r.payment_solution.get_type() == 'cheque':
                info['cheque']['total'] += r.payment_solution.amount
                info['cheque']['nb'] += 1
                info['cheque']['ids'] |= [r.payment_solution.cheque]
            if r.payment_solution.get_type() == 'lydiafacetoface':
                info['lydia_face2face']['total'] += r.payment_solution.amount
                info['lydia_face2face']['nb'] += 1
                info['lydia_face2face']['ids'] |= [r.payment_solution.lydiafacetoface]
            if r.payment_solution.get_type() == 'lydiaonline':
                info['lydia_online']['total'] += r.payment_solution.amount
                info['lydia_online']['nb'] += 1
                info['lydia_online']['ids'] |= [r.payment_solution.lydiaonline]
            info['total']['total'] += r.payment_solution.amount
            info['total']['nb'] += 1
        return info

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(operator__last_name__contains=self.search)
                | Q(operator__first_name__contains=self.search)
                | Q(operator__surname__contains=self.search)
                | Q(sender__last_name__contains=self.search)
                | Q(sender__first_name__contains=self.search)
                | Q(sender__surname__contains=self.search)
            )

        if self.date_begin:
            query = query.filter(
                datetime__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                datetime__lte=self.date_end)

        if self.operators:
            query = query.filter(operator__in=self.operators)

        return query

    def form_valid(self, form):
        if form.cleaned_data['search'] != '':
            self.search = form.cleaned_data['search']

        if form.cleaned_data['date_begin'] != '':
            self.date_begin = form.cleaned_data['date_begin']

        if form.cleaned_data['date_end'] != '':
            self.date_end = form.cleaned_data['date_end']

        if form.cleaned_data['operators']:
            self.operators = form.cleaned_data['operators']

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
            self.object = Recharging.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
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

        context['transfert_list'] = Transfert.objects.all().order_by('-datetime')

        context['transfert_list'] = self.form_query(
            context['transfert_list'])[:100]

        return context

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(recipient__last_name__contains=self.search)
                | Q(recipient__first_name__contains=self.search)
                | Q(recipient__surname__contains=self.search)
                | Q(sender__last_name__contains=self.search)
                | Q(sender__first_name__contains=self.search)
                | Q(sender__surname__contains=self.search)
            )

        if self.date_begin:
            query = query.filter(
                datetime__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                datetime__lte=self.date_end)

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
            self.object = Transfert.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
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
    lm_active = 'lm_self_transfert_create'
    form_class = SelfTransfertCreate

    def get_form_kwargs(self, **kwargs):
        kwargs = super(SelfTransfertCreate, self).get_form_kwargs(**kwargs)
        kwargs['sender'] = self.request.user
        return kwargs

    def form_valid(self, form):
        transfert = Transfert.objects.create(
            sender=self.request.user,
            recipient=form.cleaned_data['recipient'],
            amount=form.cleaned_data['amount'],
            justification=form.cleaned_data['justification']
        )
        transfert.pay()
        # We notify
        notify(notification_class_name= 'transfer_creation',
               actor=self.request.user,
               recipient= form.cleaned_data['recipient'],
               target_object=transfert)
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

        context['exceptionnalmovement_list'] = ExceptionnalMovement.objects.all().order_by('-datetime')

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
            )

        if self.date_begin:
            query = query.filter(
                datetime__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                datetime__lte=self.date_end)

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
            self.object = ExceptionnalMovement.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
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
    lm_active = 'lm_self_transaction_list'
    form_class = GenericListSearchDateForm

    search = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super(SelfTransactionList, self).get_context_data(**kwargs)

        context['transaction_list'] = self.form_query(
            self.request.user.list_transaction())[:100]
        return context

    # TODO: form to be used
    def form_query(self, query):
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

        exceptionnal_movement = ExceptionnalMovement.objects.create(
            justification=form.cleaned_data['justification'],
            operator=operator,
            recipient=self.user,
            is_credit=is_credit,
            amount=amount
        )
        exceptionnal_movement.pay()

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
            payment = cheque

        elif form.cleaned_data['type'] == 'cash':
            cash = Cash.objects.create(
                sender=sender,
                recipient=User.objects.get(username='AE_ENSAM'),
                amount=form.cleaned_data['amount'])
            payment = cash

        elif form.cleaned_data['type'] == 'lydia':
            lydia = LydiaFaceToFace.objects.create(
                date_operation=form.cleaned_data['signature_date'],
                id_from_lydia=form.cleaned_data['unique_number'],
                sender=sender,
                recipient=User.objects.get(username='AE_ENSAM'),
                amount=form.cleaned_data['amount'])
            payment = lydia

        recharging = Recharging.objects.create(
            sender=sender,
            operator=operator,
            payment_solution=payment
        )
        recharging.pay()

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


class SelfLydiaCreate(GroupPermissionMixin, FormView,
                      GroupLateralMenuFormMixin):
    """
    View to supply himself by Lydia.

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    :raises: Http404 if the group_name doesn't match a group
    """
    form_class = SelfLydiaCreateForm
    template_name = 'finances/self_lydia_create.html'
    perm_codename = None
    lm_active = 'lm_self_lydia_create'

    def get_form_kwargs(self):
        kwargs = super(SelfLydiaCreate, self).get_form_kwargs()
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
        """
        Save the current phone number as default phone number for the user.
        Render the Lydia button.
        """
        user = self.request.user
        if user.phone is None:
            user.phone = form.cleaned_data['tel_number']
            user.save()

        context = super(SelfLydiaCreate, self).get_context_data()
        context['vendor_token'] = settings.LYDIA_VENDOR_TOKEN
        context['confirm_url'] = settings.LYDIA_CONFIRM_URL
        context['callback_url'] = settings.LYDIA_CALLBACK_URL
        context['amount'] = form.cleaned_data['amount']
        context['tel_number'] = form.cleaned_data['tel_number']
        context['message'] = (
            "Borgia - AE ENSAM - Crédit de "
            + user.__str__())
        return render(self.request,
                      'finances/self_lydia_button.html',
                      context=context)

    def get_initial(self):
        initial = super(SelfLydiaCreate, self).get_initial()
        initial['tel_number'] = self.request.user.phone
        return initial


class SelfLydiaConfirm(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    View to confirm supply by Lydia.

    This view is only here to have some indications for the user. It does
    nothing more and can be "generated" with GET irelevant GET parameters.

    :note:: transaction and order parameters are given by Lydia but aren't
    used here.

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    :param GET['transaction']: id of the Lydia transaction, mandatory.
    :type GET['transaction']: string
    :param GET['order']: id of the order from Lydia, mandatory.
    :type GET['order']: string
    :raises: Http404 if the group_name doesn't match a group
    """
    perm_codename = None
    template_name = 'finances/self_lydia_confirm.html'

    # TODO: check if a Lydia object exist and if it's from the current day,
    # else raise Error
    def get(self, request, *args, **kwargs):
        context = super(SelfLydiaConfirm, self).get_context_data()
        context['transaction'] = self.request.GET.get('transaction')
        context['order'] = self.request.GET.get('order_ref')
        return render(request, self.template_name, context=context)


class SelfSharedEventList(GroupPermissionMixin, View, GroupLateralMenuMixin):
    perm_codename = None
    template_name = 'finances/self_sharedevent_list.html'
    lm_active = 'lm_self_sharedevent_list'

    def get(self, request, *args, **kwargs):
        context = super(SelfSharedEventList, self).get_context_data(**kwargs)
        context['sharedevent_list'] = SharedEvent.objects.filter(
            done=False).order_by('-date')
        return render(request, self.template_name, context=context)


class SelfSharedEventRegistration(GroupPermissionMixin, View):
    perm_codename = None

    def get(self, request, *args, **kwargs):
        try:
            se = SharedEvent.objects.get(pk=kwargs['pk'])
            if se.allow_self_registeration:
                if request.user not in se.users.all():
                    se.users.add(request.user)
                    se.save()
        except ObjectDoesNotExist:
            pass
        try:
            self.group = Group.objects.get(name=request.GET.get('group_name'))
        except ObjectDoesNotExist:
            pass

        return redirect(reverse(
            'url_self_sharedevent_list',
            kwargs={'group_name': self.group.name}
        ))


class SharedEventCreate(GroupPermissionMixin, FormView,
                        GroupLateralMenuFormMixin):
    form_class = SharedEventCreateForm
    template_name = 'finances/sharedevent_create.html'
    success_url = None
    perm_codename = None
    lm_active = 'lm_sharedevent_create'

    def form_valid(self, form):

        se = SharedEvent.objects.create(
            description=form.cleaned_data['description'],
            date=form.cleaned_data['date'],
            allow_self_registeration=form.cleaned_data['allow_self_registeration'],
            manager=self.request.user)
        if form.cleaned_data['price']:
            se.price = form.cleaned_data['price']
        if form.cleaned_data['bills']:
            se.bills = form.cleaned_data['bills']
        se.save()

        self.success_url = reverse(
            'url_sharedevent_update',
            kwargs={'group_name': self.group.name, 'pk': se.pk}
        )

        return super(SharedEventCreate, self).form_valid(form)


class SharedEventDelete(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    Delete a sharedevent and redirect to the list of sharedevents.

    :param kwargs['group_name']: name of the group used.
    :param kwargs['pk']: pk of the event
    :param self.perm_codename: codename of the permission checked.
    """
    template_name = 'finances/sharedevent_delete.html'
    success_url = None
    perm_codename = None  # Checked in dispatch

    def dispatch(self, request, *args, **kwargs):
        try:
            self.se = SharedEvent.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404

        # Permissions
        try:
            group = Group.objects.get(name=kwargs['group_name'])
        except ObjectDoesNotExist:
            raise Http404
        try:
            if Permission.objects.get(codename='manage_sharedevent') not in group.permissions.all():
                if request.user != self.se.manager:
                    raise PermissionDenied
        except ObjectDoesNotExist:
            raise Http404
        if self.se.done:
            raise PermissionDenied

        return super(SharedEventDelete, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.se
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        self.se.delete()
        if self.group.name == 'gadzarts':
            return redirect(
                reverse(
                    'url_self_sharedevent_list',
                    kwargs={'group_name': self.group.name}
                    ))
        return redirect(
            reverse(
                'url_sharedevent_list',
                kwargs={'group_name': self.group.name}
                ))


class SharedEventFinish(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    """
    Finish a sharedevent and redirect to the list of sharedevents.
    This command is used when you want to keep the event in the database, but
    you don't want to pay in Borgia (for instance paid with real money).

    :param kwargs['group_name']: name of the group used.
    :param kwargs['pk']: pk of the event
    :param self.perm_codename: codename of the permission checked.
    """
    form_class = SharedEventFinishForm
    template_name = 'finances/sharedevent_finish.html'
    success_url = None
    perm_codename = None  # Checked in dispatch

    def dispatch(self, request, *args, **kwargs):
        try:
            self.se = SharedEvent.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404

        # Permissions
        try:
            group = Group.objects.get(name=kwargs['group_name'])
        except ObjectDoesNotExist:
            raise Http404
        try:
            if Permission.objects.get(codename='manage_sharedevent') not in group.permissions.all():
                if request.user != self.se.manager:
                    raise PermissionDenied
        except ObjectDoesNotExist:
            raise Http404
        if self.se.done:
            raise PermissionDenied

        return super(SharedEventFinish, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SharedEventFinish, self).get_context_data(**kwargs)
        context['object'] = self.se
        return context

    def form_valid(self, form):
        self.se.done = True
        self.se.remark = form.cleaned_data['remark']
        self.se.save()
        if self.group.name == 'gadzarts':
            return redirect(
                reverse(
                    'url_self_sharedevent_list',
                    kwargs={'group_name': self.group.name}
                    ))
        return redirect(
            reverse(
                'url_sharedevent_list',
                kwargs={'group_name': self.group.name}
                ))


class SharedEventUpdate(GroupPermissionMixin, View, GroupLateralMenuMixin):
    template_name = 'finances/sharedevent_update.html'
    perm_codename = None

    def get_query_user(self, state):
        se = SharedEvent.objects.get(pk=self.kwargs['pk'])
        if state == 'users':
            return se.list_of_users_ponderation()
        elif state == 'participants':
            return se.list_of_participants_ponderation()
        elif state == 'registrants':
            return se.list_of_registrants_ponderation()

    @staticmethod
    def get_key(item, order_by):
        return getattr(item, order_by)

    def get(self, request, *args, **kwargs):

        # Variables
        try:
            se = SharedEvent.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        # state = ''
        # initial_list_user_form = {}

        query_user = []
        payment_error = ''

        # Vérification des permissions
        # Si on a la perm on peut voir toujours (mais plus tout faire, cf les autres fonctions)
        # Si on est juste manager, on ne peux plus voir si done=True
        try:
            if Permission.objects.get(codename='manage_sharedevent') not in self.group.permissions.all():
                if request.user != se.manager:
                    raise PermissionDenied
        except ObjectDoesNotExist:
            raise Http404

        # # TODO Si on impose un state directement en GET (en venant d'un lien remove par exemple).
        # if self.request.GET.get('state') is not None:
        #     if self.request.GET.get('state') == 'users':
        #         initial_list_user_form = {
        #             'state': 'users',
        #             'order_by': 'username',
        #         }
        #         query_user = sorted(self.get_query_user('users'), key=lambda item: getattr(item[0], 'username'))
        #         state = 'users'
        #     elif self.request.GET.get('state') == 'participants':
        #         initial_list_user_form = {
        #             'state': 'participants',
        #             'order_by': 'username',
        #         }
        #         query_user = sorted(self.get_query_user('participants'), key=lambda item: getattr(item[0], 'username'))
        #         state = 'participants'
        #     elif self.request.GET.get('state') == 'registered':
        #         initial_list_user_form = {
        #             'state': 'registered',
        #             'order_by': 'username',
        #         }
        #         query_user = sorted(self.get_query_user('registrants'), key=lambda item: getattr(item[0], 'username'))
        #         state = 'registrants'
        #
        # # Sinon on choisit en fonction de la date de l'event
        # # S'il est passé, on liste les participants par défaut, sinon on liste les préinscrits
        # else:
        state = 'users'
        order_by = 'username'

        initial_list_user_form = {
            'state': state,
            'order_by': order_by,
        }
        query_user = sorted(self.get_query_user(state), key=lambda item: getattr(item[0], order_by))


        initial_update_form = {
            'price': se.price,
            'bills': se.bills,
        }

        if request.GET.get('no_price') == 'True':
            payment_error = 'Veuillez renseigner le prix de l\'événement ! '

        if request.GET.get('no_participant') == 'True':
            payment_error = 'Veuillez ajouter au moins un participant à l\'événement ! '

        # Création des forms
        list_user_form = SharedEventManageUserListForm(prefix='list_user_form', initial=initial_list_user_form)
        update_form = SharedEventManageUpdateForm(prefix='update_form', initial=initial_update_form)
        upload_json_form = SharedEventManageUploadJSONForm(prefix='upload_json_form')
        add_user_form = SharedEventManageAddForm(prefix='add_user_form')
        download_xlsx_form = SharedEventManageDownloadXlsxForm(prefix='download_xlsx_form',
                                                               list_year=list_year())

        context = super(SharedEventUpdate, self).get_context_data(**kwargs)
        context['pk'] = kwargs['pk']
        context['list_user_form'] = list_user_form
        context['upload_json_form'] = upload_json_form
        context['update_form'] = update_form
        context['add_user_form'] = add_user_form
        context['download_xlsx_form'] = download_xlsx_form
        context['query_user'] = query_user
        context['errors'] = 0
        context['state'] = state
        context['order_by'] = order_by
        context['done'] = se.done
        context['payment_error'] = payment_error
        context['remark'] = se.remark
        context['price'] = se.price

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        # Variables
        try:
            se = SharedEvent.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        errors = 0

        # Vérification des permissions
        try:
            if Permission.objects.get(codename='manage_sharedevent') not in self.group.permissions.all() and request.user != se.manager:
                raise PermissionDenied
            state = request.POST.get('state')
            order_by = request.POST.get('order_by')
        except ObjectDoesNotExist:
            raise Http404

        query_user = []
        try:
            query_user = sorted(self.get_query_user(state), key=lambda item: getattr(item[0], order_by))
        except TypeError:
            pass

        # Liaison des forms et détermination du form qui a été submited
        initial_update_form = {
            'price': se.price,
            'bills': se.bills,
        }
        initial_list_user_form = {
            'state': state,
            'order_by': order_by
        }
        list_user_form = SharedEventManageUserListForm(prefix='list_user_form', initial=initial_list_user_form)
        update_form = SharedEventManageUpdateForm(prefix='update_form', initial=initial_update_form)
        upload_json_form = SharedEventManageUploadJSONForm(prefix='upload_json_form')
        add_user_form = SharedEventManageAddForm(prefix='add_user_form')
        download_xlsx_form = SharedEventManageDownloadXlsxForm(prefix='download_xlsx_form',
                                                               list_year=list_year())
        action = self.request.POST['action']

        # Si form list_user_form
        if action == 'list_user':
            list_user_form = SharedEventManageUserListForm(request.POST, prefix='list_user_form')
            if list_user_form.is_valid():
                if list_user_form.cleaned_data['state'] == 'users':
                    query_user = self.get_query_user('users')
                    state = 'users'
                if list_user_form.cleaned_data['state'] == 'participants':
                    query_user = self.get_query_user('participants')
                    state = 'participants'
                if list_user_form.cleaned_data['state'] == 'registrants':
                    query_user = self.get_query_user('registrants')
                    state = 'registrants'
                order_by = list_user_form.cleaned_data['order_by']
                query_user = sorted(query_user, key=lambda item: getattr(item[0], order_by))

        # Si form update
        if action == 'update':
            update_form = SharedEventManageUpdateForm(request.POST, prefix='update_form')
            if update_form.is_valid():
                se.price = update_form.cleaned_data['price']
                se.bills = update_form.cleaned_data['bills']
                se.save()

        # Si form upload_json
        elif action == 'upload_json':
            upload_json_form = SharedEventManageUploadJSONForm(request.POST, request.FILES,  prefix='upload_json_form')
            if upload_json_form.is_valid():
                lists = list_user_ponderation_errors_from_list(request.FILES['upload_json_form-file'],
                                                               False)
                # Enregistrement des participants/préinscrits et des pondérations
                if upload_json_form.cleaned_data['state'] == 'participants':
                    for i, u in enumerate(lists[0]):
                        try:
                            if lists[1][i] > 0:
                                se.add_participant(u, lists[1][i], True)
                        except KeyError:
                            pass
                else:
                    for u in lists[0]:
                        se.registered.add(u)
                se.save()

                errors = len(lists[2])
                query_user = self.get_query_user(state)

        elif action == 'add_user':
            add_user_form = SharedEventManageAddForm(request.POST, prefix='add_user_form')
            if add_user_form.is_valid():
                isParticipant = add_user_form.cleaned_data['state'] == 'participant' # True pour un participant

                se.add_participant(User.objects.get(username=add_user_form.cleaned_data['username']),
                                    add_user_form.cleaned_data['ponderation'], isParticipant)
                query_user = self.get_query_user(state)

        elif action == 'download_xlsx':
            download_xlsx_form = SharedEventManageDownloadXlsxForm(request.POST, prefix='download_xlsx_form', list_year=list_year())
            if download_xlsx_form.is_valid():

                # Initialisation du fichier excel
                workbook, worksheet, response = workboot_init(se.__str__(), 'Feuil1.XLSM_to_JSON',
                                                              'Générer le fichier JSON')

                # Ajout de l'entête de la table
                worksheet_write_line(workbook=workbook, worksheet=worksheet,
                                     data=[['Nom prénom', 'Bucque', 'Username', 'Pondération']],
                                     bold=True)

                if download_xlsx_form.cleaned_data['state'] == 'year':
                    # Ajout des valeurs
                    list_year_result = []
                    data = []
                    for i in range(0, len(list_year())):
                        if download_xlsx_form.cleaned_data["field_year_%s" % i] is True:
                            list_year_result.append(list_year()[i])
                    for u in User.objects.filter(year__in=list_year_result).exclude(groups=Group.objects.get(pk=1)).order_by('last_name'):
                        data.append([u.last_name + ' ' + u.first_name, u.surname, u.username])
                    worksheet_write_line(workbook=workbook, worksheet=worksheet, data=data, init_row=1)
                    workbook.close()
                    return response

                elif download_xlsx_form.cleaned_data['state'] == 'participants':
                    data = []
                    for e in se.list_of_participants_ponderation():
                        u = e[0]
                        data.append([u.last_name + ' ' + u.first_name, u.surname, u.username, e[1]])
                    worksheet_write_line(workbook=workbook, worksheet=worksheet, data=data, init_row=1)
                    workbook.close()
                    return response

                elif download_xlsx_form.cleaned_data['state'] == 'registered':
                    data = []
                    for e in se.list_of_registrants_ponderation():
                        u = e[0]
                        data.append([u.last_name + ' ' + u.first_name, u.surname, u.username, e[1]])
                    worksheet_write_line(workbook=workbook, worksheet=worksheet, data=data, init_row=1)
                    workbook.close()
                    return response

        context = super(SharedEventUpdate, self).get_context_data(**kwargs)
        context['pk'] = kwargs['pk']
        context['list_user_form'] = list_user_form
        context['upload_json_form'] = upload_json_form
        context['update_form'] = update_form
        context['add_user_form'] = add_user_form
        context['download_xlsx_form'] = download_xlsx_form
        context['query_user'] = query_user
        context['errors'] = errors
        context['state'] = state
        context['order_by'] = order_by
        context['done'] = se.done
        context['remark'] = se.remark
        context['price'] = se.price

        return render(request, self.template_name, context=context)


class SharedEventList(GroupPermissionMixin, FormView,
                      GroupLateralMenuFormMixin):
    template_name = 'finances/sharedevent_list.html'
    lm_active = 'lm_sharedevent_list'
    perm_codename = 'list_sharedevent'
    form_class = SharedEventManageListForm

    def form_valid(self, form, **kwargs):

        date_begin = form.cleaned_data['date_begin']
        date_end = form.cleaned_data['date_end']
        all = form.cleaned_data['all']
        order_by = form.cleaned_data['order_by']
        done = form.cleaned_data['done']
        if done != 'both':

            if done == 'False':
                done = False
            elif done == 'True':
                done = True

            if all is True:
                query_shared_event = SharedEvent.objects.filter(done=done)
            else:
                if date_end is None:
                    query_shared_event = SharedEvent.objects.filter(date__gte=date_begin, done=done)
                else:
                    query_shared_event = SharedEvent.objects.filter(date__range=[date_begin, date_end], done=done)
        else:
            if all is True:
                query_shared_event = SharedEvent.objects.all()
            else:
                if date_end is None:
                    query_shared_event = SharedEvent.objects.filter(date__gte=date_begin)
                else:
                    query_shared_event = SharedEvent.objects.filter(date__range=[date_begin, date_end])
        context = self.get_context_data(**kwargs)
        context['query_shared_event'] = query_shared_event.order_by(order_by).order_by('-date')
        return self.render_to_response(context)

    def get_initial(self):
        initial = super(SharedEventList, self).get_initial()
        initial['date_begin'] = now()
        initial['all'] = True
        initial['done'] = False
        return initial

    def get_context_data(self, **kwargs):
        context = super(SharedEventList, self).get_context_data(**kwargs)
        context['query_shared_event'] = SharedEvent.objects.filter(done=False).order_by('-date')
        return context


class SharedEventRmParticipant(GroupPermissionMixin, View):
    perm_codename = None

    def get(self, request, *args, **kwargs):
        se = SharedEvent.objects.get(pk=kwargs['pk'])

        if (request.user != se.manager
                and request.user.has_perm('finances.change_sharedevent')
                is False):
            raise PermissionDenied
        elif se.done is True:
            raise PermissionDenied

        try:
            user_pk = kwargs['participant_pk']
            if user_pk == 'ALL':
                for u in se.participants.all():
                    se.remove_participant(u)
            else:
                se.remove_participant(User.objects.get(pk=user_pk))
        except ObjectDoesNotExist:
            pass

        return redirect(reverse(
            'url_sharedevent_update',
            kwargs={'group_name': self.group.name, 'pk': se.pk}
        ) + '#table_users')# TODO : Keep user search parameters. Ex : '?state=participants#table_users')


class SharedEventRmRegistered(GroupPermissionMixin, View):
    perm_codename = None

    def get(self, request, *args, **kwargs):
        se = SharedEvent.objects.get(pk=kwargs['pk'])

        if (request.user != se.manager
                and request.user.has_perm('finances.change_sharedevent')
                is False):
            raise PermissionDenied
        # Même en ayant la permission, on ne modifie plus une event terminé
        elif se.done is True:
            raise PermissionDenied
        # Si la date est passé et que le payment n'est pas fait, on ne modifie plus les préinscrits
        elif datetime.date(now()) > se.date:
            raise PermissionDenied

        try:
            user_pk = kwargs['registered_pk']
            if user_pk == 'ALL':
                for u in se.registered.all():
                    se.registered.remove(u)
                se.save()
            else:
                se.registered.remove(User.objects.get(pk=user_pk))
                se.save()
        except ObjectDoesNotExist:
            pass

        return redirect(reverse(
            'url_sharedevent_update',
            kwargs={'group_name': self.group.name, 'pk': se.pk}
        ) + '#table_users')# TODO : Keep user search parameters. Ex : '?state=participants#table_users')


class SharedEventProceedPayment(GroupPermissionMixin, View):
    perm_codename = None

    def get(self, request, *args, **kwargs):
        try:
            se = SharedEvent.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        if se.done is True:
            raise PermissionDenied
        if se.price is not None:
            if se.users.count() > 0:
              se.pay(request.user, User.objects.get(pk=1))
              return redirect(reverse(
                'url_sharedevent_update',
                kwargs={'group_name': self.group.name, 'pk': se.pk}
              ))
            else:
              return redirect(reverse(
                'url_sharedevent_update',
                kwargs={'group_name': self.group.name, 'pk': se.pk}
              ) + '?no_participant=True')

        else:
            return redirect(reverse(
                'url_sharedevent_update',
                kwargs={'group_name': self.group.name, 'pk': se.pk}
            ) + '?no_price=True')


class SharedEventChangePonderation(GroupPermissionMixin, View):
    perm_codename = None

    def get(self, request, *args, **kwargs):
        """
        Change la valeur de la pondération d'un participant user pour un événement
        Permissions :   Si événements terminé -> denied,
                        Si pas manager ou pas la perm 'finances.manage_sharedevent' -> denied
        :param pk: pk de l'événement
        :param user_pk: paramètre GET correspondant au pk de l'user
        :param pond_pk: paramètre GET correspondant à la nouvelle pondération
        :type pk, user_pk, pond_pk: int
        """

        try:
            # Variables d'entrées
            se = SharedEvent.objects.get(pk=kwargs['pk'])
            user = User.objects.get(pk=kwargs['participant_pk'])
            pond = int(request.GET['pond'])

            # Permission
            if request.user != se.manager and request.user.has_perm('finances.manage_sharedevent') is False:
                raise PermissionDenied
            # Même en ayant la permission, on ne modifie plus une event terminé
            elif se.done is True:
                raise PermissionDenied

            if pond > 0:
                # Changement de la pondération
                se.add_participant(user, pond, True)

                # Réponse
                response = pond
            else:
                response = 0

        except KeyError:
            response = 0
        except ObjectDoesNotExist:
            response = 0
        except ValueError:
            response = 0

        return HttpResponse(response)

@csrf_exempt
def self_lydia_callback(request):
    """
    Function to catch the callback from Lydia after a payment.

    Create all objects needed to have a proper sale in the database, and credit
    the client.

    :param GET['user_pk']: pk of the client, mandatory.
    :param POST['currency']: icon of the currency, for instance EUR, mandatory.
    :param POST['request_id']: request id from lydia, mandatory.
    :param POST['amount']: amount of the transaction, in 'currency', mandatory.
    :param POST['signed']: internal to Lydia ?
    :param POST['transaction_identifier']: transaction id from Lydia,
    mandatory.
    :param POST['vendor_token']: public key of the association, mandatory.
    :param POST['sig']: signatory generated by Lydia to identify the
    transaction, mandator.
    :type GET['user_pk']: positiv integer
    :type POST['currency']: string
    :type POST['request_id: string
    :type POST['amount']: float (decimal)
    :type POST['signed']: boolean
    :type POST['transaction_identifier']: string
    :type POST['vendor_token']: string
    :type POST['sig']: string

    :note:: Even if some parameters tend to be useless (signed, request_id),
    they are mandatory because used to generated the signatory and verify the
    transaction.

    :raises: PermissionDenied if signatory generated is not sig.
    :returns: 300 if the user_pk doesn't match an user.
    :returns: 300 if a parameter is missing.
    :returns: 200 if all's good.
    :rtype: Http request
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
    if verify_token_algo_lydia(params_dict, settings.LYDIA_API_TOKEN) is True:
        try:
            lydia = LydiaOnline.objects.create(
                sender=User.objects.get(pk=request.GET.get('user_pk')),
                recipient=User.objects.get(username='AE_ENSAM'),
                amount=decimal.Decimal(params_dict['amount']),
                id_from_lydia=params_dict['transaction_identifier']
            )
            recharging = Recharging.objects.create(
                sender=User.objects.get(pk=request.GET.get('user_pk')),
                operator=User.objects.get(pk=request.GET.get('user_pk')),
                payment_solution=lydia.paymentsolution_ptr
            )
            recharging.pay()
        except KeyError:
            return HttpResponse('300')
        except ObjectDoesNotExist:
            return HttpResponse('300')
        return HttpResponse('200')
    else:
        raise PermissionDenied


def verify_token_algo_lydia(params, token):
    """
    Verify request parameters according to Lydia's algorithm.

    If parameters are valid, the request is authenticated to be from Lydia and
    can be safely used.
    :note:: sig must be contained in the parameters dictionary.

    :warning:: token is private and must never be revealed.

    :param params: all parameters, including sig, mandatory.
    :type params: python dictionary
    :param token: token to be compared, mandatory.
    :type token: string

    :returns: True if parameters are valid, False else.
    :rtype: Boolean
    """
    try:
        sig = params['sig']
        del params['sig']
        h_sig_table = []
        sorted_params = sorted(params.items(), key=operator.itemgetter(0))
        for p in sorted_params:
            h_sig_table.append(p[0] + '=' + p[1])
        h_sig = '&'.join(h_sig_table)
        h_sig += '&' + token
        h_sig_hash = hashlib.md5(h_sig.encode())
        return h_sig_hash.hexdigest() == sig

    except KeyError:
        return False
