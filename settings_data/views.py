from django.utils.timezone import now
from django.shortcuts import render, redirect, Http404, reverse

from django.contrib.auth.models import Group
from django.views.generic import FormView, View
from django.core.exceptions import ObjectDoesNotExist

from settings_data.forms import PriceConfigForm, LydiaConfigForm
from settings_data.models import Setting
from borgia.utils import (GroupPermissionMixin, GroupLateralMenuFormMixin,
                          GroupLateralMenuMixin,
                          lateral_menu)


class GlobalConfig(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    View to manage config of the application.

    :param kwargs['group_name']: name of the group, mandatory
    :type kwargs['group_name']: string
    """
    template_name = 'settings_data/application_config.html'
    perm_codename = None
    lm_active = 'lm_global_config'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['price_form'] = PriceConfigForm()
        context['lydia_form'] = LydiaConfigForm()
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        # Price form
        price_form = PriceConfigForm(request.POST)
        if price_form.is_valid():
            print(True)
        else:
            print(price_form)
            context = self.get_context_data(**kwargs)
            context['price_form'] = PriceConfigForm(price_form)
            context['lydia_form'] = LydiaConfigForm(request.POST)
            render(request, self.template_name, context=context)
        # Lydia form
        lydia_form = LydiaConfigForm(request.POST)
        print(lydia_form.is_valid())

        return redirect(reverse(
            'url_global_config', kwargs={
            'group_name': self.kwargs['group_name']}))
