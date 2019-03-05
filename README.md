![Borgia](.borgia/static/static_dirs/img/borgia-logo-light.png "Borgia")
==================================================================

Current Version : 5.0.2
Licence : [GNU GPL version 3](./license.txt)
Chat (en/fr): [Join us on Slack](https://borgia-app.slack.com)

Introduction
------------

Borgia is a software to help you manage your student association. With it, you
can sell products, organize events, keep track of your stocks, etc...
It will be your best ally to develop your possibilities for your student association.

To start
--------

* Install borgia dependencies : `pip install -r requirements/dev.txt` for development. Use prod.txt for production.
* Install LESS : `yarn global add less`.
* Update settings : `borgia/settings.py` need to be customized, depending on
your domains, Lydia account et mails.

Load initial data
-----------------

* Make migrations and load some pre-made content
  + `python manage.py makemigrations configurations users shops finances events modules sales stocks`,
  + `python manage.py migrate`,
  + `python manage.py loaddata initial`.
* In development, you can pre-populate the db with some pre-made objects :
  + `python manage.py loaddata tests_data`,
* Don't forget to change the passwords of users if you want to access them :
  + `python manage.py shell`,
  + `from users.models import User`,
  + `u = User.objects.get(pk=2)`,
  + `u.set_password('a_password')`.
  + `u.save()`
  + `exit()`

That's it !

Test
----

To run unit tests, run in a terminal : `python manage.py test`.
To run the unit tests only for a specific module, run : `python manage.py test nom_du_module`.

Documentation
-------------

Documentation are currently in writing-phase. Some ressources are available
[here](https://github.com/borgia-app/Borgia-docs).

Dependency
----------
Borgia base dependency :

* Django : Borgia run with the django framework
* django-bootstrap-form : To use bootstrap with django
* django-static-precompiler : For static files
* openpyxl : For excel manipulation
* Pillow : For users images

Developing and Contributing
---------------------------

We'd love to get contributions from you! For a quick guide to getting your
system setup for developing, take a look at the section "To Start".
Once you are up and running, take a look at the
[CONTRIBUTING.md](https://github.com/borgia-app/Borgia/CONTRIBUTING.md) to see
how to get your changes merged in.

End note (French)
--------------------

Borgia est un outil qui permet de construire, gérer et organiser votre vie
étudiante ! De la vente de produits à l'organisation d'évènements en passant
par la gestion de porte-monnaies virtuels, Borgia est votre meilleur allié pour
développer votre association d'étudiants.

L'équipe qui s'occupe de Borgia travaille tous les jours pour assurer un
logiciel de qualité. Nous sommes à l'écoute de vos remarques et nous essayons
d'améliorer Borgia de manière continue.

Borgia est actuellement utilisé par plusieurs milliers d'étudiants depuis plus
de 2 ans, notamment dans les centres [Arts et Métiers](https://artsetmetiers.fr/).
Nous cherchons activement des personnes pour participer à cette belle aventure,
n'hésite pas à nous contacter directement. Nous avons de grands projets pour Borgia
(une application mobile, de nouvelles fonctionnalités, ...) !

Enfin, si tu as une idée ou que tu as constaté un bug, n'hésite pas à ouvrir
une [issue](https://github.com/borgia-app/Borgia/issues) ou même un
[pull request](https://github.com/borgia-app/Borgia/pulls).
