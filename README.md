<p align="center">
   <img src="./static/static_dirs/img/borgia-logo-light.png" />
</p>

## Introduction

Borgia est un outil qui permet de construire, gérer et organiser votre vie étudiante ! De la vente de produits à l'organisation d'évènements en passant par la gestion de porte-monnaies virtuels, Borgia est votre meilleur allié pour développer votre association d'étudiants.

## Version actuelle :

[Build 4.5.0](https://github.com/borgia-app/Borgia/releases/tag/4.5.0)

## Commencer

### Installer les modules Python

* `pip install -r requirements.txt`

### Installer LESS

* `yarn global add less`

### Charger les données initiales

* Charger les migrations & les données initiales :
  * `python manage.py makemigrations users shops finances modules settings_data notifications stocks`
  * `python manage.py migrate`
  * `python manage.py loaddata initial`
* Changer le mot de passe du compte admin :
  * `python manage.py loaddata first_member`
  * `python manage.py shell`
  * `from users.models import User`
  * `u = User.objects.get(pk=2)`
  * `u.set_password('admin')`
  * `u.save()`
* Créer ensuite les différents magasins avec l'interface graphique. Attention, ne pas oublier d'ajouter des utiliseurs aux groupes `chefs` et `associés` de chaque magasin après la création.

## Se documenter

La documentation de Borgia est en cours de construction. Des ressources sont disponibles [ici](https://github.com/borgia-app/Borgia-docs).

## Note pour Linux & MacOs:

Python est installé par défaut avec deux versions : 2 et 3. 2 étant la version par défaut.
Or Django (et donc Borgia) fonctionnent avec la version 3. Pour les difféfentes commandes (notamment celles ci-dessus), il faut utiliser `python3`. De même, il faudra utiliser `pip3` pour installer les paquets.

**En prod, il faut changer le setting correspondant.**
