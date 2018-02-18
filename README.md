<p align="center">
   <img src="./static/static_dirs/img/borgia-logo-light.png" />
</p>

## Get started : initial commands

* S'assurer que LESS est installé (avec ``yarn global add less``)

* Charger les migrations & les données initiales :
    * ``python manage.py makemigrations users shops finances modules settings_data notifications stocks``
    * ``python manage.py migrate``
    * ``python manage.py loaddata initial``
* Changer le mot de passe du compte admin :
    * ``python manage.py loaddata first_member``
    * ``python manage.py shell``
    * ``from users.models import User``
    * ``u = User.objects.get(pk=2)``
    * ``u.set_password('admin')``
    * ``u.save()``


### Update requirements.txt
Ce fichier contient tout les modules python nécessaires pour l'execution de borgia.
Celui-ci peut être mis à jour en théorie avec la commande suivante :

* ``pip freeze -r devel-req.txt > stable-req.txt``

Cependant, ceci ajoute TOUT les modules installés par pip. Donc également les éventuels modules ajoutés pour d'autres projet.

### Installer les modules avec le fichier requirements.txt

Pour installer les modules, il suffit d'effectuer la commande :

``pip install -r requirements.txt``


## Note pour Linux (et mac ??):

Python est installé par défaut avec deux version : 2 et 3. 2 étant la version par défaut.
Or Django (et donc Borgia) fonctionnent avec la version 3. Pour les difféfentes manip (notamment celle ci-dessus), il faut utiliser ``python3``. De même, il faudra utiliser ``pip3``


## Fonctionnement Graphique:

 Le nouveau fonctionnement est le suivant : on génère un fichier "bootstrap" modifié, en utilisant LESS :
 Les variables de bootstrap sont définies pour obtenir le template.
 Si-besoin, on ajoute un fichier de style en LESS (ici main). Cici nous permet de changer facilement de template.
 De plus ce fichier est moins volumineux, car on supprime les modules de bootstrap non-utilisés.

 Le sous-dossier less/less contient les fichiers originaux de bootstrap non-modifiés.

 Le fichier LESS est compilé dans static_dirs actuellement. __En prod, il faut changer le setting correspondant.__


## Version actuellement en développement :
Build 4.4.3 ([draft 4.5](https://github.com/borgia-app/Borgia/releases/tag/untagged-35f548c24f5bef9cfd1e))

## Dernière version stable :
[Build 4.4.0](https://github.com/borgia-app/Borgia/releases/tag/4.4.0)
