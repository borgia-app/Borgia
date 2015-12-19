from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from accounts.forms import ChangeInformationsForm, UserCreationCustomForm, UserUpdateCustomForm
from django.views.generic.edit import CreateView, UpdateView
from accounts.models import User


# Page de profil
@login_required
def profile_view(request):

    # Récupération des variables
    user = request.user
    # Mise en forme de l'année mode Pg, 2014 -> 214
    year_pg = int(str(user.year)[:1] + str(user.year)[-2:])

    return render(request, 'accounts/profile.html', locals())


# Changement des informations personnelles
@login_required
def change_informations_view(request):

    # Méthode POST
    if request.method == "POST":  # POST - envoie du formulaire
        # Récupération du formulaire
        form = ChangeInformationsForm(request.POST)
        if form.is_valid():  # Validité du formulaire

            # Si les informations ont changé, les mettre à jour
            if form.cleaned_data['new_surname'] != request.user.surname:
                request.user.surname = form.cleaned_data['new_surname']
            if form.cleaned_data['new_family'] != request.user.family:
                request.user.family = form.cleaned_data['new_family']
            if form.cleaned_data['new_year'] != request.user.year:
                request.user.year = form.cleaned_data['new_year']
            if form.cleaned_data['new_campus'] != request.user.campus:
                request.user.campus = form.cleaned_data['new_campus']
            request.user.save()

            # Redirection vers la page profile
            return render(request, 'accounts/profile.html')

        else: # Formulaire invalide, nouvel essai
            form = ChangeInformationsForm(initial={'new_surname': request.user.surname,
                                                   'new_family': request.user.family,
                                                   'new_year': request.user.year,
                                                   'new_campus': request.user.campus})
    # Méthode GET
    else:
        # Création du formulaire
        form = ChangeInformationsForm(initial={'new_surname': request.user.surname,
                                               'new_family': request.user.family,
                                               'new_year': request.user.year,
                                               'new_campus': request.user.campus})

    return render(request, 'accounts/change_informations.html', locals())


# Création d'un user
# Pas possibilité de mettre un décorateur ici, on le met directement dans le routage d'url
class UserCreateView(CreateView):
    model = User
    form_class = UserCreationCustomForm
    template_name = 'accounts/user_create_form.html'
    success_url = 'profile'  # Redirection à la fin


# Modification d'un user
class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateCustomForm
    template_name = 'accounts/user_update_form.html'
    success_url = 'profile'  # Redirection à la fin
