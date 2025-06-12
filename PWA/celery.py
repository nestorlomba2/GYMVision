from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PWA.settings')
app_schedule = Celery('app')

app_schedule.config_from_object('django.conf:settings', namespace='CELERY')
app_schedule.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app_schedule.conf.beat_schedule = {
    'Send_mail_to_Client':{
        'task':'app.tasks.send_mail_task',
        'schedule': 60.0
    }

}
@app_schedule.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

