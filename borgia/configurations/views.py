from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.urls import reverse
from django.views.generic.base import TemplateView

from borgia.mixins import LateralMenuMixin
from borgia.views import BorgiaFormView
from configurations.forms import (ConfigurationBalanceForm,
                                  ConfigurationCenterForm,
                                  ConfigurationLydiaForm,
                                  ConfigurationProfitForm)
from configurations.utils import configuration_get


class ConfigurationIndexView(LoginRequiredMixin, PermissionRequiredMixin, LateralMenuMixin, TemplateView):
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
        context['center_name'] = configuration_get('CENTER_NAME')
        context['margin_profit'] = configuration_get('MARGIN_PROFIT')
        context['enable_self_lydia'] = configuration_get('ENABLE_SELF_LYDIA')
        context['min_price_lydia'] = configuration_get('MIN_PRICE_LYDIA')
        context['max_price_lydia'] = configuration_get('MAX_PRICE_LYDIA')
        context['api_token_lydia'] = configuration_get('API_TOKEN_LYDIA')
        context['vendor_token_lydia'] = configuration_get('VENDOR_TOKEN_LYDIA')
        context['enable_fee_lydia'] = configuration_get('ENABLE_FEE_LYDIA')
        context['base_fee_lydia'] = configuration_get('BASE_FEE_LYDIA')
        context['ratio_fee_lydia'] = configuration_get('RATIO_FEE_LYDIA')
        context['tax_fee_lydia'] = configuration_get('TAX_FEE_LYDIA')
        context['balance_threshold_purchase'] = configuration_get(
            "BALANCE_THRESHOLD_PURCHASE")
        #context['balance_threshold_mail_alert'] = configuration_get("BALANCE_THRESHOLD_MAIL_ALERT")
        #context['balance_frequency_mail_alert'] = configuration_get("BALANCE_FREQUENCY_MAIL_ALERT")
        return context


class ConfigurationChangeBaseView(LoginRequiredMixin, PermissionRequiredMixin, BorgiaFormView):
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

    def get_initial(self):
        initial = super().get_initial()
        initial['center_name'] = configuration_get('CENTER_NAME').get_value()
        return initial

    def form_valid(self, form):
        # Margin profit
        center_name = configuration_get('CENTER_NAME')
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

    def get_initial(self):
        initial = super().get_initial()
        initial['margin_profit'] = configuration_get(
            'MARGIN_PROFIT').get_value()
        return initial

    def form_valid(self, form):
        # Margin profit
        margin_profit = configuration_get('MARGIN_PROFIT')
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

    def get_initial(self):
        initial = super().get_initial()
        initial['enable_self_lydia'] = configuration_get(
            'ENABLE_SELF_LYDIA').get_value()
        initial['min_price_lydia'] = configuration_get(
            'MIN_PRICE_LYDIA').get_value()
        initial['max_price_lydia'] = configuration_get(
            'MAX_PRICE_LYDIA').get_value()
        initial['api_token_lydia'] = configuration_get(
            'API_TOKEN_LYDIA').get_value()
        initial['vendor_token_lydia'] = configuration_get(
            'VENDOR_TOKEN_LYDIA').get_value()
        initial['enable_fee_lydia'] = configuration_get(
            'ENABLE_FEE_LYDIA').get_value()
        initial['base_fee_lydia'] = configuration_get(
            'BASE_FEE_LYDIA').get_value()
        initial['ratio_fee_lydia'] = configuration_get(
            'RATIO_FEE_LYDIA').get_value()
        initial['tax_fee_lydia'] = configuration_get(
            'TAX_FEE_LYDIA').get_value()
        return initial

    def form_valid(self, form):
        # Enable
        enable_self_lydia = configuration_get('ENABLE_SELF_LYDIA')
        enable_self_lydia.value = form.cleaned_data['enable_self_lydia']
        enable_self_lydia.save()
        # Lydia min price
        min_price_lydia = configuration_get('MIN_PRICE_LYDIA')
        min_price_lydia.value = form.cleaned_data['min_price_lydia']
        min_price_lydia.save()
        # Lydia max price
        max_price_lydia = configuration_get('MAX_PRICE_LYDIA')
        if not form.cleaned_data['max_price_lydia']:
            max_price_lydia.value = ''
        else:
            max_price_lydia.value = form.cleaned_data['max_price_lydia']
        max_price_lydia.save()
        # Enable fee
        enable_fee_lydia = configuration_get('ENABLE_FEE_LYDIA')
        enable_fee_lydia.value = form.cleaned_data['enable_fee_lydia']
        enable_fee_lydia.save()
        # Base fee
        base_fee_lydia = configuration_get('BASE_FEE_LYDIA')
        if not form.cleaned_data['base_fee_lydia']:
            base_fee_lydia.value = ''
        else:
            base_fee_lydia.value = form.cleaned_data['base_fee_lydia']
        base_fee_lydia.save()
        # Ratio fee
        ratio_fee_lydia = configuration_get('RATIO_FEE_LYDIA')
        if not form.cleaned_data['ratio_fee_lydia']:
            ratio_fee_lydia.value = ''
        else:
            ratio_fee_lydia.value = form.cleaned_data['ratio_fee_lydia']
        ratio_fee_lydia.save()
        # Tax fee
        tax_fee_lydia = configuration_get('TAX_FEE_LYDIA')
        if not form.cleaned_data['tax_fee_lydia']:
            tax_fee_lydia.value = ''
        else:
            tax_fee_lydia.value = form.cleaned_data['tax_fee_lydia']
        tax_fee_lydia.save()
        # Lydia api token
        api_token_lydia = configuration_get('API_TOKEN_LYDIA')
        api_token_lydia.value = form.cleaned_data['api_token_lydia']
        api_token_lydia.save()
        # Lydia vendor token
        vendor_token_lydia = configuration_get('VENDOR_TOKEN_LYDIA')
        vendor_token_lydia.value = form.cleaned_data['vendor_token_lydia']
        vendor_token_lydia.save()
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

    def get_initial(self):
        initial = super().get_initial()
        initial['balance_threshold_purchase'] = configuration_get(
            'BALANCE_THRESHOLD_PURCHASE').get_value()
        #initial['balance_threshold_mail_alert'] = configuration_get('BALANCE_THRESHOLD_MAIL_ALERT').get_value()
        #initial['balance_frequency_mail_alert'] = configuration_get('BALANCE_FREQUENCY_MAIL_ALERT').get_value()
        return initial

    def form_valid(self, form):
        # balance_threshold_purchase
        balance_threshold_purchase = configuration_get(
            'BALANCE_THRESHOLD_PURCHASE')
        balance_threshold_purchase.value = form.cleaned_data['balance_threshold_purchase']
        balance_threshold_purchase.save()

        # # balance_threshold_mail_alert
        # balance_threshold_mail_alert = configuration_get('BALANCE_THRESHOLD_MAIL_ALERT')
        # if not form.cleaned_data['balance_threshold_mail_alert']:
        #     balance_threshold_mail_alert.value = ''
        # else:
        #     balance_threshold_mail_alert.value = form.cleaned_data['balance_threshold_mail_alert']
        # balance_threshold_mail_alert.save()
        # # balance_frequency_mail_alert
        # balance_frequency_mail_alert = configuration_get('BALANCE_FREQUENCY_MAIL_ALERT')
        # if not form.cleaned_data['balance_frequency_mail_alert']:
        #     balance_frequency_mail_alert.value = ''
        # else:
        #     balance_frequency_mail_alert.value = form.cleaned_data['balance_frequency_mail_alert']
        # balance_frequency_mail_alert.save()

        return super().form_valid(form)
