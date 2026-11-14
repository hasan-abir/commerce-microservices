from celery import shared_task
from checkout_api.services import sendreciept_service

@shared_task
def sendreciept_task(data1, data2):
    return sendreciept_service(data1, data2)


