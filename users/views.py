#-*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse, force_text, redirect, HttpResponseRedirect
from users.forms import UserCreationCustomForm, ManageGroupForm, LinkTokenUserForm, UserListCompleteForm
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin, DeleteView
from django.views.generic import ListView, DetailView, FormView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.core import serializers
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from notifications.models import  *
import json
import datetime
import re, datetime

from users.models import User, list_year
from borgia.models import FormNextView, CreateNextView, UpdateNextView, ListCompleteView
from contrib.models import add_to_breadcrumbs


class LinkTokenUserView(FormNextView):
    form_class = LinkTokenUserForm
    template_name = 'users/link_token_user.html'
    success_url = '/auth/login'

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liaison jeton')
        return super(LinkTokenUserView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        user = User.objects.get(username=form.cleaned_data['username'])
        user.token_id = form.cleaned_data['token_id']
        user.save()
        return super(LinkTokenUserView, self).form_valid(form)


def balance_from_username(request):
    try:
        return HttpResponse(User.objects.get(username=request.GET.get('username')).balance)
    except ObjectDoesNotExist:
        pass


class ManageGroupView(FormNextView):
    template_name = 'users/manage_group.html'
    success_url = '/auth/login'
    form_class = ManageGroupForm

    def get(self, request, *args, **kwargs):

        # Test de permission
        group = Group.objects.get(pk=request.GET.get('group_pk'))
        manage_perm_linked = permission_to_manage_group(group=group)[1]
        if request.user.has_perm(manage_perm_linked) is False:
            raise PermissionDenied

        add_to_breadcrumbs(request, 'Groupe ' + group.name)
        return super(ManageGroupView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):

        kwgars = super(ManageGroupView, self).get_form_kwargs()
        group = Group.objects.get(pk=self.request.GET.get('group_pk', self.request.POST.get('group_pk')))

        # Cas d'un groupe de gestionnaires d'organes
        # Permissions possibles -> celles du groupe des chefs de l'organes (hors celle de gérer le group des chefs)
        if group.name.startswith('Gestionnaires') is True:
            chefs_gestionnaires_group_name = group.name.replace('Gestionnaires', 'Chefs gestionnaires')
            kwgars['possible_permissions'] = Group.objects.get(
                name=chefs_gestionnaires_group_name).permissions.all().exclude(
                pk=permission_to_manage_group(group)[0].pk)

        # Pour les autres groupes, tout est possible (utilisation normalement par le président seulement)
        else:
            kwgars['possible_permissions'] = Permission.objects.all()

        # Dans tous les cas, les membres possibles sont tous les membres de l'association
        kwgars['possible_members'] = User.objects.all().exclude(groups=Group.objects.get(name='Membres spéciaux'))
        return kwgars

    def get_initial(self):

        group = Group.objects.get(pk=self.request.GET.get('group_pk', self.request.POST.get('group_pk')))
        initial = super(ManageGroupView, self).get_initial()
        initial['members'] = User.objects.filter(groups=group)
        initial['permissions'] = group.permissions.all()
        return initial

    def get_context_data(self, **kwargs):
        context = super(ManageGroupView, self).get_context_data(**kwargs)
        context['group_name'] = Group.objects.get(pk=self.request.GET.get('group_pk')).name
        context['group_pk'] = self.request.GET.get('group_pk')
        return context

    def form_valid(self, form):

        group = Group.objects.get(pk=self.request.POST.get('group_pk'))
        old_members = User.objects.filter(groups=group)
        new_members = form.cleaned_data['members']
        old_permissions = group.permissions.all()
        new_permissions = form.cleaned_data['permissions']

        # Modification des membres
        for m in old_members:
            if m not in new_members:
                m.groups.remove(group)
                m.save()
        for m in new_members:
            if m not in old_members:
                m.groups.add(group)
                m.save()

        # Modification des permissions
        for p in old_permissions:
            if p not in new_permissions:
                group.permissions.remove(p)
        for p in new_permissions:
            if p not in old_permissions:
                group.permissions.add(p)
        group.save()

        return super(ManageGroupView, self).form_valid(form)


def username_from_username_part(request):
    data = []
    for e in User.objects.filter(family=request.GET.get('keywords')):
        data.append(e.username)
    return HttpResponse(json.dumps(data))


def profile_view(request):
    add_to_breadcrumbs(request, 'Profil')
    return render(request, 'users/profile.html', locals())


class UserCreateView(FormNextView):
    form_class = UserCreationCustomForm
    template_name = 'users/create.html'
    success_url = '/users/'  # Redirection a la fin

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Création user')
        return super(UserCreateView, self).get(request, *args, **kwargs)

    # Override form_valid pour enregistrer les attributs issues d'autres classes (m2m ou autres)
    def form_valid(self, form):
        user = User.objects.create(username=form.cleaned_data['username'],
                                   first_name=form.cleaned_data['first_name'],
                                   last_name=form.cleaned_data['last_name'],
                                   email=form.cleaned_data['email'],
                                   surname=form.cleaned_data['surname'],
                                   family=form.cleaned_data['family'],
                                   campus=form.cleaned_data['campus'],
                                   year=form.cleaned_data['year'])
        user.set_password(form.cleaned_data['password'])
        user.save()

        # Cas d'un membre d'honneur
        if form.cleaned_data['honnor_member'] is True:
            user.groups.add(Group.objects.get(name='Membres d\'honneurs'))
        # Sinon, c'est un Gadz'Arts
        else:
            user.groups.add(Group.objects.get(name='Gadz\'Arts'))
        user.save()

        # Notifications
        user_creation_notify_success_to_user_and_admins(self.request, user)

        return super(UserCreateView, self).form_valid(form)

    def get_initial(self):
        return {'campus': 'Me', 'year': 2014}


class UserRetrieveView(DetailView):
    model = User
    template_name = "users/retrieve.html"

    def get(self, request, *args, **kwargs):

        if request.user.has_perm('users.retrieve_user') is False and int(kwargs['pk']) != request.user.pk:
            raise PermissionDenied

        add_to_breadcrumbs(request, 'Détail user')
        return super(UserRetrieveView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserRetrieveView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next')
        return context


class UserUpdateView(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'surname', 'email', 'family', 'year', 'campus', 'avatar']
    template_name = 'users/update.html'
    success_url = '/users/profile/'

    def get(self, request, *args, **kwargs):

        if request.user.has_perm('users.change_user') is False and int(kwargs['pk']) != request.user.pk:
            raise PermissionDenied

        add_to_breadcrumbs(request, 'Modification user')
        return super(UserUpdateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.request.POST.get('next', self.success_url))
        return context

    def get_success_url(self):
        # Notifications
        user_updating_notify_success_to_user_and_admins(self.request, self.object)
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))

    def form_valid(self, form):

        # Si on modifie l'avatar (changement ou suppression)
        # Si l'avatar a changé, et qu'initialement il n'était pas vide
        # Alors on supprime l'ancien avatar des fichiers
        old_object = User.objects.get(pk=self.kwargs['pk'])
        if old_object.avatar != self.object.avatar and old_object.avatar:
            old_object.avatar.delete(True)

        return super(UserUpdateView, self).form_valid(form)


