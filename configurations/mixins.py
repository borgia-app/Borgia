from django.contrib.auth.mixins import PermissionRequiredMixin
from borgia.mixins import LateralMenuManagersMixin


class ConfigurationMixin(PermissionRequiredMixin, LateralMenuManagersMixin):
    """
    Mixin that check permission and add MANAGERS lateral menu.
    """
