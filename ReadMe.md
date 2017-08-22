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
