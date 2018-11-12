from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.template import Context, Template
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.timezone import now
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from lxml import etree

from borgia.utils import (GroupLateralMenuFormMixin, GroupLateralMenuMixin,
                          GroupPermissionMixin)
from borgia.views import ListCompleteView
from notifications.forms import (NotificationTemplateCreateViewForm,
                                 NotificationTemplateUpdateViewForm, notiftest)
from notifications.models import (Notification, NotificationClass,
                                  NotificationGroup, NotificationTemplate,
                                  get_allowed_tags, notify,
                                  template_rendering_engine)


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
        self.query = Notification.objects.filter(
            target_user=self.request.user).order_by(self.attr['order_by'])
        notification_tab_header = []
        seen = set(notification_tab_header)

        for notification in self.query:
            if notification.read_datetime is None:
                notification.read_datetime = now()
                notification.save()

            if notification.group_category not in seen:
                seen.add(notification.group_category)
                notification_tab_header.append(notification.group_category)

        context = super(NotificationListCompleteView,
                        self).get_context_data(**kwargs)

        context['notification_tab_header'] = notification_tab_header

        return context


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
        self.query = NotificationTemplate.objects.all().order_by(
            self.attr['order_by'])
        # Call the base implementation first to get a context
        context = super(NotificationTemplateListCompleteView,
                        self).get_context_data(**kwargs)
        # Add in the html template
        for template_object in context['page']:
            template_object.html_template = Template(template_rendering_engine(template_object.xml_template)).\
                render(Context({
                    'group_name': self.kwargs['group_name'],
                    'actor': self.request.user}))
        return context


class NotificationTemplateCreateView(GroupPermissionMixin, CreateView, GroupLateralMenuFormMixin):
    """

    """
    model = NotificationTemplate
    template_name = 'notifications/notification_template_create.html'
    form_class = NotificationTemplateCreateViewForm
    perm_codename = 'add_notificationtemplate'

    def get_initial(self):
        if self.kwargs['notification_class'] is not None:
            return {'notification_class': NotificationClass.objects.get(name=self.kwargs['notification_class'])}

    # Here we will add allowed tags to context in order to display it and help users
    def get_context_data(self, **kwargs):
        # First, we get the usual context thanks to super
        context = super(NotificationTemplateCreateView,
                        self).get_context_data(**kwargs)
        # Next, we add variables used to render tags
        context['actor'] = self.request.user
        context['target_object'] = self.request.user

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
                        Template(html[0]+tag+html[1]).render(Context(context)))
            context['tag_dictionary'] = tag_dictionary
        except ObjectDoesNotExist:
            pass

        return context

    def form_valid(self, form):

        self.success_url = reverse(
            'url_notificationtemplate_list',
            kwargs={'group_name': self.group.name})

        # We notify
        notify(notification_class_name='notification_template_creation',
               actor=self.request.user)
        return super(NotificationTemplateCreateView, self).form_valid(form)


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
        context = super(NotificationTemplateUpdateView,
                        self).get_context_data(**kwargs)
        # Next, we add variables used to render tags
        context['actor'] = self.request.user
        context['target_object'] = self.request.user

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

    def form_valid(self, form):

        self.success_url = reverse(
            'url_notificationtemplate_change',
            kwargs={'group_name': self.group.name,
                    'pk': self.object.pk})

        # We notify
        notify(notification_class_name='notification_template_update',
               actor=self.request.user)

        return super(NotificationTemplateUpdateView, self).form_valid(form)


class NotificationTemplateDeactivateView(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    Deactivate a notification template and redirect to the notification template list.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    template_name = 'notifications/notification_template_deactivate.html'
    success_url = None
    perm_codename = 'deactivate_notificationtemplate'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['notification_template'] = NotificationTemplate.objects.get(pk=kwargs['pk'])
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        notification_template = NotificationTemplate.objects.get(
            pk=kwargs['pk'])
        if notification_template.is_activated is True:
            notification_template.is_activated = False
        else:
            notification_template.is_activated = True
        notification_template.save()

        self.success_url = reverse(
            'url_notificationtemplate_list',
            kwargs={'group_name': self.group.name})

        # We notify
        notify(notification_class_name='notification_template_deactivation',
               actor=self.request.user)

        return redirect(force_text(self.success_url))


class NotificationGroupListCompleteView(GroupPermissionMixin, ListView, GroupLateralMenuFormMixin):
    """

    """
    model = NotificationGroup
    template_name = 'notifications/notification_group_list_complete.html'
    success_url = None
    perm_codename = "list_notificationgroup"

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
    perm_codename = "add_notificationgroup"


class NotificationGroupUpdateView(GroupPermissionMixin, UpdateView, GroupLateralMenuFormMixin):
    """

    """
    model = NotificationGroup
    fields = ['weight']
    template_name = 'notifications/notification_group_update.html'
    success_url = None
    perm_codename = "change_notificationgroup"


def read_notification(request):

    try:
        int(request.GET.get('notification_id'))

        try:
            notification = Notification.objects.get(
                pk=request.GET.get('notification_id'))
        except Notification.DoesNotExist:
            raise Http404

        if notification.target_user == request.user:

            if notification.read_datetime is None:
                notification.read_datetime = now()
                notification.save()

            return HttpResponseRedirect(reverse('url_login'))

        else:
            raise PermissionDenied
    except ValueError:
        raise Http404
