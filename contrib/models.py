#-*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile, match
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in, user_logged_out


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


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).
    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    Note : ajout de LOGIN_EXEMPT_URL_PATTERNS qui contient des patterns de re plus complexes
    """
    def process_request(self, request):
        assert hasattr(request, 'user'), "The Login Required middleware\
 requires authentication middleware to be installed. Edit your\
 MIDDLEWARE_CLASSES setting to insert\
 'django.contrib.auth.middleware.AuthenticationMiddleware'. If that doesn't\
 work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
 'django.core.context_processors.auth'."
        if not request.user.is_authenticated():
            path = request.path_info
            if path not in settings.LOGIN_EXEMPT_URLS:
                denied = True
                for pattern in settings.LOGIN_EXEMPT_URL_PATTERNS:
                    if pattern.match(path) is not None:
                        denied = False
                        break
                if denied is True:
                    return HttpResponseRedirect(settings.LOGIN_URL)


def user_logged_in_handler(sender, request, user, **kwargs):
    """
    Initialisation du breadcrumbs à la connexion
    """
    request.session['breadcrumbs'] = []


def user_logged_out_handler(sender, request, user, **kwargs):
    """
     Effacement du breadcrumbs à la deconnexion, même si on garde la session
    """
    request.session['breadcrumbs'] = []


# Connection des signaux aux fonctions initialisation et suppression breadcrumbs
user_logged_in.connect(user_logged_in_handler)
user_logged_out.connect(user_logged_out_handler)


def add_to_breadcrumbs(request, label):
    """
    Ajoute un couple (label, url) au breadcrumb.

    Si on détecte que le label est déjà dans le breadcrumb, alors on ne l'ajoute pas et on se positionne sur cet url.
    On supprime alors les breadcrumbs qui sont après.
    Ex: Profil -> workboard X -> Profil devient Profil

    Dans le cas où on boucle sur un même url, le premier est sauvegardé, pas les autres.
    On garde de cette façon les paramètres GET utiles.
    Ex: listx?next=blabla est sauvegardé, même si on revient sur listx sans next

    La fonction ne garde que 5 breadcrumbs dans la liste
    """
    try:
        breadcrumbs = request.session['breadcrumbs'][:]

        # Si le lien est déjà dans le breadcrumbs, on ne l'ajoute pas mais on fait comme s'il était celui actif

        in_breadcrumbs = False

        for d in breadcrumbs:
            if d[0] == label:
                in_breadcrumbs = breadcrumbs.index(d)
                break

        if in_breadcrumbs is not False:
            breadcrumbs = breadcrumbs[0:in_breadcrumbs+1]
        else:
            breadcrumbs.append([label, request.get_full_path()])

        # Seulement 5 breadcrumbs
        # Effacement par le début
        while len(breadcrumbs) > 5:
            del breadcrumbs[0]

        request.session['breadcrumbs'] = breadcrumbs

    except KeyError:
        pass
    except IndexError:
        pass


class RedirectLoginProfile:
    """
    Redirection vers le profile si l'user va sur une page de login alors qu'il est déjà connecté
    """
    def process_request(self, request):
        login_pages = [
            '/auth/login',
            '/',
        ]
        if request.path_info in login_pages and request.user.is_authenticated():
            return HttpResponseRedirect('/shops/foyer/consumption')