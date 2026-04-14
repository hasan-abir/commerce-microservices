from django.conf import settings
from django.core.mail import send_mail
from checkout_api.models import OrderItem

def sendreciept_service(order_pk):
    create_reciept(order_pk)

    return None

def create_reciept(order_pk):
    items = []
    total_amount = 0

    order_items = OrderItem.objects.filter(order=order_pk)

    for item in order_items:
        total_amount += item.price * item.quantity

        items.append({'title': item.title, 'quantity': item.quantity, 'price': item.price, 'total': item.price * item.quantity})

    return {
        'items': items,
        'totals': total_amount
    }