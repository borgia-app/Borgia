from re import compile

from django.conf import settings
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import Resolver404, resolve
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import ugettext_lazy as _


class TimeStampedDescription(models.Model):
    """TimeStampedDescription
    Une classe de base abstraite qui fournit une gestion automatique des dates de creation
    et de derniere modification, ainsi qu'un titre, une description
    """
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        get_latest_by = 'modified'
        ordering = ('-modified', '-created',)
        abstract = True


EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).
    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    Note : ajout de LOGIN_EXEMPT_URL_PATTERNS qui contient des patterns de re
    plus complexes
    """

    def process_request(self, request):
        assert hasattr(request, 'user'), "The Login Required middleware\
 requires authentication middleware to be installed. Edit your\
 MIDDLEWARE_CLASSES setting to insert\
 'django.contrib.auth.middleware.AuthenticationMiddleware'. If that doesn't\
 work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
 'django.core.context_processors.auth'."
        if not request.user.is_authenticated:
            path = request.path_info
            if path not in settings.LOGIN_EXEMPT_URLS:
                denied = True
                for pattern in settings.LOGIN_EXEMPT_URL_PATTERNS:
                    if pattern.match(path) is not None:
                        denied = False
                        break
                if denied is True:
                    try:
                        match = resolve(request.path_info)
                        request.session['after_login'] = request.path_info
                    except Resolver404:
                        try:
                            del request.session['after_login']
                        except KeyError:
                            pass
                    return HttpResponseRedirect(settings.LOGIN_URL)


class SaveLoginUrlMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            if view_kwargs['save_login_url'] is True:
                request.session['save_login_url'] = request.path
            elif view_kwargs['save_login_url'] is False:
                del request.session['save_login_url']
        except KeyError:
            pass
