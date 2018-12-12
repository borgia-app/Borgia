from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.edit import FormView

from borgia.utils import GroupLateralMenuMixin, GroupPermissionMixin
from configurations.forms import (ConfigurationBalanceForm, ConfigurationCenterForm,
                                 ConfigurationLydiaForm, ConfigurationProfitForm)
from configurations.utils import configurations_safe_get


class ConfigurationListView(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    View to manage config of the application.

    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    """
    template_name = 'configurations/global_config.html'
    perm_codename = 'view_configuration'
    lm_active = 'lm_global_config'

    def get_context_data(self, **kwargs):
        context = super(ConfigurationListView, self).get_context_data(**kwargs)
        context['center_name'] = configurations_safe_get('CENTER_NAME')
        context['margin_profit'] = configurations_safe_get('MARGIN_PROFIT')
        context['lydia_min_price'] = configurations_safe_get('LYDIA_MIN_PRICE')
        context['lydia_max_price'] = configurations_safe_get("LYDIA_MAX_PRICE")
        context['lydia_api_token'] = configurations_safe_get("LYDIA_API_TOKEN")
        context['lydia_vendor_token'] = configurations_safe_get("LYDIA_VENDOR_TOKEN")
        context['balance_threshold_purchase'] = configurations_safe_get(
            "BALANCE_THRESHOLD_PURCHASE")
        #context['balance_threshold_mail_alert'] = configurations_safe_get("BALANCE_THRESHOLD_MAIL_ALERT")
        #context['balance_frequency_mail_alert'] = configurations_safe_get("BALANCE_FREQUENCY_MAIL_ALERT")
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)


class ConfigurationCenterView(GroupPermissionMixin, FormView, GroupLateralMenuMixin):
    """
    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'configurations/center_config.html'
    perm_codename = 'change_configuration'
    lm_active = 'lm_global_config'
    form_class = ConfigurationCenterForm

    def get_initial(self, **kwargs):
        initial = super(ConfigurationCenterView, self).get_initial(**kwargs)
        initial['center_name'] = configurations_safe_get('CENTER_NAME').get_value()
        return initial

    def form_valid(self, form):
        # Margin profit
        center_name = configurations_safe_get('CENTER_NAME')
        center_name.value = form.cleaned_data['center_name']
        center_name.save()
        return redirect(reverse('url_global_config',
                                kwargs={'group_name': self.group.name}))


class ConfigurationProfitView(GroupPermissionMixin, FormView, GroupLateralMenuMixin):
    """
    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'configurations/price_config.html'
    perm_codename = 'change_configuration'
    lm_active = 'lm_global_config'
    form_class = ConfigurationProfitForm

    def get_initial(self, **kwargs):
        initial = super(ConfigurationProfitView, self).get_initial(**kwargs)
        initial['margin_profit'] = configurations_safe_get(
            'MARGIN_PROFIT').get_value()
        return initial

    def form_valid(self, form):
        # Margin profit
        margin_profit = configurations_safe_get('MARGIN_PROFIT')
        margin_profit.value = form.cleaned_data['margin_profit']
        margin_profit.save()
        return redirect(reverse('url_global_config',
                                kwargs={'group_name': self.group.name}))


class ConfigurationLydiaView(GroupPermissionMixin, FormView, GroupLateralMenuMixin):
    """
    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'configurations/lydia_config.html'
    perm_codename = 'change_configuration'
    lm_active = 'lm_global_config'
    form_class = ConfigurationLydiaForm

    def get_initial(self, **kwargs):
        initial = super(ConfigurationLydiaView, self).get_initial(**kwargs)
        initial['lydia_min_price'] = configurations_safe_get(
            'LYDIA_MIN_PRICE').get_value()
        initial['lydia_max_price'] = configurations_safe_get(
            'LYDIA_MAX_PRICE').get_value()
        initial['lydia_api_token'] = configurations_safe_get(
            'LYDIA_API_TOKEN').get_value()
        initial['lydia_vendor_token'] = configurations_safe_get(
            'LYDIA_VENDOR_TOKEN').get_value()
        return initial

    def form_valid(self, form):
        # Lydia min price
        lydia_min_price = configurations_safe_get('LYDIA_MIN_PRICE')
        if not form.cleaned_data['lydia_min_price']:
            lydia_min_price.value = ''
        else:
            lydia_min_price.value = form.cleaned_data['lydia_min_price']
        lydia_min_price.save()
        # Lydia max price
        lydia_max_price = configurations_safe_get('LYDIA_MAX_PRICE')
        if not form.cleaned_data['lydia_max_price']:
            lydia_max_price.value = ''
        else:
            lydia_max_price.value = form.cleaned_data['lydia_max_price']
        lydia_max_price.save()
        # Lydia api token
        lydia_api_token = configurations_safe_get('LYDIA_API_TOKEN')
        lydia_api_token.value = form.cleaned_data['lydia_api_token']
        lydia_api_token.save()
        # Lydia vendor token
        lydia_vendor_token = configurations_safe_get('LYDIA_VENDOR_TOKEN')
        lydia_vendor_token.value = form.cleaned_data['lydia_vendor_token']
        lydia_vendor_token.save()
        return redirect(reverse('url_global_config',
                                kwargs={'group_name': self.group.name}))


class ConfigurationBalanceView(GroupPermissionMixin, FormView, GroupLateralMenuMixin):
    """
    Each config parameter MUST exists..
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'configurations/balance_config.html'
    perm_codename = 'change_configuration'
    lm_active = 'lm_global_config'
    form_class = ConfigurationBalanceForm

    def get_initial(self, **kwargs):
        initial = super(ConfigurationBalanceView, self).get_initial(**kwargs)
        initial['balance_threshold_purchase'] = configurations_safe_get(
            'BALANCE_THRESHOLD_PURCHASE').get_value()
        #initial['balance_threshold_mail_alert'] = configurations_safe_get('BALANCE_THRESHOLD_MAIL_ALERT').get_value()
        #initial['balance_frequency_mail_alert'] = configurations_safe_get('BALANCE_FREQUENCY_MAIL_ALERT').get_value()
        return initial

    def form_valid(self, form):
        # balance_threshold_purchase
        balance_threshold_purchase = configurations_safe_get(
            'BALANCE_THRESHOLD_PURCHASE')
        balance_threshold_purchase.value = form.cleaned_data['balance_threshold_purchase']
        balance_threshold_purchase.save()
        """
        # balance_threshold_mail_alert
        balance_threshold_mail_alert = configurations_safe_get('BALANCE_THRESHOLD_MAIL_ALERT')
        if not form.cleaned_data['balance_threshold_mail_alert']:
            balance_threshold_mail_alert.value = ''
        else:
            balance_threshold_mail_alert.value = form.cleaned_data['balance_threshold_mail_alert']
        balance_threshold_mail_alert.save()
        # balance_frequency_mail_alert
        balance_frequency_mail_alert = configurations_safe_get('BALANCE_FREQUENCY_MAIL_ALERT')
        if not form.cleaned_data['balance_frequency_mail_alert']:
            balance_frequency_mail_alert.value = ''
        else:
            balance_frequency_mail_alert.value = form.cleaned_data['balance_frequency_mail_alert']
        balance_frequency_mail_alert.save()
        """
        return redirect(reverse('url_global_config',
                                kwargs={'group_name': self.group.name}))
