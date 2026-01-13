from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from checkout_api.models import Cart, CartItem, Order, OrderItem, Product
from checkout_api.serializers import CartSerializer
from decimal import *
from django.utils import timezone
from datetime import timedelta
from mail_dispatch_api.services import sendmail_service
import logging

logger = logging.getLogger(__name__)

def placeorder_service(data):
    try:
        # Will allow rolling back db changes if the service crashes
        with transaction.atomic(): 
            session_key = data['session_key']

            cart = Cart.objects.get(session_key=session_key)
            cartSerializer = CartSerializer(instance=cart, context={'request': None})
            cartItems = CartItem.objects.filter(cart__session_key=session_key)
            
            order = Order.objects.create(status=Order.PENDING, source_cart_session_key=session_key, total=cartSerializer.data['total'], subtotal=cartSerializer.data['subtotal'], tax_rate=Decimal('0.08'), contact_email=data['contact_email'], shipping_address_line1=data['shipping_address_line1'], shipping_city=data['shipping_city'], shipping_country=data['shipping_country'], shipping_zip=data['shipping_zip'])
            
            item_summary_list = []

            for item in cartItems:
                OrderItem.objects.create(order=order, original_product_id=item.product.pk, product_name=item.product.name, unit_price=item.product.price, quantity=item.quantity)

                item_summary_list.append(f"- {item.product.name} ({item.product.price} x{item.quantity})")

            cartItems.delete()

            cart.status = Cart.COMPLETED
            cart.save()

            items_string = "\n".join(item_summary_list)

            sendmail_service({
                'recipient': data['contact_email'],
                'subject': f'Order confirmed: {order.order_number}',
                'msg_content': (
                    f"Order processed successfully!\n\n"
                    f"Items Ordered:\n{items_string}\n\n"
                    f"Total: ${order.total}\n\n"
                    f"We'll contact you soon (keep your doors unlocked 😊)."
                )
            })
    except Exception as e:
        # exc_info is to trace the error
        try:
            cart.status = Cart.FAILED
            cart.save()
        except Exception as save_error:
            logger.error(f"Could not flip cart to FAILED: {save_error}")

        logger.error(f"Order failed for session {session_key}: {e}", exc_info=True)
        raise e

def cleanupcarts_service():
    abandoned_threshold = timezone.now() - timedelta(hours=48)
    completed_threshold = timezone.now() - timedelta(days=90)

    abandoned_carts = Cart.objects.filter(
        status__in=[Cart.ACTIVE, Cart.FAILED],
        updated_at__lt=abandoned_threshold
    )

    completed_carts = Cart.objects.filter(
        status__in=[Cart.COMPLETED],
        updated_at__lt=completed_threshold
    )

    count = abandoned_carts.count()
    abandoned_carts.delete()

    count = count + completed_carts.count()
    completed_carts.delete()

    return count

def seedproducts_service():
    products_data = [
        {"name": "Abstract Horizon", "price": 120.00, "stock": 5},
        {"name": "Midnight Jazz Preview", "price": 15.00, "stock": 100},
        {"name": "Golden Hour Canvas", "price": 250.00, "stock": 2},
        {"name": "Urban Echoes Audio", "price": 12.50, "stock": 50},
        {"name": "Neon Dreams", "price": 85.00, "stock": 10},
        {"name": "Sapphire Skies", "price": 300.00, "stock": 1},
        {"name": "Rhythm & Blues", "price": 20.00, "stock": 200},
        {"name": "Crimson Texture", "price": 145.00, "stock": 4},
        {"name": "Silent Forest", "price": 110.00, "stock": 7},
        {"name": "Electric Pulse", "price": 18.00, "stock": 75},
    ]

    for product in products_data:
        Product.objects.get_or_create(name=product['name'], price=product['price'], stock=product['stock'], is_active=True)



