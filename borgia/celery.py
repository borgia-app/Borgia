from __future__ import absolute_import, unicode_literals

import os
from celery import Celery, chain
from celery.schedules import crontab
from users.tasks import scan_mailing_balance_alert

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borgia.settings')
"""import django
from django.conf import settings
settings.configure()
django.setup()"""

# set the default Django settings module for the 'celery' program.
app = Celery('borgia', backend='rpc://', broker='pyamqp://')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Console log
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        5,
        scan_mailing_balance_alert.s(),
        name='Alert mailing'
    )
