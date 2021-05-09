import random
from faker import Faker

from users.models import User, get_list_year

faker = Faker('fr_FR')


def fake_User():
    return User.objects.create(username=faker.user_name(),
                               password=faker.password(),
                               first_name=faker.first_name(),
                               last_name=faker.last_name(),
                               email=faker.email(),
                               surname=faker.name(),
                               family='53',
                               year=random.randrange(1900, 2500),
                               campus='ME',
                               phone=faker.phone_number(),
                               balance=random.uniform(-1000, 1000))
