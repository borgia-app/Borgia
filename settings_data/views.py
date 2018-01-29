from django.shortcuts import render
from django.views.generic.base import View
from settings_data.models import Setting

from contrib.models import add_to_breadcrumbs
from borgia.views import FormNextView
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
        initial['value'] = setting.value
        return initial

    def get_form_kwargs(self):
        kwargs = super(UpdateSettingView, self).get_form_kwargs()
        kwargs['setting'] = Setting.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UpdateSettingView, self).get_context_data(**kwargs)
        context['setting'] = Setting.objects.get(pk=self.kwargs['pk'])
        return context
