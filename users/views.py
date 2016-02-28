#-*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse, force_text
from users.forms import UserCreationCustomForm, ManageGroupForm
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin, DeleteView
from django.views.generic import ListView, DetailView, FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.core import serializers
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied

from users.models import User


class ManageGroupView(FormView):
    template_name = 'users/manage_group.html'
    success_url = '/auth/login'
    form_class = ManageGroupForm

    def get_success_url(self):
        if self.request.POST.get('next') != 'None':
            return force_text(self.request.POST.get('next', self.success_url))
        else:
            return force_text(self.success_url)

    def get(self, request, *args, **kwargs):

        # Test de permission
        group = Group.objects.get(pk=request.GET.get('group_pk'))
        manage_perm_linked = permission_to_manage_group(group=group)[1]
        if request.user.has_perm(manage_perm_linked) is False:
            raise PermissionDenied
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
        kwgars['possible_members'] = User.objects.all()
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
        context['next'] = self.request.GET.get('next')
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
    data = ''
    if len(request.GET.get('keywords')) >= 3:
        for e in User.objects.filter(username__startswith=request.GET.get('keywords')):
            data += e.username + '|'
    return HttpResponse(data)


def profile_view(request):

    return render(request, 'users/profile.html', locals())


class UserCreateView(SuccessMessageMixin, CreateView):
    model = User
    form_class = UserCreationCustomForm
    template_name = 'users/create.html'
    success_message = "%(name)s was created successfully"
    success_url = '/users/'  # Redirection a la fin

    # Override form_valid pour enregistrer les attributs issues d'autres classes (m2m ou autres)
    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save()  # Save l'object et ses attributs
        form.save_m2m()  # Save les m2m de l'object cree
        return super(ModelFormMixin, self).form_valid(form)

    def get_initial(self):
        return {'campus': 'Me', 'year': 2014}


class UserRetrieveView(DetailView):
    model = User
    template_name = "users/retrieve.html"

    def get(self, request, *args, **kwargs):

        if request.user.has_perm('users.retrieve_user') is False and int(kwargs['pk']) != request.user.pk:
            raise PermissionDenied

        return super(UserRetrieveView, self).get(request, *args, **kwargs)


class UserUpdateView(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'surname', 'family', 'year', 'campus']
    template_name = 'users/update.html'
    success_url = '/users/profile/'

    def get(self, request, *args, **kwargs):

        if request.user.has_perm('users.change_user') is False and int(kwargs['pk']) != request.user.pk:
            raise PermissionDenied

        return super(UserUpdateView, self).get(request, *args, **kwargs)


class UserDeleteView(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'users/delete.html'
    success_url = '/users/'
    success_message = "Supression"


class UserListView(ListView):
    model = User
    template_name = "users/list.html"
    queryset = User.objects.all()


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
    print(group_name)
    return group_name