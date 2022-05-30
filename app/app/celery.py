from __future__ import absolute_import, unicode_literals
# Standard Library
import os
import kombu # type: ignore
from celery import Celery, bootsteps
from django.core.mail import send_mass_mail,send_mail
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')  # type: ignore

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# setting publisher
with app.pool.acquire(block=True) as conn:
    exchange = kombu.Exchange(
        name='email_exchange',
        type='direct',
        durable=True,
        channel=conn,
    )
    exchange.declare()

    queue = kombu.Queue(
        name='email_queue',
        exchange=exchange,
        routing_key='email_key',
        channel=conn,
        message_ttl=600,
        queue_arguments={
            'x-queue-type': 'classic'
        },
        durable=True
    )
    queue.declare()


# setting consumer
class MyConsumerStep(bootsteps.ConsumerStep):  # type: ignore

    def get_consumers(self, channel):
        return [kombu.Consumer(channel,
                               queues=[queue],
                               callbacks=[self.handle_message],
                               accept=['json'])]
    def handle_message(self, body, message):
        email=body.decode()
        if(email['type']=='single'):
            print('single')
            subject=email['data']["subject"]
            mess=email['data']["body"]
            from_email=email['data']["from"]
            toArr=email['data']["to"]
            send_mail(subject,mess,from_email,toArr)
            
        elif (email['type']=='bulk'):
            print('bulk')
            email_tuple=email['data']
            send_mass_mail((email_tuple), fail_silently=False)
        else:
            print('neither single nor bulk ')
        print('Received message: {0!r}'.format(body))
        message.ack()

app.steps['consumer'].add(MyConsumerStep)