from __future__ import absolute_import, unicode_literals

from celery import Celery, chain, current_app
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
#app = Celery('borgia', backend='rpc://', broker='pyamqp://')
app = current_app

@app.task
def scan_for_expired_users():
    for user in get_expired_users():
        deactivating_process = chain(deactivate_account.s(user), send_expiration_email.s())
        deactivating_process()



@app.task
def deactivate_account(user):
    # do some stuff
    print(f'deactivating account: {user}')
    return user + '_deactivated'


@app.task
def send_expiration_email(user):
    # do some other stuff
    print(f'sending expiration email to: {user}')
    return True

def get_expired_users():
    # Set up Django for models
    import django
    django.setup()
    from settings_data.models import Setting
    from users.models import User


    return (f'user_{i}' for i in range(5))


"""

from __future__ import absolute_import, unicode_literals

from celery import Celery, chain
from celery.schedules import crontab
#from settings_data.models import Setting

# set the default Django settings module for the 'celery' program.
app = Celery('borgia', backend='rpc://', broker='pyamqp://')

@app.task
def scan_for_expired_users():
    for user in get_expired_users():
        deactivating_process = chain(deactivate_account.s(user), send_expiration_email.s())
        deactivating_process()


@app.task
def deactivate_account(user):
    # do some stuff
    print(f'deactivating account: {user}')
    return user + '_deactivated'


@app.task
def send_expiration_email(user):
    # do some other stuff
    print(f'sending expiration email to: {user}')
    return True


def get_expired_users():
    return (f'user_{i}' for i in range(5))


"""
