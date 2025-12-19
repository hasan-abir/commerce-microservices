from django.conf import settings
from django.core.mail import send_mail

def placeorder_service(data):
    session_key = data['session_key']

    return print(session_key)