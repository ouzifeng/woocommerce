from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'woocommerce_database.settings')

app = Celery('woocommerce_database')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Set Upstash Redis as the broker
app.conf.broker_url = settings.CELERY_BROKER_URL
