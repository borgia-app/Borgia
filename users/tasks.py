from __future__ import absolute_import, unicode_literals
from celery import Celery, chain, current_app
from celery.schedules import crontab
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.core.exceptions import ObjectDoesNotExist

# set the default Django settings module for the 'celery' program.
app = current_app

@app.task
def scan_mailing_balance_alert():
    for user in get_concerned_users_balance_mailing_alert():
        mailing_process = chain(mail_alert_balance.s(user))
        mailing_process()
    return True

@app.task
def mail_alert_balance(user):
    """
    Send an email to alert about low balance.
    """
    from settings_data.models import Setting

    threshold = Setting.objects.get(name="BALANCE_THRESHOLD_MAIL_ALERT").get_value()

    msg_plain = render_to_string('users/mail_alert_balance.txt', {})
    msg_html = render_to_string('users/mail_alert_balance.html', {})

    send_mail(
        'email title',
        msg_plain,
        'ae.ensam.assoc@gmail.com',
        [user.email],
        html_message=msg_html,
    )
    print(f'mailing alert balance: {user.__str__()}')

def get_concerned_users_balance_mailing_alert():
    """
    Return users concerned by the mailing alert concerning the balance.
    Threshold & frequency must be defined for filtering.

    :returns: [] if threshold or frequency is None or if both settings aren't defined.
    :returns: [Users]
    """
    # Set up Django for models
    import django
    django.setup()
    from settings_data.models import Setting
    from users.models import User
    from django.contrib.auth.models import Group

    try:
        threshold = Setting.objects.get(name="BALANCE_THRESHOLD_MAIL_ALERT").get_value()
        frequency = Setting.objects.get(name="BALANCE_FREQUENCY_MAIL_ALERT").get_value()

        if threshold is not None and frequency is not None:
            return User.objects.filter(balance__lt=threshold, is_active=True).exclude(
                groups=Group.objects.get(name='specials'))
        else:
            return []
    except ObjectDoesNotExist:
        return []


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
