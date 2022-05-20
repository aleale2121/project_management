# from celery import shared_task 
from __future__ import absolute_import, unicode_literals

from django.core.mail import send_mass_mail,send_mail


from celery import shared_task
from app.celery import app

@shared_task
def publish_message(message):
    with app.producer_pool.acquire(block=True) as producer:
        producer.publish(message,exchange='email_exchange',
                         routing_key='email_key',
                         retry=True,
                        retry_policy={
                            'interval_start': 0, # First retry immediately,
                            'interval_step': 2,  # then increase by 2s for every retry.
                            'interval_max': 30,  # but don't exceed 30s between retries.
                            'max_retries': 30,   # give up after 30 tries.
                        }
                         )