class UserDesactivateView(SuccessMessageMixin, View):
    template_name = 'users/desactivate.html'

    success_url = '/users/'
    success_message = "Mise à jour"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        add_to_breadcrumbs(request, 'Désactivation user')
        return render(request, 'users/desactivate.html',
                      {'object': user,
                       'next': self.request.GET.get('next', self.request.POST.get('next', self.success_url))})

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        user_updating_notify_success_to_user_and_admins(self.request, user)
        if user.is_active is True:
            user.is_active = False
        else:
            user.is_active = True

        user.save()
        return redirect(force_text(self.request.POST.get('next')))


class UserListView(ListView):
    model = User
    template_name = "users/list.html"
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, "Liste users")
        return super(UserListView, self).get(request, *args, **kwargs)


class UserListCompleteView(ListCompleteView):
    form_class = UserListCompleteForm
    template_name = 'users/user_list_complete.html'
    success_url = '/auth/login'
    attr = {
        'order_by': 'last_name',
        'years': 'all',
        'active': True,
    }

    def get(self, request, *args, **kwargs):
        add_to_breadcrumbs(request, 'Liste users')
        return super(UserListCompleteView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UserListCompleteView, self).get_form_kwargs()
        kwargs['list_year'] = list_year()
        return kwargs

    def get_initial(self):
        initial = {}
        if self.attr['years'] == 'all':
            initial['all'] = True
        else:
            list_years = list_year()
            for y in json.loads(self.attr['years']):
                initial['field_year_%s' % list_years.index(y)] = True
        if self.attr['active'] is False:
            initial['unactive'] = True
        return initial

    def get_context_data(self, **kwargs):
        context = super(UserListCompleteView, self).get_context_data(**kwargs)
        if self.attr['years'] != 'all':
            context['query_user'] = User.objects.filter(is_active=self.attr['active'], year__in=json.loads(self.attr['years'])).exclude(
                groups=Group.objects.get(name='Membres spéciaux')).order_by(self.attr['order_by'])
        else:
            context['query_user'] = User.objects.filter(is_active=self.attr['active']).exclude(
                groups=Group.objects.get(name='Membres spéciaux')).order_by(self.attr['order_by'])

        context['next'] = self.request.GET.get('next', self.request.POST.get('next'))
        return context

    def form_valid(self, form, **kwargs):
        """
        Se charge de vérifier que si un choix sur le formulaire est fait, il met à jour les paramètres enregistrés.
        """
        list_year_result = []

        # Cas où "toutes les promotions" est coché
        if form.cleaned_data['all'] is True:
            self.attr['years'] = 'all'
        # Sinon on choisi seulement les promotions sélectionnées
        else:
            for i in range(0, len(list_year())):
                if form.cleaned_data["field_year_%s" % i] is True:
                    list_year_result.append(list_year()[i])
                    self.attr['years'] = json.dumps(list_year_result)

        # Si "utilisateurs désactivés" est coché
        if form.cleaned_data['unactive'] is True:
            self.attr['active'] = False
        else:
            self.attr['active'] = True

        return self.render_to_response(self.get_context_data(**kwargs))


