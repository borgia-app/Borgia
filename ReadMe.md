# borgia-app
Borgia private repository

# Get started : initial commands
(to load data and create a admin user)

python manage.py makemigrations users shops finances modules settings_data notifications stocks
python manage.py migrate

python manage.py loaddata first_member
python manage.py shell
from users.models import User
u = User.objects.get(pk=2)
u.set_password('admin')
u.save()

python manage.py loaddata initial


# Update requirements.txt
Ce fichier contient tout les modules pytohn nécessaires pour l'execution de borgia.
Celui-ci peut être mis à jour en théorie avec la commande suivante :

pip freeze -r devel-req.txt > stable-req.txt

Cependant, ceci ajoute TOUT les modules installés par pip. Donc également les éventuels modules ajoutés pour d'autres projet.

# Installer les modules avec le fichier requirements.txt

Pour installer les modules, il suffit d'effectuer la commande :

``pip install -r requirements.txt``


# Note pour Linux (et mac ??):

Python est installé par défaut avec deux version : 2 et 3. 2 étant la version par défaut.
Or Django (et donc Borgia) fonctionnent avec la version 3. Pour les difféfentes manip (notamment celle ci-dessus), il faut utiliser ``python3``. De même, il faudra utiliser ``pip3``


## Partie Graphique :

 - Le but initial était de réaliser un second template sombre, pour laisser le choix à l'utilisateur.
 Pour des raisons de maintenance, c'est plus simple de faire ça avec du LESS :
 Pour ajouter le LESS il faut :

 -- installer LESS (npm install -g less)
 -- install django-static-precompiler (avec pip)
 -- Ajouter static_precompiler aux INSTALLED_APP
 -- Ajouter {% load compile_static %}

 -- Migrer (``python manage.py makemigrations`` puis ``migrate``)

 - Puis j'ai ajouté une propriété en plus a User. Donc ne pas oublier makemigrations et migrate.

 - C'est un bordel monstre le dossier statique actuel, il faudrait rendre ça plus clair.
 Notamment bien gerer la distinction entre dirs et root (le dernier etant la version final, contenant les compilation).

 - Une fois ça épuré, réaliser le fichier less proprement dit. voir le lien :
 https://openclassrooms.com/courses/prenez-en-main-bootstrap/configurer-bootstrap

## Fonctionnement Graphique:

 Le nouveau fonctionnement est le suivant : on génère un fichier "bootstrap" modifié, en utilisant LESS :
 Les variables de bootstrap sont définies pour obtenir le template.
 Si-besoin, on ajoute un fichier de style en LESS (ici main). Cici nous permet de changer facilement de template.
 De plus ce fichier est moins volumineux, car on supprime les modules de bootstrap non-utilisés.

 Le sous-dossier less/less contient les fichiers originaux de bootstrap non-modifiés.

 Le fichier LESS est compilé dans static_dirs actuellement. __En prod, il faut changer le setting correspondant.__
