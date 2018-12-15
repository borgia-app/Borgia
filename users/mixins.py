from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic.base import ContextMixin

from borgia.mixins import LateralMenuManagersMixin
from users.models import User


class UserPermissionAndContextMixin(PermissionRequiredMixin, ContextMixin):
    """
    Permission and context mixin for user model.
    """
    def __init__(self):
        self.user = None

    def add_user_object(self):
        """
        Define shop object.
        Raise Http404 is shop doesn't exist.
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


class UserMixin(UserPermissionAndContextMixin, LateralMenuManagersMixin):
    """
    Mixin that check permission, give context for users and add MANAGERS lateral menu.
    """
