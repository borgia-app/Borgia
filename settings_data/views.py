from django.utils.timezone import now
from django.shortcuts import render, redirect, Http404, reverse
from django.conf import settings

from django.contrib.auth.models import Group
from django.views.generic import FormView, View
from django.core.exceptions import ObjectDoesNotExist

from settings_data.forms import PriceConfigForm, LydiaConfigForm, BalanceConfigForm
from settings_data.models import Setting
from borgia.utils import (GroupPermissionMixin, GroupLateralMenuFormMixin,
                          GroupLateralMenuMixin,
                          lateral_menu)
from settings_data.utils import settings_safe_get


class GlobalConfig(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    View to manage config of the application.

    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    """
    template_name = 'settings_data/global_config.html'
    perm_codename = 'change_setting'
    lm_active = 'lm_global_config'

    def get_context_data(self, **kwargs):
        context = super(GlobalConfig, self).get_context_data(**kwargs)
        context['margin_profit'] = settings_safe_get('MARGIN_PROFIT')
        context['lydia_min_price'] = settings_safe_get('LYDIA_MIN_PRICE')
        context['lydia_max_price'] = settings_safe_get("LYDIA_MAX_PRICE")
        context['balance_threshold_mail_alert'] = settings_safe_get("BALANCE_THRESHOLD_MAIL_ALERT")
        context['balance_frequency_mail_alert'] = settings_safe_get("BALANCE_FREQUENCY_MAIL_ALERT")
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)


class PriceConfig(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    """
    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'settings_data/price_config.html'
    perm_codename = 'change_setting'
    lm_active = 'lm_global_config'
    form_class = PriceConfigForm

    def get_initial(self, **kwargs):
        initial = super(PriceConfig, self).get_initial(**kwargs)
        initial['margin_profit'] = settings_safe_get('MARGIN_PROFIT').get_value()
        return initial

    def form_valid(self, form):
        # Margin profit
        margin_profit = settings_safe_get('MARGIN_PROFIT')
        margin_profit.value = form.cleaned_data['margin_profit']
        margin_profit.save()
        return redirect(reverse('url_global_config',
                        kwargs={'group_name': self.group.name}))


class LydiaConfig(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    """
    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'settings_data/lydia_config.html'
    perm_codename = 'change_setting'
    lm_active = 'lm_global_config'
    form_class = LydiaConfigForm

    def get_initial(self, **kwargs):
        initial = super(LydiaConfig, self).get_initial(**kwargs)
        initial['lydia_min_price'] = settings_safe_get('LYDIA_MIN_PRICE').get_value()
        initial['lydia_max_price'] = settings_safe_get('LYDIA_MAX_PRICE').get_value()
        return initial

    def form_valid(self, form):
        # Lydia min price
        lydia_min_price = settings_safe_get('LYDIA_MIN_PRICE')
        if not form.cleaned_data['lydia_min_price']:
            lydia_min_price.value = ''
        else:
            lydia_min_price.value = form.cleaned_data['lydia_min_price']
        lydia_min_price.save()
        # Lydia max price
        lydia_max_price = settings_safe_get('LYDIA_MAX_PRICE')
        if not form.cleaned_data['lydia_max_price']:
            lydia_max_price.value = ''
        else:
            lydia_max_price.value = form.cleaned_data['lydia_max_price']
        lydia_max_price.save()
        return redirect(reverse('url_global_config',
                        kwargs={'group_name': self.group.name}))


class BalanceConfig(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    """
    Each config parameter MUST exists..
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'settings_data/balance_config.html'
    perm_codename = 'change_setting'
    lm_active = 'lm_global_config'
    form_class = BalanceConfigForm

    def get_initial(self, **kwargs):
        initial = super(BalanceConfig, self).get_initial(**kwargs)
        initial['balance_threshold_mail_alert'] = settings_safe_get('BALANCE_THRESHOLD_MAIL_ALERT').get_value()
        initial['balance_frequency_mail_alert'] = settings_safe_get('BALANCE_FREQUENCY_MAIL_ALERT').get_value()
        return initial

    def form_valid(self, form):
        # balance_threshold_mail_alert
        balance_threshold_mail_alert = settings_safe_get('BALANCE_THRESHOLD_MAIL_ALERT')
        if not form.cleaned_data['balance_threshold_mail_alert']:
            balance_threshold_mail_alert.value = ''
        else:
            balance_threshold_mail_alert.value = form.cleaned_data['balance_threshold_mail_alert']
        balance_threshold_mail_alert.save()
        # balance_frequency_mail_alert
        balance_frequency_mail_alert = settings_safe_get('BALANCE_FREQUENCY_MAIL_ALERT')
        if not form.cleaned_data['balance_frequency_mail_alert']:
            balance_frequency_mail_alert.value = ''
        else:
            balance_frequency_mail_alert.value = form.cleaned_data['balance_frequency_mail_alert']
        balance_frequency_mail_alert.save()
        return redirect(reverse('url_global_config',
                        kwargs={'group_name': self.group.name}))
