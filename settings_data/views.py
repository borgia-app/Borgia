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

        margin_profit, created = Setting.objects.get_or_create(
            name=settings.MARGIN_PROFIT_NAME,
            description=settings.MARGIN_PROFIT_DESCRIPTION,
            value_type=settings.MARGIN_PROFIT_VALUE_TYPE
        )
        if created:
            margin_profit.value = settings.MARGIN_PROFIT_VALUE
            margin_profit.save()
        context['margin_profit'] = margin_profit

        lydia_min_price, created = Setting.objects.get_or_create(
            name=settings.LYDIA_MIN_PRICE_NAME,
            description=settings.LYDIA_MIN_PRICE_DESCRIPTION,
            value_type=settings.LYDIA_MIN_PRICE_VALUE_TYPE
        )
        if created:
            lydia_min_price.value = settings.LYDIA_MIN_PRICE_VALUE
            lydia_min_price.save()
        context['lydia_min_price'] = lydia_min_price

        lydia_max_price, created = Setting.objects.get_or_create(
            name=settings.LYDIA_MAX_PRICE_NAME,
            description=settings.LYDIA_MAX_PRICE_DESCRIPTION,
            value_type=settings.LYDIA_MAX_PRICE_VALUE_TYPE
        )
        if created:
            lydia_max_price = settings.LYDIA_MAX_PRICE_VALUE
            lydia_max_price.save()
        context['lydia_max_price'] = lydia_max_price

        balance_threshold_mail_alert, created = Setting.objects.get_or_create(
            name=settings.BALANCE_THRESHOLD_MAIL_ALERT_NAME,
            description=settings.BALANCE_THRESHOLD_MAIL_ALERT_DESCRIPTION,
            value_type=settings.BALANCE_THRESHOLD_MAIL_ALERT_VALUE_TYPE
        )
        if created:
            balance_threshold_mail_alert.value = settings.BALANCE_THRESHOLD_MAIL_ALERT_VALUE
            balance_threshold_mail_alert.save()
        context['balance_threshold_mail_alert'] = balance_threshold_mail_alert

        balance_frequency_mail_alert, created = Setting.objects.get_or_create(
            name=settings.BALANCE_FREQUENCY_MAIL_ALERT_NAME,
            description=settings.BALANCE_FREQUENCY_MAIL_ALERT_DESCRIPTION,
            value_type=settings.BALANCE_FREQUENCY_MAIL_ALERT_VALUE_TYPE
        )
        if created:
            balance_frequency_mail_alert.value = settings.BALANCE_FREQUENCY_MAIL_ALERT_VALUE
            balance_frequency_mail_alert.save()
        context['balance_frequency_mail_alert'] = balance_frequency_mail_alert

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

        margin_profit, created = Setting.objects.get_or_create(
            name=settings.MARGIN_PROFIT_NAME,
            description=settings.MARGIN_PROFIT_DESCRIPTION,
            value_type=settings.MARGIN_PROFIT_VALUE_TYPE
        )
        if created:
            margin_profit.value = settings.MARGIN_PROFIT_VALUE
            margin_profit.save()

        initial['margin_profit'] = margin_profit.get_value()
        return initial

    def form_valid(self, form):
        # Margin profit
        margin_profit = Setting.objects.get(name="MARGIN_PROFIT")
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

        lydia_min_price, created = Setting.objects.get_or_create(
            name=settings.LYDIA_MIN_PRICE_NAME,
            description=settings.LYDIA_MIN_PRICE_DESCRIPTION,
            value_type=settings.LYDIA_MIN_PRICE_VALUE_TYPE
        )
        if created:
            lydia_min_price.value = settings.LYDIA_MIN_PRICE_VALUE
            lydia_min_price.save()
        initial['lydia_min_price'] = lydia_min_price.get_value()

        lydia_max_price, created = Setting.objects.get_or_create(
            name=settings.LYDIA_MAX_PRICE_NAME,
            description=settings.LYDIA_MAX_PRICE_DESCRIPTION,
            value_type=settings.LYDIA_MAX_PRICE_VALUE_TYPE
        )
        if created:
            lydia_max_price = settings.LYDIA_MAX_PRICE_VALUE
            lydia_max_price.save()
        initial['lydia_max_price'] = lydia_max_price.get_value()
        return initial

    def form_valid(self, form):
        # Lydia min price
        lydia_min_price = Setting.objects.get(name="LYDIA_MIN_PRICE")
        if not form.cleaned_data['lydia_min_price']:
            lydia_min_price.value = ''
        else:
            lydia_min_price.value = form.cleaned_data['lydia_min_price']
        lydia_min_price.save()
        # Lydia max price
        lydia_max_price = Setting.objects.get(name="LYDIA_MAX_PRICE")
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

        balance_threshold_mail_alert, created = Setting.objects.get_or_create(
            name=settings.BALANCE_THRESHOLD_MAIL_ALERT_NAME,
            description=settings.BALANCE_THRESHOLD_MAIL_ALERT_DESCRIPTION,
            value_type=settings.BALANCE_THRESHOLD_MAIL_ALERT_VALUE_TYPE
        )
        if created:
            balance_threshold_mail_alert.value = settings.BALANCE_THRESHOLD_MAIL_ALERT_VALUE
            balance_threshold_mail_alert.save()
        initial['balance_threshold_mail_alert'] = balance_threshold_mail_alert.get_value()

        balance_frequency_mail_alert, created = Setting.objects.get_or_create(
            name=settings.BALANCE_FREQUENCY_MAIL_ALERT_NAME,
            description=settings.BALANCE_FREQUENCY_MAIL_ALERT_DESCRIPTION,
            value_type=settings.BALANCE_FREQUENCY_MAIL_ALERT_VALUE_TYPE
        )
        if created:
            balance_frequency_mail_alert.value = settings.BALANCE_FREQUENCY_MAIL_ALERT_VALUE
            balance_frequency_mail_alert.save()
        initial['balance_frequency_mail_alert'] = balance_frequency_mail_alert.get_value()
        return initial

    def form_valid(self, form):
        # balance_threshold_mail_alert
        balance_threshold_mail_alert = Setting.objects.get(name="BALANCE_THRESHOLD_MAIL_ALERT")
        if not form.cleaned_data['balance_threshold_mail_alert']:
            balance_threshold_mail_alert.value = ''
        else:
            balance_threshold_mail_alert.value = form.cleaned_data['balance_threshold_mail_alert']
        balance_threshold_mail_alert.save()
        # balance_frequency_mail_alert
        balance_frequency_mail_alert = Setting.objects.get(name="BALANCE_FREQUENCY_MAIL_ALERT")
        if not form.cleaned_data['balance_frequency_mail_alert']:
            balance_frequency_mail_alert.value = ''
        else:
            balance_frequency_mail_alert.value = form.cleaned_data['balance_frequency_mail_alert']
        balance_frequency_mail_alert.save()
        return redirect(reverse('url_global_config',
                        kwargs={'group_name': self.group.name}))
