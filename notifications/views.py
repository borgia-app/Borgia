#-*- coding: utf-8 -*-

from notifications.models import *
from contrib.models import add_to_breadcrumbs
from django.shortcuts import HttpResponseRedirect
from borgia.models import ListCompleteView
from notifications.forms import notiftest, NotificationTemplateUpdateViewForm
from django.views.generic.edit import UpdateView, CreateView
from borgia.utils import *
from django.template import Template

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

    def get(self, request, *args, **kwargs):
        # Ajout au fil d'ariane
        add_to_breadcrumbs(request, 'Notifications')
        return super(NotificationListCompleteView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        # Récupération de la liste de notifications filtrées de l'user
        self.query = Notification.objects.filter(target_user=self.request.user).order_by(self.attr['order_by'])
        for notification in self.query:
            if notification.read_date is None:
                notification.read_date = now()
                notification.save()
        return super(NotificationListCompleteView, self).get_context_data(**kwargs)

    # Définit la méthode de rendu du template qui sera accessible dans le template avec view
    def template_rendering_engine(self):
        for e in self.query:
            return Template(template_rendering_engine(NotificationTemplate.objects.get(
                pk=e.notification_template.pk).message)).\
                render(template.Context
                (
                    {
                        'recipient': e.action_medium_object,
                        'object': e.action_medium_object,
                        'actor': e.actor_object,
                        'group_name': self.kwargs['group_name'],
                    }
                )
                       )


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

    def get(self, request, *args, **kwargs):
        # Ajout au fil d'ariane
        add_to_breadcrumbs(request, 'Templates de notification')
        return super(NotificationTemplateListCompleteView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Récupération de la liste de templates de notifications
        self.query = NotificationTemplate.objects.all().order_by(self.attr['order_by'])
        return super(NotificationTemplateListCompleteView, self).get_context_data(**kwargs)

    # Définit la méthode de rendu du template qui sera accessible dans le template avec view
    def template_rendering_engine(self):
        for e in self.query:
            return template_rendering_engine(e.message)


class NotificationTemplateCreateView(GroupPermissionMixin, CreateView, GroupLateralMenuFormMixin):
    """

    """
    model = NotificationTemplate
    template_name = 'notifications/notification_template_create.html'
    success_url = '/notifications/templates/'
    fields = ['notification_class', 'target_users', 'required_permission', 'message', 'category', 'type', 'is_activated']
    perm_codename = 'add_notificationtemplate'

    def get(self, request, *args, **kwargs):
        # Ajout au fil d'ariane
        add_to_breadcrumbs(request, 'Création de template')
        return super(NotificationTemplateCreateView, self).get(request, *args, **kwargs)

    def get_initial(self):
        if self.request.GET.get('notification_class') is not None:
            return {'notification_class': NotificationClass.objects.get(name=self.request.GET.get('notification_class'))}


class NotificationTemplateUpdateView(GroupPermissionMixin, UpdateView, GroupLateralMenuFormMixin):
    """

    """
    model = NotificationTemplate
    form_class = NotificationTemplateUpdateViewForm
    template_name = 'notifications/notification_template_update.html'
    success_url = None
    perm_codename = 'change_notificationtemplate'

    def get(self, request, *args, **kwargs):
        # Ajout au fil d'ariane
        add_to_breadcrumbs(request, 'Modification de template')
        return super(NotificationTemplateUpdateView, self).get(request, *args, **kwargs)


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

