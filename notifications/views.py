#-*- coding: utf-8 -*-

from notifications.models import *
from django.shortcuts import HttpResponseRedirect
from borgia.models import ListCompleteView
from notifications.forms import notiftest, NotificationTemplateUpdateViewForm, NotificationTemplateCreateViewForm
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView
from borgia.utils import *
from django.template import Template, Context
from lxml import etree

# CRUD modèle notification

# List


class NotificationListCompleteView(GroupPermissionMixin, ListCompleteView, GroupLateralMenuMixin):
    """

    """
    form_class = notiftest
    template_name = 'notifications/notification_list_complete.html'
    success_url = '/auth/login'
    attr = {
        'order_by': '-creation_datetime',
        }
    perm_codename = 'list_notification'

    def get_context_data(self, **kwargs):

        # Récupération de la liste de notifications filtrées de l'user
        self.query = Notification.objects.filter(target_user=self.request.user).order_by(self.attr['order_by'])
        for notification in self.query:
            if notification.read_date is None:
                notification.read_date = now()
                notification.save()

        return super(NotificationListCompleteView, self).get_context_data(**kwargs)


class NotificationTemplateListCompleteView(GroupPermissionMixin, ListCompleteView, GroupLateralMenuMixin):
    """

    """
    form_class = notiftest
    template_name = 'notifications/notification_template_list_complete.html'
    success_url = '/auth/login'
    attr = {
        'order_by': '-creation_datetime',
    }
    perm_codename = 'list_notificationtemplate'

    def get_context_data(self, **kwargs):
        # Récupération de la liste de templates de notifications
        self.query = NotificationTemplate.objects.all().order_by(self.attr['order_by'])
        # Call the base implementation first to get a context
        context = super(NotificationTemplateListCompleteView, self).get_context_data(**kwargs)
        # Add in the html template
        for template_object in context['page']:
            template_object.html_template = Template(template_rendering_engine(template_object.message)).\
                render(template.Context({
                    'group_name': self.kwargs['group_name'],
                    'actor': self.request.user}))
        return context


class NotificationTemplateCreateView(GroupPermissionMixin, CreateView, GroupLateralMenuFormMixin):
    """

    """
    model = NotificationTemplate
    template_name = 'notifications/notification_template_create.html'
    success_url = '/notifications/templates/'
    form_class = NotificationTemplateCreateViewForm
    perm_codename = 'add_notificationtemplate'

    def get_initial(self):
        if self.request.GET.get('notification_class') is not None:
            return {'notification_class': NotificationClass.objects.get(name=self.request.GET.get('notification_class'))}

    # Here we will add allowed tags to context in order to display it and help users
    def get_context_data(self, **kwargs):
        # First, we get the usual context thanks to super
        context = super(NotificationTemplateCreateView, self).get_context_data(**kwargs)
        # Next, we add variables used to render tags
        context['actor'] = self.request.user

        # Finally, we add allowed tags
        try:
            tag_dictionary = dict()
            allowed_tags = get_allowed_tags()
            del (allowed_tags['#text'], allowed_tags['bcode'])
            for tag, html in allowed_tags.items():
                # if html[1] = "", it means the tag is alone, like <actor/r
                if html[1] == "":
                    tag_dictionary[etree.tostring(etree.Element(tag))] = str(Template(html[0]).render(Context(context)))
                else:
                    xml_element = etree.Element(tag)
                    xml_element.text = tag
                    tag_dictionary[etree.tostring(xml_element)] = str(Template(html[0]+tag+html[1]).render(Context(context)))
            context['tag_dictionary'] = tag_dictionary
        except ObjectDoesNotExist:
            pass

        return context

    def form_valid(self, form):
        response = super(NotificationTemplateCreateView, self).form_valid(form)
        notify(self.request, 'template_creation')
        return response


class NotificationTemplateUpdateView(GroupPermissionMixin, UpdateView, GroupLateralMenuFormMixin):
    """

    """
    model = NotificationTemplate
    form_class = NotificationTemplateUpdateViewForm
    template_name = 'notifications/notification_template_update.html'
    success_url = None
    perm_codename = 'change_notificationtemplate'

    # Here we will add allowed tags to context in order to display it and help users
    def get_context_data(self, **kwargs):
        # First, we get the usual context thanks to super
        context = super(NotificationTemplateUpdateView, self).get_context_data(**kwargs)
        # Next, we add variables used to render tags
        context['actor'] = self.request.user

        # Finally, we add allowed tags
        try:
            tag_dictionary = dict()
            allowed_tags = get_allowed_tags()
            del (allowed_tags['#text'], allowed_tags['bcode'])
            for tag, html in allowed_tags.items():
                # if html[1] = "", it means the tag is alone, like <actor/r
                if html[1] == "":
                    tag_dictionary[etree.tostring(etree.Element(tag))] = str(
                        Template(html[0]).render(Context(context)))
                else:
                    xml_element = etree.Element(tag)
                    xml_element.text = tag
                    tag_dictionary[etree.tostring(xml_element)] = str(
                        Template(html[0] + tag + html[1]).render(Context(context)))
            context['tag_dictionary'] = tag_dictionary
        except ObjectDoesNotExist:
            pass

        return context


class NotificationGroupListCompleteView(GroupPermissionMixin, ListView, GroupLateralMenuFormMixin):
    """

    """
    model = NotificationGroup
    template_name = 'notifications/notification_group_list_complete.html'
    success_url = None
    perm_codename = None

    def get_queryset(self):
        for group in Group.objects.all().exclude(name='specials'):
            try:
                NotificationGroup.objects.get(notificationgroup=group)
            except ObjectDoesNotExist:
                NotificationGroup.objects.create(notificationgroup=group)
        return super(NotificationGroupListCompleteView, self).get_queryset()


class NotificationGroupCreateView(GroupPermissionMixin, CreateView, GroupLateralMenuFormMixin):
    """

    """
    model = NotificationGroup
    fields = ['notificationgroup', 'weight']
    template_name = 'notifications/notification_group_create.html'
    success_url = None
    perm_codename = None


class NotificationGroupUpdateView(GroupPermissionMixin, UpdateView, GroupLateralMenuFormMixin):
    """

    """
    model = NotificationGroup
    fields = ['weight']
    template_name = 'notifications/notification_group_update.html'
    success_url = None
    perm_codename = None


def read_notification(request):

    try:
        int(request.GET.get('notification_id'))

        try:
            notification = Notification.objects.get(pk=request.GET.get('notification_id'))
        except Notification.DoesNotExist:
            raise Http404

        if notification.target_user == request.user:

            if notification.read_date is None:
                notification.read_date = now()
                notification.save()

            return HttpResponseRedirect(reverse('url_login'))

        else:
            raise PermissionDenied
    except ValueError:
        raise Http404
