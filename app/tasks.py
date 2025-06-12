from __future__ import absolute_import
from time import time
from celery import Celery
from celery.utils.log import get_task_logger
from celery import shared_task
from celery.schedules import crontab
from django.conf import settings
from django.core.mail import send_mail
from .models import Event
from datetime import date, datetime, timedelta
from django.utils import timezone
from celery.utils.log import get_logger
import pytz
logger = get_task_logger(__name__)

@shared_task

def send_mail_task():

    #print('Mail sending........')
    subject = "Hora de entrenar!"
    now = timezone.localtime()
    #problem timezone it has a delay of two hours. Checks if theres events in 30 min
    events = Event.objects.filter(start_time__range = (now + timedelta(minutes=150), now + timedelta(minutes=151)))
    print(now)
    message = 'Quedan menos de 30 minutos para que empiece tu rutina.'
    email_from = settings.EMAIL_HOST_USER

    #recipient_list = ['aaron.granja.l@gmail.com',]
  
    if(events != None):
        for event in events:
            recipient = [str(event.useremail)]
            send_mail(subject, message, email_from, recipient)
            return "Mail has been sent........"
    # else:
    #    return "Nothing found"