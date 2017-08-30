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


## Partie Graphique :

 - Le but initial était de réaliser un second template sombre, pour laisser le choix à l'utilisateur.
 Pour des raisons de maintenance, c'est plus simple de faire ça avec du LESS :
 Pour ajouter le LESS il faut :
 
 -- installer LESS (npm install -g less)
 -- Ajouter static_precompiler aux INSTALLED_APP
 -- Ajouter {% load compile_static %}
 -- ??
 
 - Puis j'ai ajouté une propriété en plus a User. Donc ne pas oublier makemigrations et migrate.
 
 - C'est un bordel monstre le dossier statique actuel, il faudrait rendre ça plus clair. 
 Notamment bien gerer la distinction entre dirs et root (le dernier etant la version final, contenant les compilation).
 
 - Une fois ça épuré, réaliser le fichier less proprement dit. voir le lien : 
 https://openclassrooms.com/courses/prenez-en-main-bootstrap/configurer-bootstrap