from celery import shared_task
from checkout_api.services import placeorder_service

@shared_task
def placeorder_task(data):
    return placeorder_service(data)

