from __future__ import absolute_import

from .celery import app_schedule as celery_app

__all__ = ('celery_app',)