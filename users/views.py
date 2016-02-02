#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.forms import UserCreationCustomForm
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin, DeleteView
from django.views.generic import ListView, DetailView


from users.models import User
from finances.models import Purchase

# Page de profil
@login_required
def profile_view(request):

    list_purchase_perso = Purchase.objects.filter(client=request.user)

    return render(request, 'users/profile.html', locals())


# C - Creation d'un user
class UserCreateView(CreateView):
    model = User
    form_class = UserCreationCustomForm
    template_name = 'users/create.html'
    success_url = '/users/profile/'  # Redirection a la fin

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


# R - Recuperation d'un user
class UserRetrieveView(DetailView):
    model = User
    template_name = "users/retrieve_view.html"


# U - Modification d'un user
# Si l'on se modifie soit meme
class UserUpdatePersoView(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'surname', 'family', 'year', 'campus']
    template_name = 'users/update.html'
    success_url = '/users/profile/'


# Si un admin veut modifier quelqu'un d'autre
class UserUpdateAdminView(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'surname', 'family', 'year', 'campus', 'user_permissions', 'groups']
    template_name = 'users/update.html'
    success_url = '/users/'


# D - Suppression d'un user
class UserDeleteView(DeleteView):
    model = User
    template_name = 'users/delete.html'
    success_url = '/users/'


# Liste d'users
class UserListView(ListView):
    model = User
    template_name = "users/list_view.html"
    queryset = User.objects.all()

    class Meta:
        permissions = (
            ('list_user', 'Acceder a la liste des Users')
        )
