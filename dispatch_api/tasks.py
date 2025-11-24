from celery import shared_task
from dispatch_api.services import sendmail_service

@shared_task
def sendmail_task(data):
    return sendmail_service(data)

