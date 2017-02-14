#-*- coding: utf-8 -*-
from django import forms
from borgia.validators import *
from notifications.models import NotificationTemplate, NotificationClass, NotificationGroup
from django.contrib.auth.models import Group
from shops.models import Shop
import re


class notiftest(forms.Form):
    recipient = forms.CharField(label='Receveur', max_length=255,
                                widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                                validators=[autocomplete_username_validator])

    amount = forms.DecimalField(label='Montant (€)', decimal_places=2, max_digits=9, min_value=0)


class NotificationTemplateCreateViewForm(forms.ModelForm):
    class Meta:
        model = NotificationTemplate
        fields = ['notification_class', 'target_users', 'target_groups', 'message', 'category',
                  'type', 'is_activated']

    def __init__(self, *args, **kwargs):
        super(NotificationTemplateCreateViewForm, self).__init__(*args, **kwargs)

        # Some fields are improved with a search tools and a better display (thanks to bootstrap)
        self.fields['notification_class'] = forms.ModelChoiceField(
            queryset=NotificationClass.objects.all(),
            widget=forms.Select(
                attrs={'class': 'selectpicker', 'data-live-search': 'True'}),
            required=True)
        self.fields['target_groups'] = forms.ModelMultipleChoiceField(
            queryset=NotificationGroup.objects.all().exclude(
                notificationgroup=Group.objects.get(name='specials')),
            widget=forms.SelectMultiple(
                attrs={'class': 'selectpicker', 'data-live-search': 'True'}),
            required=False)
        self.fields['category'] = forms.ModelChoiceField(
            queryset=Shop.objects.all(),
            widget=forms.Select(
                attrs={'class': 'selectpicker', 'data-live-search': 'True'}),
            required=True)

    def clean(self):
        super(NotificationTemplateCreateViewForm, self).clean()

        if self.cleaned_data.get("target_users") != "TARGET_GROUPS":
            if self.cleaned_data.get("target_groups"):
                raise forms.ValidationError(
                    "Target_groups should be None when the target_users key is not TARGET_GROUPS")
        else:
            if not self.cleaned_data.get("target_groups"):
                raise forms.ValidationError(
                    "Target_groups should not be None when the target_users key is TARGET_GROUPS")


class NotificationTemplateUpdateViewForm(forms.ModelForm):
    class Meta:
        model = NotificationTemplate
        fields = ['notification_class', 'target_users', 'target_groups', 'message', 'category',
                  'type', 'is_activated']

    def __init__(self, *args, **kwargs):
        super(NotificationTemplateUpdateViewForm, self).__init__(*args, **kwargs)

        # Some fields are improved with a search tools and a better display (thanks to bootstrap)
        self.fields['notification_class'] = forms.ModelChoiceField(
            queryset=NotificationClass.objects.all(),
            widget=forms.Select(
                attrs={'class': 'selectpicker', 'data-live-search': 'True'}),
            required=True)
        self.fields['target_groups'] = forms.ModelMultipleChoiceField(
            queryset=NotificationGroup.objects.all().exclude(
                notificationgroup=Group.objects.get(name='specials')),
            widget=forms.SelectMultiple(
                attrs={'class': 'selectpicker', 'data-live-search': 'True'}),
            required=False)
        self.fields['category'] = forms.ModelChoiceField(
            queryset=Shop.objects.all(),
            widget=forms.Select(
                attrs={'class': 'selectpicker', 'data-live-search': 'True'}),
            required=True)

    def clean(self):
        super(NotificationTemplateUpdateViewForm, self).clean()

        if self.cleaned_data.get("target_users") != "TARGET_GROUPS":
            if self.cleaned_data.get("target_groups"):
                raise forms.ValidationError(
                    "Target_groups should be None when the target_users key is not TARGET_GROUPS")
        else:
            if not self.cleaned_data.get("target_groups"):
                raise forms.ValidationError(
                    "Target_groups should not be None when the target_users key is TARGET_GROUPS")




