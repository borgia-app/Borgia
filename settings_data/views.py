from django.shortcuts import render
from django.views.generic.base import View
from settings_data.models import Setting
from django.forms.models import model_to_dict

from contrib.models import add_to_breadcrumbs
from borgia.models import FormNextView
from settings_data.form import *


class ListSettingView(View):
    template_name = 'settings_data/setting_list.html'
    attr = {
        'order_by': 'name',
    }

    def get(self, request, *args, **kwargs):
        if request.GET.get('order_by') is not None:
            self.attr['order_by'] = request.GET.get('order_by')
        context = {
            'query_setting': Setting.objects.all().order_by(self.attr['order_by']),
        }
        add_to_breadcrumbs(request, 'Liste paramètres système')
        return render(request, self.template_name, context)


class UpdateSettingView(FormNextView):
    form_class = UpdateSettingForm
    template_name = 'settings_data/setting_update.html'
    success_url = '/finances/bank_account/'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Modification paramètre système')
        return super(UpdateSettingView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        setting = Setting.objects.get(pk=self.kwargs['pk'])
        setting.value = form.cleaned_data['value']
        setting.save()
        return super(UpdateSettingView, self).form_valid(form)

    def get_initial(self):
        setting = Setting.objects.get(pk=self.kwargs['pk'])
        initial = super(UpdateSettingView, self).get_initial()
        for attr in model_to_dict(setting):
            if attr == 'value_type':
                initial[attr] = setting.get_value_type_display()
            else:
                initial[attr] = model_to_dict(setting)[attr]
        return initial
