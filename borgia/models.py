from django.views.generic.edit import FormView
from django.shortcuts import force_text


class FormNextView(FormView):
    def get_context_data(self, **kwargs):
        context = super(FormNextView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.request.POST.get('next', self.success_url))
        return context

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))

