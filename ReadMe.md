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
