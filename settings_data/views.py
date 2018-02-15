from django.utils.timezone import now
from django.shortcuts import render, redirect, Http404, reverse

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

    Each config parameter MUST exists and are created by a fixture.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create.

    margin_profit default value: 5%
    lydia_min_price default value: 5€
    lydia_max_price default value: 500€
    balance_threshold_mail_alert default value: -10€
    balance_frequency_mail_alert default value: 7 days

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    """
    template_name = 'settings_data/global_config.html'
    perm_codename = 'change_setting'
    lm_active = 'lm_global_config'

    def get_context_data(self, **kwargs):
        context = super(GlobalConfig, self).get_context_data(**kwargs)

        margin_profit, created = Setting.objects.get_or_create(
            name="MARGIN_PROFIT",
            description="Marge (%) à appliquer sur le prix des produits calculés automatiquement",
            value_type="f"
        )
        if created:
            margin_profit.value = "5"
            margin_profit.save()
        context['margin_profit'] = margin_profit

        lydia_min_price, created = Setting.objects.get_or_create(
            name="LYDIA_MIN_PRICE",
            description="Valeur minimale (€) de rechargement en automatique par Lydia",
            value_type="f"
        )
        if created:
            lydia_min_price.value = "5"
            lydia_min_price.save()
        context['lydia_min_price'] = lydia_min_price

        lydia_max_price, created = Setting.objects.get_or_create(
            name="LYDIA_MAX_PRICE",
            description="Valeur maximale (€) de rechargement en automatique par Lydia",
            value_type="f"
        )
        if created:
            lydia_max_price = "500"
            lydia_max_price.save()
        context['lydia_max_price'] = lydia_max_price

        balance_threshold_mail_alert, created = Setting.objects.get_or_create(
            name="BALANCE_THRESHOLD_MAIL_ALERT",
            description="Valeur seuil (€) en dessous de laquelle (strictement) l'alerte par email est activée",
            value_type="f"
        )
        if created:
            balance_threshold_mail_alert.value = "-10"
            balance_threshold_mail_alert.save()
        context['balance_threshold_mail_alert'] = balance_threshold_mail_alert

        balance_frequency_mail_alert, created = Setting.objects.get_or_create(
            name="BALANCE_FREQUENCY_MAIL_ALERT",
            description="Fréquence (jours) à laquelle l'alerte mail est envoyée si le solde est inférieur à la valeur seuil",
            value_type="i"
        )
        if created:
            balance_frequency_mail_alert.value = "7"
            balance_frequency_mail_alert.save()
        context['balance_frequency_mail_alert'] = balance_frequency_mail_alert

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)


class PriceConfig(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    """
    Each config parameter MUST exists and are created by a fixture.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create.

    margin_profit default value: 5%
    """
    template_name = 'settings_data/price_config.html'
    perm_codename = 'change_setting'
    lm_active = 'lm_global_config'
    form_class = PriceConfigForm

    def get_initial(self, **kwargs):
        initial = super(PriceConfig, self).get_initial(**kwargs)

        margin_profit, created = Setting.objects.get_or_create(
            name="MARGIN_PROFIT",
            description="Marge (%) à appliquer sur le prix des produits calculés automatiquement",
            value_type="f"
        )
        if created:
            margin_profit.value = "5"
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
    Each config parameter MUST exists and are created by a fixture.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create.

    lydia_min_price default value: 5€
    lydia_max_price default value: 500€
    """
    template_name = 'settings_data/lydia_config.html'
    perm_codename = 'change_setting'
    lm_active = 'lm_global_config'
    form_class = LydiaConfigForm

    def get_initial(self, **kwargs):
        initial = super(LydiaConfig, self).get_initial(**kwargs)

        lydia_min_price, created = Setting.objects.get_or_create(
            name="LYDIA_MIN_PRICE",
            description="Valeur minimale (€) de rechargement en automatique par Lydia",
            value_type="f"
        )
        if created:
            lydia_min_price.value = "5"
            lydia_min_price.save()
        initial['lydia_min_price'] = lydia_min_price.get_value()

        lydia_max_price, created = Setting.objects.get_or_create(
            name="LYDIA_MAX_PRICE",
            description="Valeur maximale (€) de rechargement en automatique par Lydia",
            value_type="f"
        )
        if created:
            lydia_max_price = "500"
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
    Each config parameter MUST exists and are created by a fixture.
    However, to ensure that these values still exists, they are recreated if
    necessary in get_initial with a get_or_create.

    balance_threshold_mail_alert default value: -10€
    balance_frequency_mail_alert default value: 7 days
    """
    template_name = 'settings_data/balance_config.html'
    perm_codename = 'change_setting'
    lm_active = 'lm_global_config'
    form_class = BalanceConfigForm

    def get_initial(self, **kwargs):
        initial = super(BalanceConfig, self).get_initial(**kwargs)

        balance_threshold_mail_alert, created = Setting.objects.get_or_create(
            name="BALANCE_THRESHOLD_MAIL_ALERT",
            description="Valeur seuil (€) en dessous de laquelle (strictement) l'alerte par email est activée",
            value_type="f"
        )
        if created:
            balance_threshold_mail_alert.value = "-10"
            balance_threshold_mail_alert.save()
        initial['balance_threshold_mail_alert'] = balance_threshold_mail_alert.get_value()

        balance_frequency_mail_alert, created = Setting.objects.get_or_create(
            name="BALANCE_FREQUENCY_MAIL_ALERT",
            description="Fréquence (jours) à laquelle l'alerte mail est envoyée si le solde est inférieur à la valeur seuil",
            value_type="i"
        )
        if created:
            balance_frequency_mail_alert.value = "7"
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


# TODO: min < max, check for '' value in views, ensure min, max, values are respected in views
