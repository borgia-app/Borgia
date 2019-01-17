from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic.base import ContextMixin

from events.models import Event


class EventMixin(LoginRequiredMixin, PermissionRequiredMixin, ContextMixin):
    """
    Mixin for Event views.
    For Permission :
    This mixin check if the user has the permission required OR
    if allow_manager is true and the user is the manager of the event.
    Then, it check if the event exists.
    Then, if it is not already done.

    Also, add to context the event itself.
    """
    permission_required = None
    allow_manager = False
    need_ongoing_event = False

    def __init__(self):
        self.event = None

    def has_permission(self):
        """
        Check if event exists, then permission.
        Then check potentially on-going / manager attributes
        """
        try:
            self.event = Event.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        has_perms = super().has_permission()
        if has_perms or self.allow_manager and self.request.user == self.event.manager:
            if self.need_ongoing_event:
                return not self.event.done
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context
