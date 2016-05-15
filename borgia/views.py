#-*- coding: utf-8 -*-
from django.views.generic import FormView
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.forms import BooleanField
from django.db.models import Q
from functools import reduce
from operator import or_
from django.core.serializers import serialize

from users.models import User
from django.contrib.auth.models import Group
import json
from django.core.exceptions import ObjectDoesNotExist


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
        if param != 'order_by' and param != 'search':
            if param in model._meta.get_all_field_names():
                # Traitement spécifique pour les booléens envoyés en GET
                if isinstance(model._meta.get_field(param), BooleanField):
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

    # On traite le cas particulier de User à part car des informations sont sensibles
    if model is not User:

        # Order_by si précisé
        try:
            query = query.order_by(request.GET['order_by'])
        except KeyError:
            pass

        # Sérialisation
        data_serialise = serialize('json', query)
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

    else:
        # Suppression des users spéciaux
        query = query.exclude(Q(groups=Group.objects.get(pk=9)) | Q(username='admin'))

        # Order_by si précisé
        try:
            query = query.order_by(request.GET['order_by'])
        except KeyError:
            pass

        # Sérialisation
        allowed_fields = User._meta.get_all_field_names()
        for e in ['password', 'is_superuser', 'is_staff', 'last_login']:
            allowed_fields.remove(e)

        data_serialise = serialize('json', query, fields=allowed_fields)
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
            allowed_fields = User._meta.get_all_field_names()
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

    except ObjectDoesNotExist:
        data = [[]]

    return HttpResponse(data_load)