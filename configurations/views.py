from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from borgia.mixins import LateralMenuMixin
from borgia.views import BorgiaFormView
from configurations.forms import (ConfigurationBalanceForm,
                                  ConfigurationCenterForm,
                                  ConfigurationLydiaForm,
                                  ConfigurationProfitForm)
from configurations.utils import configurations_safe_get


class ConfigurationIndexView(PermissionRequiredMixin, LateralMenuMixin, TemplateView):
    """
    View to manage config of the application.

    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    permission_required = 'configurations.view_configuration'
    menu_type = 'managers'
    template_name = 'configurations/global_config.html'
    lm_active = 'lm_index_config'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


class ConfigurationChangeBaseView(PermissionRequiredMixin, BorgiaFormView):
    """
    Override this base view for configuration changes.
    """
    permission_required = 'configurations.change_configuration'
    menu_type = 'managers'

    def get_success_url(self):
        return reverse('url_index_config')


class ConfigurationCenterView(ConfigurationChangeBaseView):
    """
    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'configurations/center_config.html'
    form_class = ConfigurationCenterForm
    lm_active = 'lm_global_config'

    def get_initial(self, **kwargs):
        initial = super().get_initial(**kwargs)
        initial['center_name'] = configurations_safe_get('CENTER_NAME').get_value()
        return initial

    def form_valid(self, form):
        # Margin profit
        center_name = configurations_safe_get('CENTER_NAME')
        center_name.value = form.cleaned_data['center_name']
        center_name.save()
        return super().form_valid(form)


class ConfigurationProfitView(ConfigurationChangeBaseView):
    """
    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'configurations/price_config.html'
    form_class = ConfigurationProfitForm
    lm_active = 'lm_global_config'

    def get_initial(self, **kwargs):
        initial = super().get_initial(**kwargs)
        initial['margin_profit'] = configurations_safe_get(
            'MARGIN_PROFIT').get_value()
        return initial

    def form_valid(self, form):
        # Margin profit
        margin_profit = configurations_safe_get('MARGIN_PROFIT')
        margin_profit.value = form.cleaned_data['margin_profit']
        margin_profit.save()
        return super().form_valid(form)


class ConfigurationLydiaView(ConfigurationChangeBaseView):
    """
    Each config parameter MUST exists.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'configurations/lydia_config.html'
    form_class = ConfigurationLydiaForm
    lm_active = 'lm_global_config'

    def get_initial(self, **kwargs):
        initial = super().get_initial(**kwargs)
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
        return super().form_valid(form)


class ConfigurationBalanceView(ConfigurationChangeBaseView):
    """
    Each config parameter MUST exists..
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create. Default values are specified
    in borgia/settings.py.
    """
    template_name = 'configurations/balance_config.html'
    form_class = ConfigurationBalanceForm
    lm_active = 'lm_global_config'

    def get_initial(self, **kwargs):
        initial = super().get_initial(**kwargs)
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
        return super().form_valid(form)
