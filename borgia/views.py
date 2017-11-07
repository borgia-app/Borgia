from django.views.generic import FormView, TemplateView, View
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from functools import reduce
from django.core.serializers import serialize
from datetime import datetime, timedelta

from users.models import User
from django.contrib.auth.models import Group
import json
from django.core.exceptions import ObjectDoesNotExist

from borgia.utils import *
from finances.models import Sale, SharedEvent, Transfert, Recharging, ExceptionnalMovement
from shops.models import Product
from borgia.forms import LoginForm
from django.conf import settings

class Login(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = None

    def dispatch(self, request, *args, **kwargs):
        try:
            if self.kwargs['shop_name']:
                try:
                    self.shop = Shop.objects.get(name=self.kwargs['shop_name'])
                except ObjectDoesNotExist:
                    raise Http404
            self.gadzarts = self.kwargs['gadzarts']
        except KeyError or ObjectDoesNotExist:
            pass
        return super(Login, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        kwargs = super(Login, self).get_form_kwargs(**kwargs)
        try:
            if self.gadzarts:
                kwargs['module'], created = SelfSaleModule.objects.get_or_create(
                    shop=self.shop)
            else:
                kwargs['module'], created = OperatorSaleModule.objects.get_or_create(
                    shop=self.shop)
        except AttributeError or ObjectDoesNotExist:
            kwargs['module'] = None
        return kwargs

    def get_success_url(self, **kwargs):
        try:
            self.shop = Shop.objects.get(name=self.kwargs['shop_name'])
            self.gadzarts = self.kwargs['gadzarts']
            if self.gadzarts:
                self.success_url = self.to_shop_selfsale()
            else:
                self.success_url	 = self.to_shop_operatorsale()
        except KeyError or ObjectDoesNotExist:
            pass

        try:
            if self.request.session['after_login']:
                self.success_url = self.request.session['after_login']
                del self.request.session['after_login']
        except KeyError:
            pass

        if self.success_url is None:
            self.success_url = reverse(
                'url_group_workboard',
                kwargs={'group_name': 'gadzarts'}
            )
        return super(Login, self).get_success_url(**kwargs)

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)
		# Update forecast_balance on login
        user.forecast_balance()
        return super(Login, self).form_valid(form)

    def to_shop_selfsale(self):
        if (Group.objects.get(name='gadzarts')
                in self.request.user.groups.all()):
            return reverse(
                'url_module_selfsale',
                kwargs={'group_name': 'gadzarts', 'shop_name': self.shop.name}
            )
        else:
            return None

    def to_shop_operatorsale(self):
        if (Group.objects.get(name='chiefs-'+self.shop.name)
                in self.request.user.groups.all()):
            return reverse(
                'url_module_operatorsale',
                kwargs={'group_name': 'chiefs-'+self.shop.name,
                        'shop_name': self.shop.name}
            )
        elif (Group.objects.get(name='associates-'+self.shop.name)
                in self.request.user.groups.all()):
            return reverse(
                'url_module_operatorsale',
                kwargs={'group_name': 'associates-'+self.shop.name,
                        'shop_name': self.shop.name}
            )
        else:
            return None
        return success_url

    def get_context_data(self, **kwargs):
        context = super(Login, self).get_context_data(**kwargs)
        context['default_theme'] = settings.DEFAULT_TEMPLATE
        try:
            if self.shop:
                if self.gadzarts:
                    context['next'] = "Gadz'Arts - " + self.shop.__str__()
                else:
                    context['next'] = "opérateur - " + self.shop.__str__()
        except AttributeError:
            pass

        context['shop_list'] = []
        for shop in Shop.objects.all().exclude(pk=1):
            operator_module, created = OperatorSaleModule.objects.get_or_create(
                shop=shop)
            self_module, created = SelfSaleModule.objects.get_or_create(
                shop=shop)
            context['shop_list'].append({
                'shop': shop,
                'operator_module': operator_module,
                'self_module': self_module
            })
        return context


class Logout(View):
    def get(self, request, *args, **kwargs):
        try:
            success_url = request.session['save_login_url']
        except KeyError:
            success_url = '/auth/login/'
        try:
            del request.session['save_login_url']
        except KeyError:
            pass
        if request.user.is_authenticated():
            logout(request)
        return redirect(success_url)


def jsi18n_catalog(request):
    """
    Render le js nécessaire à la jsi18n utilisé dans certains widgets venant
    de l'app admin
    Par exemple: FilteredSelectMultiple
    """
    return render(request, 'jsi18n.html')


def handler403(request):
    context = {}
    try:
        group_name = request.path.split('/')[1]
        context['group'] = Group.objects.get(name=group_name)
        context['group_name'] = group_name
        if (request.user.groups.all().exclude(
                pk__in=[1, 5, 6]).count() > 0):
            context['first_job'] = request.user.groups.all().exclude(
                pk__in=[1, 5, 6])[0]
        context['list_selfsalemodule'] = []
        for shop in Shop.objects.all().exclude(pk=1):
            try:
                module = SelfSaleModule.objects.get(shop=shop)
                if module.state is True:
                    context['list_selfsalemodule'].append(shop)
            except ObjectDoesNotExist:
                pass
    except IndexError:
        pass
    except ObjectDoesNotExist:
        pass
    response = render(
        request,
        '403.html',
        context=context)
    response.status_code = 403
    return response


def handler404(request):
    context = {}
    try:
        group_name = request.path.split('/')[1]
        context['group'] = Group.objects.get(name=group_name)
        context['group_name'] = group_name
        if (request.user.groups.all().exclude(
                pk__in=[1, 5, 6]).count() > 0):
            context['first_job'] = request.user.groups.all().exclude(
                pk__in=[1, 5, 6])[0]
        context['list_selfsalemodule'] = []
        for shop in Shop.objects.all().exclude(pk=1):
            try:
                module = SelfSaleModule.objects.get(shop=shop)
                if module.state is True:
                    context['list_selfsalemodule'].append(shop)
            except ObjectDoesNotExist:
                pass
    except IndexError:
        pass
    except ObjectDoesNotExist:
        pass
    response = render(
        request,
        '404.html',
        context=context)
    response.status_code = 404
    return response


def handler500(request):
    context = {}
    try:
        group_name = request.path.split('/')[1]
        context['group'] = Group.objects.get(name=group_name)
        context['group_name'] = group_name
    except IndexError:
        pass
    except ObjectDoesNotExist:
        pass
    response = render(
        request,
        '500.html',
        context=context)
    response.status_code = 500
    return response


def page_clean(request, template_name):
    return render(request, 'page_clean.html')


def get_list_model(request, model, search_in, props=None):
    """
    Permet de sérialiser en JSON les instances de modèle. Il est possible de
    donner des paramtères GET à cette fonction pour moduler
    la liste obtenue, plutôt que de faire un traitement en JS.
    Ne renvoie par les informations sensibles comme is_superuser ou password.

    :param model: Model dont on veut lister les instances
    :type model: héritée de models.Model
    :param search_in: paramètres dans lesquels le paramètre GET search sera
    recherché
    :type search_in: liste de chaînes de caractères
    :param props: méthodes du model à envoyer dans la sérialisation en
    supplément
    :type props: liste de chaînes de caractères de nom de méthodes de model
    :param request.GET : chaîne de caractère qui doit représenter une
    recherche filter dans un des champs de model
    :type request.GET : doit être dans les champs de model
    Les paramètres spéciaux sont order_by pour trier et search pour chercher
    dans search_in
    :return HttpResponse(data): liste des instances de model sérialisé
    en JSON, modulée par les parametres

    Exemple :
    model = User
    search_in = ['username', 'last_name', 'first_name']
    request.GET = { 'family': '101-99', 'order_by': 'year' }
    renverra la liste des users dont la famille est 101-99
    en les triant par année
    """

    # Liste des filtres
    kwargs_filter = {}
    for param in request.GET:
        if param not in ['order_by', 'reverse', 'search']:
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
        args_search = reduce(
            lambda q, where: q | Q(
                **{where + '__startswith': request.GET['search']}), search_in,
            Q())
        query = query.filter(args_search).distinct()
    except KeyError:
        pass

    # Sérialisation
    if model is not User:

        data_serialise = serialize('json', query)

    else:  # Cas User traité à part car contient des fields sensibles

        # Suppression des users spéciaux
        query = query.exclude(
            Q(groups=Group.objects.get(pk=1)) | Q(username='admin'))

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
        if (request.GET['order_by']
                in [f.name for f in model._meta.get_fields()]):
            data_load = sorted(
                data_load,
                key=lambda obj: obj['fields'][request.GET['order_by']],
                reverse=reverse)
        # Trie par la valeur d'une méthode
        else:
            data_load = sorted(
                data_load,
                key=lambda obj: getattr(
                    model.objects.get(pk=obj['pk']),
                    request.GET['order_by'])(),
                reverse=reverse)
    except KeyError:
        pass

    # Information du nombre total d'élément
    count = len(data_load)

    # End et begin
    try:
        data_load = data_load[int(request.GET[
            'begin']):int(request.GET['end'])]
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
    Ne renvoie par les informations sensibles comme is_superuser ou password
    dans le cas d'un User.

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
    serialise envoie une liste sérialisé, pour récupérer en js il ne faut
    pas faire data car c'est une liste, mais bien
    data[0]. Il n'y aura toujours que 1 élément dans cette liste car
    générée par un objects.get()
    """

    try:
        # On traite le cas particulier de User à part car des informations
        # sont sensibles
        if model is not User:

            # Sérialisation
            data = serialize('json', [model.objects.get(pk=pk), ])

        else:

            # Sérialisation
            allowed_fields = [f.name for f in User._meta.get_fields()]
            for e in ['password', 'is_superuser', 'is_staff', 'last_login']:
                allowed_fields.remove(e)

            data_serialise = serialize('json', [User.objects.get(pk=pk), ],
                                       fields=allowed_fields)
            data_load = json.loads(data_serialise)

            if props:
                for i, e in enumerate(data_load):
                    props_dict = {}
                    for p in props:
                        try:
                            props_dict[p] = getattr(
                                model.objects.get(pk=e['pk']), p)()
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


class GadzartsGroupWorkboard(GroupPermissionMixin, View,
                             GroupLateralMenuMixin):
    template_name = 'workboards/gadzarts_workboard.html'
    perm_codename = None
    lm_active = 'lm_workboard'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['transaction_list'] = self.get_transactions(request)
        return render(request, self.template_name, context=context)

    def get_transactions(self, request):
        transactions = {}
        transactions['months'] = self.monthlist(
            datetime.now() - timedelta(days=365),
            datetime.now())

        transactions['all'] = self.request.user.list_transaction()[:5]

        # Shops sales
        sale_list = Sale.objects.filter(sender=self.request.user).order_by('-datetime')
        transactions['shops'] = []
        for shop in Shop.objects.all().exclude(pk=1):
            list_filtered = sale_list.filter(shop=shop)
            total = 0
            for sale in list_filtered:
                total += sale.amount()
            transactions['shops'].append({
                'shop': shop,
                'total': total,
                'sale_list_short': list_filtered[:5],
                'data_months': self.data_months(request, list_filtered, transactions['months'])
            })

        # Transferts
        transfert_list = Transfert.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        ).order_by('-datetime')
        transactions['transferts'] = {
            'transfert_list_short': transfert_list[:5]
        }

        # Rechargings
        rechargings_list = Recharging.objects.filter(sender=self.request.user).order_by('-datetime')
        transactions['rechargings'] = {
            'recharging_list_short': rechargings_list[:5]
        }

        # ExceptionnalMovements
        exceptionnalmovements_list = ExceptionnalMovement.objects.filter(recipient=self.request.user).order_by('-datetime')
        transactions['exceptionnalmovements'] = {
            'exceptionnalmovement_list_short': exceptionnalmovements_list[:5]
        }

        # Shared event
        sharedevents_list = SharedEvent.objects.filter(done=True, users=self.request.user).order_by('-datetime')
        for obj in sharedevents_list:
            obj.amount = obj.get_price_of_user(self.request.user)

        transactions['sharedevents'] = {
            'sharedevent_list_short': sharedevents_list[:5]
        }

        return transactions

    def data_months(self, request, list, months):
        amounts = [0 for i in range(0, len(months))]
        for object in list:
            if object.datetime.strftime("%b-%y") in months:
                amounts[
                    months.index(object.datetime.strftime("%b-%y"))] +=\
                        abs(object.amount())
        return amounts

    def monthlist(self, start, end):
        total_months = lambda dt: dt.month + 12 * dt.year
        mlist = []
        for tot_m in range(total_months(start)-1, total_months(end)):
            y, m = divmod(tot_m, 12)
            mlist.append(datetime(y, m+1, 1).strftime("%b-%y"))
        return mlist


class ShopGroupWorkboard(GroupPermissionMixin, ShopFromGroupMixin, View,
                         GroupLateralMenuMixin):
    perm_codename = None
    template_name = 'workboards/shop_workboard.html'
    lm_active = 'lm_workboard'

    def get(self, request, *args, **kwargs):
        if self.shop is None:
            raise Http404

        context = self.get_context_data(**kwargs)
        context['sale_list'] = self.get_sales(request)
        context['purchase_list'] = self.get_purchases(request)
        return render(request, self.template_name, context=context)

    def get_sales(self, request):
        sales = {}
        list = Sale.objects.filter(shop=self.shop).order_by('-datetime')
        sales['weeks'] = self.weeklist(
            datetime.now() - timedelta(days=365),
        datetime.now())
        sales['data_weeks'] = self.sale_data_weeks(list, sales['weeks'])[0]
        sales['total'] = self.sale_data_weeks(list, sales['weeks'])[1]
        sales['all'] = list[:7]
        return sales

    # TODO: purchases with stock
    def get_purchases(self, request):
        purchases = {}
        return purchases

    # TODO: purchases with stock
    def purchase_data_weeks(self, list_single_products, list_containers,
                            weeks):
        amounts = [0 for i in range(0, len(weeks))]
        total = 0

        return amounts, total

    def sale_data_weeks(self, list, weeks):
        amounts = [0 for i in range(0, len(weeks))]
        total = 0
        for object in list:
            string = (str(object.datetime.isocalendar()[1])
                      + '-' + str(object.datetime.year))
            if string in weeks:
                amounts[weeks.index(string)] += object.amount()
                total += object.amount()
        return amounts, total

    def weeklist(self, start, end):
        list = []
        for i in range(start.year, end.year+1):
            week_start = 1
            week_end = 52
            if i == start.year:
                week_start = start.isocalendar()[1]
            if i == end.year:
                week_end = end.isocalendar()[1]
            list += [str(j) + '-' + str(i) for j in range(
                week_start, week_end+1)]
        return list


class PresidentsGroupWorkboard(GroupPermissionMixin, View,
                               GroupLateralMenuMixin):
    template_name = 'workboards/presidents_workboard.html'
    perm_codename = None
    lm_active = 'lm_workboard'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['sale_list'] = Sale.objects.all().order_by('-datetime')[:5]
        context['events'] = []
        for event in SharedEvent.objects.all():
            context['events'].append({
                'title': event.description,
                'start': event.date
            })
        return render(request, self.template_name, context=context)


class VicePresidentsInternalGroupWorkboard(GroupPermissionMixin, View,
                                   GroupLateralMenuMixin):
    template_name = 'workboards/vice-presidents-internal_workboard.html'
    perm_codename = None
    lm_active = 'lm_workboard'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['sale_list'] = Sale.objects.all().order_by('-datetime')[:5]
        context['events'] = []
        for event in SharedEvent.objects.all():
            context['events'].append({
                'title': event.description,
                'start': event.date
            })
        return render(request, self.template_name, context=context)


class TreasurersGroupWorkboard(GroupPermissionMixin, View,
                               GroupLateralMenuMixin):
    template_name = 'workboards/treasurers_workboard.html'
    perm_codename = None
    lm_active = 'lm_workboard'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['sale_list'] = Sale.objects.all().order_by('-datetime')[:5]
        context['events'] = []
        for event in SharedEvent.objects.all():
            context['events'].append({
                'title': event.description,
                'start': event.date
            })
        return render(request, self.template_name, context=context)
