import datetime
import functools
import json
from urllib.parse import urlparse, urlunparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
from django.db.models import Q
from django.http import HttpResponse, QueryDict
from django.shortcuts import render, resolve_url
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.edit import FormView

from borgia.mixins import LateralMenuMixin
from borgia.utils import (INTERNALS_GROUP_NAME, get_managers_group_from_user,
                          is_association_manager)
from events.models import Event
from finances.models import ExceptionnalMovement, Recharging, Transfert
from modules.models import SelfSaleModule
from sales.models import Sale
from shops.utils import get_shops_managed
from shops.models import Shop
from users.forms import UserQuickSearchForm
from users.models import User


class BorgiaView(LateralMenuMixin, View):
    """
    Add Lateral menu mixin to View.
    """


class BorgiaFormView(LateralMenuMixin, SuccessMessageMixin, FormView):
    """
    Add Lateral menu and success message mixins to FormView.
    """


class ModulesLoginView(LoginView):
    """ Override of auth login view, to include direct login to sales modules """
    redirect_authenticated_user = True

    def add_next_to_login(self, path_next, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
        """
        Add the given 'path_next' path to the 'login_url' path.
        """
        resolved_url = resolve_url(login_url or settings.LOGIN_URL)

        login_url_parts = list(urlparse(resolved_url))
        if redirect_field_name:
            querystring = QueryDict(login_url_parts[4], mutable=True)
            querystring[redirect_field_name] = path_next
            login_url_parts[4] = querystring.urlencode(safe='/')

        return urlunparse(login_url_parts)

    def readable_shop_url(self, next, shop_list):
        readable_url = ""
        operator_urls = [l['operator_module_rev_link'] for l in shop_list]
        self_urls = [l['self_module_rev_link'] for l in shop_list]
        shop_urls = operator_urls + self_urls
        if next in shop_urls:
           url_parts = [i for i in next.split("/") if i]
           if "self_sales" in url_parts:
               readable_url = "Vente directe - "
           elif "operator_sales" in url_parts:
               readable_url = "Vente par opérateur - "
           if "shops" in url_parts:
               shop = Shop.objects.get(pk=int(url_parts[1]))
               if shop:
                  readable_url += shop.name.capitalize()
        if readable_url == "":
           readable_url = next
        return readable_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_theme'] = settings.DEFAULT_TEMPLATE

        context['shop_list'] = []
        for shop in Shop.objects.all():
            operator_module = shop.modules_operatorsalemodule_shop.first()
            operator_module_rev_link = reverse('url_shop_module_sale', kwargs={'shop_pk': shop.pk, 'module_class': 'operator_sales'})
            operator_module_link = self.add_next_to_login(operator_module_rev_link)
            self_module = shop.modules_selfsalemodule_shop.first()
            self_module_rev_link = reverse('url_shop_module_sale', kwargs={'shop_pk': shop.pk, 'module_class': 'self_sales'})
            self_module_link = self.add_next_to_login(self_module_rev_link)
            context['shop_list'].append({
                'shop': shop,
                'operator_module': operator_module,
                'operator_module_link': operator_module_link,
                'operator_module_rev_link': operator_module_rev_link,
                'self_module': self_module,
                'self_module_link': self_module_link,
                'self_module_rev_link': self_module_rev_link
            })
        if context['next']:
           context['humanized_next'] = self.readable_shop_url(context['next'], context['shop_list'])
        return context


class MembersWorkboard(LoginRequiredMixin, BorgiaView):
    menu_type = 'members'
    template_name = 'workboards/members_workboard.html'
    lm_active = 'lm_workboard'

    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        context['transaction_list'] = self.get_transactions()
        return render(request, self.template_name, context=context)

    def get_transactions(self):
        transactions = {'months': self.monthlist(
            datetime.datetime.now() - datetime.timedelta(days=365),
            datetime.datetime.now()), 'all': self.request.user.list_transaction()[:5]}

        # Shops sales
        sale_list = Sale.objects.filter(
            sender=self.request.user).order_by('-datetime')
        transactions['shops'] = []
        for shop in Shop.objects.all():
            list_filtered = sale_list.filter(shop=shop)
            total = 0
            for sale in list_filtered:
                total += sale.amount()
            transactions['shops'].append({
                'shop': shop,
                'total': total,
                'sale_list_short': list_filtered[:5],
                'data_months': self.data_months(list_filtered, transactions['months'])
            })

        # Transferts
        transfert_list = Transfert.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        ).order_by('-datetime')
        transactions['transferts'] = {
            'transfert_list_short': transfert_list[:5]
        }

        # Rechargings
        rechargings_list = Recharging.objects.filter(
            sender=self.request.user).order_by('-datetime')
        transactions['rechargings'] = {
            'recharging_list_short': rechargings_list[:5]
        }

        # ExceptionnalMovements
        exceptionnalmovements_list = ExceptionnalMovement.objects.filter(
            recipient=self.request.user).order_by('-datetime')
        transactions['exceptionnalmovements'] = {
            'exceptionnalmovement_list_short': exceptionnalmovements_list[:5]
        }

        # Shared event
        events_list = Event.objects.filter(
            done=True, users=self.request.user).order_by('-datetime')
        for obj in events_list:
            obj.amount = obj.get_price_of_user(self.request.user)

        transactions['events'] = {
            'event_list_short': events_list[:5]
        }

        return transactions

    @staticmethod
    def data_months(mlist, months):
        amounts = [0 for _ in range(0, len(months))]
        for obj in mlist:
            if obj.datetime.strftime("%b-%y") in months:
                amounts[
                    months.index(obj.datetime.strftime("%b-%y"))] +=\
                    abs(obj.amount())
        return amounts

    @staticmethod
    def monthlist(start, end):
        def total_months(dt):
            return dt.month + 12 * dt.year

        mlist = []
        for tot_m in range(total_months(start)-1, total_months(end)):
            y, m = divmod(tot_m, 12)
            mlist.append(datetime.datetime(y, m+1, 1).strftime("%b-%y"))
        return mlist


class ManagersWorkboard(LoginRequiredMixin, PermissionRequiredMixin, BorgiaView):
    menu_type = 'managers'
    template_name = 'workboards/managers_workboard.html'
    lm_active = 'lm_workboard'

    def has_permission(self):
        self.managers_group = get_managers_group_from_user(self.request.user)
        self.shops_managed = get_shops_managed(self.request.user)
        return self.managers_group or self.shops_managed

    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        if (self.managers_group):
            context['group'] = self.managers_group
            context['sale_list'] = Sale.objects.all().order_by('-datetime')[:5]
        elif self.shops_managed:
            context['group'] = self.shops_managed[0]
            context['sale_list'] = self.shops_managed[0].sale_set.all().order_by(
                '-datetime')[:5]
        context['events'] = []
        for event in Event.objects.all():
            context['events'].append({
                'title': event.description,
                'start': event.date
            })

        # Form Quick user search
        context['quick_user_search_form'] = UserQuickSearchForm()
        return render(request, self.template_name, context=context)
