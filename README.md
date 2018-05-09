<p align="center">
   <img src="./static/static_dirs/img/borgia-logo-light.png" />
</p>

Build : [4.5.3](https://github.com/borgia-app/Borgia/releases/tag/4.5.3)

Licence : [GNU GPL version 3](./license.txt)

Chat : [Join us on Slack](https://borgia-app.slack.com)

## Introduction

Borgia est un outil qui permet de construire, gérer et organiser votre vie étudiante ! De la vente de produits à l'organisation d'évènements en passant par la gestion de porte-monnaies virtuels, Borgia est votre meilleur allié pour développer votre association d'étudiants.

## Commencer

### Installer les modules Python

* `pip install -r requirements.txt`.

### Installer LESS

* `yarn global add less`.

### Paramètres

* Modifier le fichier `borgia/settings.py` en fonction de vos données et paramètres (notamment domaines, compte Lydia et compte mail).

### Charger les données initiales

* Charger les migrations & les données initiales :
  * `python manage.py makemigrations users shops finances modules settings_data notifications stocks`,
  * `python manage.py migrate`,
  * `python manage.py loaddata initial`.
* Changer le mot de passe du compte admin :
  * `python manage.py loaddata first_member`,
  * `python manage.py shell`,
  * `from users.models import User`,
  * `u = User.objects.get(pk=2)`,
  * `u.set_password('admin')`.
  * `u.save()`
* Créer ensuite les différents magasins avec l'interface graphique. Attention, ne pas oublier d'ajouter des utiliseurs aux groupes `chefs` et `associés` de chaque magasin après la création.

## Se documenter

La documentation de Borgia est en cours de construction. Des ressources sont disponibles [ici](https://github.com/borgia-app/Borgia-docs).

## Note pour Linux & MacOs:

Python est installé par défaut avec deux versions : 2 et 3. 2 étant la version par défaut.
Or Django (et donc Borgia) fonctionnent avec la version 3. Pour les difféfentes commandes (notamment celles ci-dessus), il faut utiliser `python3`. De même, il faudra utiliser `pip3` pour installer les paquets.

## Contribuer

L'équipe qui s'occupe de Borgia travaille tous les jours pour assurer un logiciel de qualité. Nous sommes à l'écoute de vos remarques et nous essayons d'améliorer Borgia de manière continue.

Borgia est actuellement utilisé par plusieurs milliers d'étudiants depuis plus de 2 ans, notamment dans les centres [Arts et Métiers](https://artsetmetiers.fr/). Nous cherchons activement des personnes pour participer à cette belle aventure, n'hésite pas à nous contacter directement. Nous avons de grands projets pour Borgia (une application mobile, de nouvelles fonctionnalités, ...) !

Enfin, si tu as une idée ou que tu as constaté un bug, n'hésite pas à ouvrir une [issue](https://github.com/borgia-app/Borgia/issues) ou même un [pull request](https://github.com/borgia-app/Borgia/pulls).
