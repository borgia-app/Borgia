from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic.base import ContextMixin

from users.models import User


class UserMixin(LoginRequiredMixin, PermissionRequiredMixin, ContextMixin):
    """
    Permission and context mixin for user model.
    """
    def __init__(self):
        self.user = None

    def add_user_object(self):
        """
        Define user object.
        Raise Http404 is user doesn't exist.
        """
        try:
            self.user = User.objects.get(pk=self.kwargs['user_pk'])
        except ObjectDoesNotExist:
            raise Http404
        self.user.forecast_balance()
        
    def add_context_objects(self):
        """
        Override to add more context objects for the view.
        """
        self.add_user_object()

    def has_permission(self):
        self.add_context_objects()
        return super().has_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        return context


class GroupMixin(LoginRequiredMixin, PermissionRequiredMixin, ContextMixin):
    """
    Permission and context mixin for group model.
    """
    def __init__(self):
        self.group = None
        self.group

    def add_group_object(self):
        """
        Define group object.
        Raise Http404 is group doesn't exist.
        """
        try:
            self.group = Group.objects.get(pk=self.kwargs['group_pk'])
        except ObjectDoesNotExist:
            raise Http404
        
    def add_context_objects(self):
        """
        Override to add more context objects for the view.
        """
        self.add_group_object()

    def has_permission(self):
        self.add_context_objects()
        return super().has_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context