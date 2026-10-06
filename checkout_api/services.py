from mail_dispatch_api.services import sendmail_service
from checkout_api.models import OrderItem, Order

def sendreciept_service(payment_intent_id):
    order = Order.objects.get(payment_intent_id=payment_intent_id)
    order.status = Order.PAID
    order.save()

    reciept = create_reciept(order.pk)
    msg_content = "Order Receipt\n"
    msg_content += "-----------------\n"

    for item in reciept['items']:
        msg_content += f"{item['title']} (x{item['quantity']}) - ${item['price']}\n"

    msg_content += "-----------------\n"
    msg_content += f"TOTAL: ${reciept['totals']}"

    email = {
        'msg_content': msg_content,
        'subject': 'Order paid for',
        'recipient': order.contact_email
    }

    sendmail_service(email)


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