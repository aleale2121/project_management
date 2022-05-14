
from django.core.mail import send_mail,send_mass_mail
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'
def sender(data):
    print("sender ",data)
    print("type of data ",type(data))
    print(data['subject'])
    
    try:
        send_mail(
            data['subject'],
            data['body'],
            data['from_email'],
            data['to_email'],
            fail_silently=False,
        )
    except Exception as e :
        print("Can not sent email, something wrong!",e)
