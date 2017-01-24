#-*- coding: utf-8 -*-
from django.views.generic import FormView, TemplateView, View
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.forms import BooleanField
from django.db.models import Q
from functools import reduce
from operator import or_
from django.core.serializers import serialize

from users.models import User
from django.contrib.auth.models import Group, Permission
import json
from django.core.exceptions import ObjectDoesNotExist
import operator

from borgia.utils import *
from finances.models import Sale
from borgia.forms import UserSearchForm
from users.views import UserListView


class LoginPG(FormView):
    form_class = AuthenticationForm
    template_name = 'login_clean.html'

    def get(self, request, *args, **kwargs):
        if request.user:
            logout(request)
        return super(LoginPG, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect('/shops/' + self.kwargs['organe'] + '/consumption/')

    def get_context_data(self, **kwargs):
        context = super(LoginPG, self).get_context_data(**kwargs)
        context['organe_name'] = self.kwargs['organe']
        return context


def jsi18n_catalog(request):
    """
    Render le js nécessaire à la jsi18n utilisé dans certains widgets venant de l'app admin
    Par exemple: FilteredSelectMultiple
    """
    return render(request, 'jsi18n.html')

def page_clean(request, template_name):
    return render(request, 'page_clean.html')

def get_list_model(request, model, search_in, props=None):
    """
    Permet de sérialiser en JSON les instances de modèle. Il est possible de donner des paramtères GET à cette fonction pour moduler
    la liste obtenue, plutôt que de faire un traitement en JS.
    Ne renvoie par les informations sensibles comme is_superuser ou password.

    :param model: Model dont on veut lister les instances
    :type model: héritée de models.Model
    :param search_in: paramètres dans lesquels le paramètre GET search sera recherché
    :type search_in: liste de chaînes de caractères
    :param props: méthodes du model à envoyer dans la sérialisation en supplément
    :type props: liste de chaînes de caractères de nom de méthodes de model
    :param request.GET : chaîne de caractère qui doit représenter une recherche filter dans un des champs de model
    :type request.GET : doit être dans les champs de model
    Les paramètres spéciaux sont order_by pour trier et search pour chercher dans search_in

    :return HttpResponse(data): liste des instances de model sérialisé en JSON, modulée par les parametres

    Exemple :
    model = User
    search_in = ['username', 'last_name', 'first_name']
    request.GET = { 'family': '101-99', 'order_by': 'year' }
    renverra la liste des users dont la famille est 101-99 en les triant par année
    """

    # Liste des filtres
    kwargs_filter = {}
    for param in request.GET:
        if param not in ['order_by', 'reverse', 'search'] :
            if param in [f.name for f in model._meta.get_fields()]:
                # Traitement spécifique pour les booléens envoyés en GET
                if request.GET[param] in ['True', 'true', 'False', 'false']:
                    if request.GET[param] in ['True', 'true']:
                        kwargs_filter[param] = True
                    else:
                        kwargs_filter[param] = False
                else:
                    kwargs_filter[param] = request.GET[param]
    query = model.objects.filter(**kwargs_filter)

    # Recherche si précisée
    try:
        args_search = reduce(lambda q, where: q | Q(**{where + '__startswith': request.GET['search']}), search_in, Q())
        query = query.filter(args_search).distinct()
    except KeyError:
        pass

    # Sérialisation
    if model is not User:

        data_serialise = serialize('json', query)

    else: # Cas User traité à part car contient des fields sensibles

        # Suppression des users spéciaux
        query = query.exclude(Q(groups=Group.objects.get(pk=9)) | Q(username='admin'))

        # Sérialisation
        allowed_fields = [f.name for f in User._meta.get_fields()]
        for e in ['password', 'is_superuser', 'is_staff', 'last_login']:
            allowed_fields.remove(e)

        data_serialise = serialize('json', query, fields=allowed_fields)

    data_load = json.loads(data_serialise)

    # Méthodes supplémentaires
    if props:
        for i, e in enumerate(data_load):
            props_dict = {}
            for p in props:
                try:
                    props_dict[p] = getattr(model.objects.get(pk=e['pk']), p)()
                except:
                    pass
            data_load[i]['props'] = props_dict

    # Trie si précisé
    try:
        if request.GET['reverse'] in ['True', 'true']:
            reverse = True
        else:
            reverse = False
        # Trie par la valeur d'un field
        if request.GET['order_by'] in [f.name for f in model._meta.get_fields()]:
            data_load = sorted(data_load, key=lambda obj: obj['fields'][request.GET['order_by']], reverse=reverse)
        # Trie par la valeur d'une méthode
        else:
            data_load = sorted(data_load,
                               key=lambda obj: getattr(model.objects.get(pk=obj['pk']), request.GET['order_by'])(),
                               reverse=reverse)
    except KeyError:
        pass

    # Information du nombre total d'élément
    count = len(data_load)

    # End et begin
    try:
        data_load = data_load[int(request.GET['begin']):int(request.GET['end'])]
    except KeyError or AttributeError:
        pass

    # Ajout de l'information du nombre total d'élément
    try:
        data_load[0]['count'] = count
    except IndexError:
        pass

    data = json.dumps(data_load)
    return HttpResponse(data)


def get_unique_model(request, pk, model, props=None):
    """
    Permet de sérialiser en JSON une instance spécifique pk=pk de model.
    Ne renvoie par les informations sensibles comme is_superuser ou password dans le cas d'un User.

    :param model: Model dont on veut lister les instances
    :type model: héritée de models.Model
    :param pk: pk de l'instance à retourner
    :type pk: integer > 0

    :return HttpResponse(data): l'instance de model sérialisé en JSON

    Exemple :
    model = User
    pk = 3
    renverra le json de l'user pk=3

    Remarque :
    serialise envoie une liste sérialisé, pour récupérer en js il ne faut pas faire data car c'est une liste, mais bien
    data[0]. Il n'y aura toujours que 1 élément dans cette liste car générée par un objects.get()
    """

    try:
        # On traite le cas particulier de User à part car des informations sont sensibles
        if model is not User:

            # Sérialisation
            data = serialize('json', [model.objects.get(pk=pk), ])

        else:

            # Sérialisation
            allowed_fields = [f.name for f in User._meta.get_fields()]
            for e in ['password', 'is_superuser', 'is_staff', 'last_login']:
                allowed_fields.remove(e)

            data_serialise = serialize('json', [User.objects.get(pk=pk), ], fields=allowed_fields)
            data_load = json.loads(data_serialise)

            if props:
                for i, e in enumerate(data_load):
                    props_dict = {}
                    for p in props:
                        try:
                            props_dict[p] = getattr(model.objects.get(pk=e['pk']), p)()
                        except:
                            pass
                    data_load[i]['props'] = props_dict

            data = json.dumps(data_load)

    except ObjectDoesNotExist:
        data = [[]]

    return HttpResponse(data)


class TestBootstrapSober(TemplateView):
    template_name = 'test_bootstrap.html'

    def get_context_data(self, **kwargs):
        context = super(TestBootstrapSober, self).get_context_data(**kwargs)
        context['nav_tree'] = [
            {
                'label': 'User',
                'icon': 'user',
                'id': 1,
                'subs': [
                    {
                        'label': 'Create',
                        'icon': 'plus',
                        'url': '/users/create',
                        'id': 11
                    },
                    {
                        'label': 'List',
                        'icon': 'list',
                        'url': '/users/user',
                        'id': 12
                    }
                    ]
            },
            {
                'label': 'Presidency',
                'icon': 'book',
                'url': '#',
                'id': 2
            },
            {
                'label': 'Foyer',
                'id': 3,
                'icon': 'beer',
                'subs': [
                    {
                        'label': 'Workboard',
                        'icon': 'briefcase',
                        'url': '/shops/foyer/workboard',
                        'id': 31
                    },
                    {
                        'label': 'Active kegs',
                        'icon': 'barcode',
                        'url': '/shops/foyer/list_active_keg',
                        'id': 32
                    }
                ]
            }
        ]
        return context


class GroupWorkboard(GroupPermissionMixin, View, GroupLateralMenuMixin):
    template_name = 'group_workboard.html'
    perm_codename = None
    lm_active = 'lm_workboard'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        if Permission.objects.get(codename='list_user') in self.group.permissions.all():
            context['user_search_form'] = UserSearchForm()
            context['module_search_user'] = True
        if Permission.objects.get(codename='list_sale') in self.group.permissions.all():
            try:
                shop = shop_from_group(self.group)
                context['sale_list'] = Sale.objects.filter(
                    category='sale',
                    wording='Vente '+shop.name
                ).order_by('-date')[:5]
            except ValueError:
                context['sale_list'] = Sale.objects.filter(
                    category='sale'
                ).order_by('-date')[:5]
            context['module_list_sale'] = True
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        return UserListView().form_valid(UserSearchForm(request.POST))