def permission_to_manage_group(group):
    """
    Récupère la permission qui permet de gérer le groupe 'group'
    Utilisable directement dans has_perm
    :param group:
    :return: (objet permission, permission name formatée pour has_perm)
    """
    perm = Permission.objects.get(codename=group_name_clean_for_perm(group.name) + '_group_manage')
    perm_name = 'users.' + perm.codename
    return perm, perm_name


def group_name_clean_for_perm(group_name):
    """
    Formate un string en enlevant les accents,
    remplaçant espaces et ' par _
    Utilisé notamment pour permission_to_manage_group
    :param group_name:
    :return: string
    """
    dirty = ['é', 'è', 'ê', 'à', 'ù', 'û', 'ç', 'ô', 'î', 'ï', 'â', ' ', "\'"]
    clean = ['e', 'e', 'e', 'a', 'u', 'u', 'c', 'o', 'i', 'i', 'a', '_', '_']

    for i in range(0, len(dirty)):
        group_name = group_name.replace(dirty[i], clean[i])

    group_name = group_name.lower()
    return group_name


def workboard_presidents(request):

    group_vices_presidents_vie_interne_pk = Group.objects.get(name='Vices présidents délégués à la vie interne').pk
    group_tresoriers_pk = Group.objects.get(name='Trésoriers').pk
    group_presidents_pk = Group.objects.get(name='Présidents').pk
    group_gadzarts_pk = Group.objects.get(name='Gadz\'Arts').pk
    group_membres_honneurs_pk = Group.objects.get(name='Membres d\'honneurs').pk

    add_to_breadcrumbs(request, 'Workboard présidents')
    return render(request, 'users/workboard_presidents.html', locals())


def workboard_vices_presidents_vie_interne(request):

    group_chefs_gestionnaires_foyer_pk = Group.objects.get(name='Chefs gestionnaires du foyer').pk
    group_chefs_gestionnaires_auberge_pk = Group.objects.get(name='Chefs gestionnaires de l\'auberge').pk

    add_to_breadcrumbs(request, 'Workboard vices présidents')
    return render(request, 'users/workboard_vices_presidents_vie_interne.html', locals())