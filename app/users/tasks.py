from celery import shared_task 

from django.core.mail import send_mass_mail,send_mail

@shared_task
def send_email_task(email_tuple):
    send_mass_mail((email_tuple), fail_silently=False)
    return None
        
@shared_task
def send_email_for_student(subject,message,fromMail,toArr):
    send_mail(subject,message,fromMail,toArr)
    return None
