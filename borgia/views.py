#-*- coding: utf-8 -*-
from django.views.generic import FormView
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm


class LoginPG(FormView):
    form_class = AuthenticationForm
    template_name = 'login_clean.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect('/shops/' + self.kwargs['organe'] + '/consumption/')

    def get_context_data(self, **kwargs):
        context = super(LoginPG, self).get_context_data(**kwargs)
        context['organe_name'] = self.kwargs['organe']
        return context
