import random
from faker import Faker

from users.models import User, get_list_year

faker = Faker('fr_FR')


def fake_User(fields=['username', 'password', 'first_name', 'last_name', 'email', 'surname', 'family', 'year', 'campus', 'phone', 'balance'], forced_fields={}):
    attributes = {}

    if 'username' in fields:
        attributes['username'] = faker.user_name()

    if 'password' in fields:
        attributes['password'] = faker.password()

    if 'first_name' in fields:
        attributes['first_name'] = faker.first_name()

    if 'last_name' in fields:
        attributes['last_name'] = faker.last_name()

    if 'email' in fields:
        attributes['email'] = faker.email()

    if 'surname' in fields:
        attributes['surname'] = faker.name()

    if 'family' in fields:
        attributes['family'] = '53'

    if 'year' in fields:
        attributes['year'] = random.randrange(2000, 2999)

    if 'campus' in fields:
        attributes['campus'] = 'ME'

    if 'phone' in fields:
        attributes['phone'] = faker.phone_number()

    if 'balance' in fields:
        attributes['balance'] = random.uniform(-1000, 1000)

    for key in forced_fields:
        attributes[key] = forced_fields[key]

    return User.objects.create(**attributes)
